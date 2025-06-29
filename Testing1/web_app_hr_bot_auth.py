#!/usr/bin/env python3
"""
HR Document Q&A System with Google OAuth Authentication
Features:
- Google OAuth login using Flask-Dance
- Session-based document management
- User-specific document storage
- HR bot persona with structured responses
- PDF and text file support
- Link following and PDF link extraction
"""

import os
import json
import re
import requests
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta, timezone
import PyPDF2
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.utils import secure_filename
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import numpy as np
from urllib.parse import urlparse
import hashlib
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from werkzeug.middleware.proxy_fix import ProxyFix
import random
import smtplib
from email.mime.text import MIMEText

# Import configuration
try:
    from config import (
        GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY, GEMINI_API_KEY,
        EMAIL_CONFIG, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM, 
        EMAIL_FROM_NAME, EMAIL_ENABLED, EMAIL_PROVIDER, EMAIL_TIMEOUT, EMAIL_MAX_RETRIES
    )
except ImportError:
    # Fallback to environment variables
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your-client-id-here")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your-client-secret-here")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    EMAIL_CONFIG = {
        'smtp_server': os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
        'smtp_port': int(os.getenv("EMAIL_SMTP_PORT", "587")),
        'use_tls': True,
        'use_ssl': False
    }
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "your-email@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-app-password")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "your-email@gmail.com")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "HR Document Q&A System")
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "gmail").lower()
    EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))
    EMAIL_MAX_RETRIES = int(os.getenv("EMAIL_MAX_RETRIES", "3"))

# Configuration - Remove hardcoded client ID, use from config/env
# GOOGLE_CLIENT_ID = "710501982331-qr11u9rnbfk8p8kd5skkbbvvrs7vg6em.apps.googleusercontent.com"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Debug: Print configuration (without sensitive values)
print(f"🔧 OAuth Configuration:")
print(f"   Client ID: {GOOGLE_CLIENT_ID[:10]}..." if GOOGLE_CLIENT_ID and len(GOOGLE_CLIENT_ID) > 10 else f"   Client ID: {GOOGLE_CLIENT_ID}")
print(f"   Client Secret: {'*' * 10}..." if GOOGLE_CLIENT_SECRET else "   Client Secret: Not set")
print(f"   Gemini API Key: {'*' * 10}..." if GEMINI_API_KEY else "   Gemini API Key: Not set")
print(f"   Flask Secret Key: {'*' * 10}..." if SECRET_KEY else "   Flask Secret Key: Not set")

# Configure OAuth - only allow insecure transport for local development
if os.getenv('FLASK_ENV') == 'development' or 'localhost' in os.getenv('HOSTNAME', ''):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    print("🔧 Development mode: Allowing insecure transport for OAuth")

# Configure Google OAuth with explicit redirect URI
google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="index"  # Redirect to index route after login
)
app.register_blueprint(google_bp, url_prefix="/login")

# Global variables for document storage (in production, use a database)
user_documents = {}  # {user_email: {documents: [], chunks: [], embeddings: []}}
user_fetched_urls = {}  # {user_email: {url: content}}

# In-memory OTP store: {email: (otp, expiry_datetime)}
otp_store = {}

class HRDocumentQA:
    def __init__(self):
        """Initialize the HR Document Q&A system"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ HR Document Q&A system initialized successfully")
    
    def add_document_from_file(self, file_path: str, title: Optional[str] = None, max_depth: int = 2, user_email: str = None):
        """Add a document from a file with link processing, including PDF hyperlinks"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine title
        if title is None:
            title = os.path.basename(file_path)
        
        # Read file content and extract URLs
        try:
            extra_urls = set()
            if file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    
                    # Extract text content
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                    
                    # Extract URLs from PDF annotations (clickable links)
                    for page in pdf_reader.pages:
                        if '/Annots' in page:
                            for annot in page['/Annots']:
                                if annot.get_object()['/Subtype'] == '/Link':
                                    if '/A' in annot.get_object():
                                        action = annot.get_object()['/A']
                                        if '/URI' in action:
                                            url = action['/URI']
                                            if url.startswith('http'):
                                                extra_urls.add(url)
                                                print(f"🔗 Adding Benefits and Perks URL: {url}")
            
            else:
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            
            # Extract URLs from content
            urls = set(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content))
            urls.update(extra_urls)
            
            if urls:
                print(f"🔍 Found {len(urls)} URLs in document: {title}")
                
                # Fetch content from URLs
                fetched_content = ""
                for url in urls:
                    try:
                        print(f"🔗 Fetching URL (attempt 1): {url}")
                        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                        response.raise_for_status()
                        
                        # Extract text content (basic extraction)
                        text_content = response.text
                        # Remove HTML tags and get first 10000 characters
                        text_content = re.sub(r'<[^>]+>', '', text_content)
                        text_content = text_content[:10000]
                        
                        fetched_content += f"\n\n--- Content from {url} ---\n{text_content}\n"
                        print(f"✅ Successfully fetched content from: {url} ({len(text_content)} characters)")
                        
                        # Store fetched URLs for user
                        if user_email:
                            if user_email not in user_fetched_urls:
                                user_fetched_urls[user_email] = {}
                            user_fetched_urls[user_email][url] = text_content
                        
                    except Exception as e:
                        print(f"❌ Failed to fetch {url}: {e}")
                
                # Append fetched content to original content
                content += fetched_content
                print(f"📄 Enhanced document '{title}' with content from {len(urls)} links")
            
            # Add document to user's collection
            if user_email:
                if user_email not in user_documents:
                    user_documents[user_email] = {"documents": [], "chunks": [], "embeddings": []}
                
                # Add document
                user_documents[user_email]["documents"].append({
                    "title": title,
                    "content": content,
                    "content_length": len(content)
                })
                
                # Create chunks and embeddings
                self._create_chunks_and_embeddings(content, title, user_email)
                
                print(f"📄 Uploaded document: {title}")
                print(f"📊 Content length: {len(content)} characters")
                print(f"📚 Total documents in system: {len(user_documents[user_email]['documents'])}")
                print(f"🔍 Total chunks in system: {len(user_documents[user_email]['chunks'])}")
                
                return {
                    "title": title,
                    "content_length": len(content),
                    "urls_found": len(urls)
                }
            
        except Exception as e:
            print(f"❌ Error processing document {file_path}: {e}")
            raise
    
    def _create_chunks_and_embeddings(self, content: str, title: str, user_email: str):
        """Create chunks and embeddings for the content"""
        # Split content into chunks (simple splitting by paragraphs)
        paragraphs = content.split('\n\n')
        chunks = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                chunk = {
                    "content": paragraph.strip(),
                    "source": title,
                    "chunk_id": i
                }
                chunks.append(chunk)
        
        # Create embeddings
        chunk_texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(chunk_texts)
        
        # Store chunks and embeddings
        user_documents[user_email]["chunks"].extend(chunks)
        if "embeddings" not in user_documents[user_email]:
            user_documents[user_email]["embeddings"] = []
        user_documents[user_email]["embeddings"].extend(embeddings.tolist())
    
    def _find_relevant_chunks(self, question: str, user_email: str, top_k: int = 5) -> List[Dict]:
        """Find the most relevant chunks for a question using semantic search"""
        if user_email not in user_documents or not user_documents[user_email]["chunks"]:
            return []
        
        # Encode the question
        question_embedding = self.embedding_model.encode([question])
        
        # Calculate similarities
        embeddings = np.array(user_documents[user_email]["embeddings"])
        similarities = np.dot(embeddings, question_embedding.T).flatten()
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_chunks = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                relevant_chunks.append(user_documents[user_email]["chunks"][idx])
        
        return relevant_chunks
    
    def ask_question(self, question: str, user_email: str, user_name: str = None) -> str:
        """Ask a question and get answer as an HR bot with compassion and empathy"""
        # Use user name if provided, otherwise use email prefix
        if not user_name:
            user_name = user_email.split('@')[0]
        
        # Extract first name only (split by space and take first part)
        first_name = user_name.split()[0] if ' ' in user_name else user_name
        
        # Check if this is a greeting or general conversation
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
        question_lower = question.lower().strip()
        
        # Handle greetings and general conversation
        if any(keyword in question_lower for keyword in greeting_keywords):
            return f"""**Hello {first_name}! 👋 I'm your HR Assistant**

I'm here to help you with any questions about company policies, employee benefits, workplace guidelines, or any other HR-related matters. I have access to your company documents and I'm ready to provide you with accurate, helpful information.

**How can I assist you today?** Some common topics I can help with:
• Work hours and schedules
• Leave policies and time off
• Employee benefits and perks
• Expense reimbursement
• Dress code and workplace policies
• Confidentiality and company policies

Feel free to ask me anything! 🤝"""
        
        # Find relevant chunks
        relevant_chunks = self._find_relevant_chunks(question, user_email)
        
        if not relevant_chunks:
            return f"""**I understand your question, {first_name}, but I don't have specific information about that in the available documents.**

**What I can help you with:**
Based on the documents I have access to, I can provide information about:
• Work hours and flexible arrangements
• Leave policies (vacation, sick leave, personal days)
• Dress code requirements
• Expense reimbursement procedures
• Confidentiality policies

**Next Steps:**
1. **Check if your question relates to the topics above**
2. **Ask about a specific policy area** I can help with
3. **Upload additional documents** if you need information about other topics

**Need help?** Feel free to ask me about any of the policy areas I mentioned, or let me know if you'd like to upload additional company documents! 📋"""
        
        # Build context from relevant chunks
        context = "\n\n".join([f"[From: {chunk['source']}]\n{chunk['content']}" for chunk in relevant_chunks])
        
        # Create HR bot prompt
        hr_prompt = f"""You are a professional, empathetic HR Assistant. You have access to company documents and should provide helpful, accurate information based ONLY on the provided document content.

**Document Context:**
{context}

**Employee Question:** {question}

**Instructions:**
1. **Address the employee by first name** ({first_name}) in a warm, professional manner
2. **Provide a clear, structured answer** with bullet points and numbered lists where appropriate
3. **Use ONLY information from the provided documents** - do not make up or assume information
4. **Be specific and actionable** - provide concrete details when available
5. **End with a supportive message** and offer to help with follow-up questions
6. **Keep the tone conversational and natural** - avoid formal business letter formatting

**Response Format:**
- Use **bold headers** for sections
- Use bullet points (•) for lists
- Use numbered lists (1., 2., 3.) for procedures
- Be warm and professional
- If information is not available, clearly state that and suggest what IS available
- **Do NOT use formal subject lines or "Dear [Name]" formatting**

**Remember:** You are an HR professional helping an employee named {first_name}. Be supportive, accurate, and professional while maintaining a conversational tone."""
        
        try:
            # Generate response
            response = self.model.generate_content(hr_prompt)
            return response.text
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"""**I apologize, {first_name}, but I encountered an error while processing your question.**

**What happened:** There was a technical issue with generating your response.

**What you can do:**
1. **Try asking your question again** - sometimes this resolves the issue
2. **Rephrase your question** - be more specific about what you need
3. **Check if your question relates to:** work hours, leave policies, dress code, expenses, or confidentiality

**I'm here to help!** Please try again, and I'll do my best to assist you with your HR-related questions. 🤝"""

# Initialize the HR Q&A system
try:
    hr_qa = HRDocumentQA()
    print("✅ HR Document Q&A system initialized successfully")
except Exception as e:
    print(f"❌ Error initializing HR Q&A system: {e}")
    hr_qa = None

def login_required(f):
    """Decorator to require login for certain routes"""
    def decorated_function(*args, **kwargs):
        # Check for email OTP authentication first
        if session.get('logged_in') and session.get('user_email'):
            return f(*args, **kwargs)
        
        # Check for Google OAuth authentication
        if google.authorized:
            return f(*args, **kwargs)
        
        # If neither is authenticated, redirect to login
        return redirect(url_for('login'))
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Main page - redirect to login if not authenticated"""
    # Check for email OTP authentication first
    if session.get('logged_in') and session.get('user_email'):
        user_email = session.get('user_email')
        user_name = session.get('user_name', user_email.split('@')[0])
        # Initialize user document storage if not exists
        if user_email not in user_documents:
            user_documents[user_email] = {"documents": [], "chunks": [], "embeddings": []}
        return render_template('index.html', user_email=user_email, user_name=user_name)
    
    # Check for Google OAuth authentication
    if not google.authorized:
        return render_template('login.html', logged_in=False)
    
    try:
        # Get user info
        resp = google.get('/oauth2/v2/userinfo')
    except TokenExpiredError:
        print("🔄 OAuth token expired, clearing session and redirecting to login")
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        print(f"❌ OAuth error: {e}")
        session.clear()
        return redirect(url_for('login'))
    
    if resp.ok:
        user_info = resp.json()
        user_email = user_info['email']
        full_name = user_info.get('name', user_email.split('@')[0])  # Use name or email prefix
        first_name = full_name.split()[0] if ' ' in full_name else full_name  # Extract first name only
        session['user_email'] = user_email
        session['user_name'] = first_name  # Store first name in session
        # Initialize user document storage if not exists
        if user_email not in user_documents:
            user_documents[user_email] = {"documents": [], "chunks": [], "embeddings": []}
        return render_template('index.html', user_email=user_email, user_name=first_name)
    else:
        print(f"❌ OAuth response not OK: {resp.status_code} - {resp.text}")
        session.clear()
        return redirect(url_for('login'))

@app.route('/login')
def login():
    """Explicit login page route for Google OAuth and Email OTP"""
    # Check for email OTP authentication first
    if session.get('logged_in') and session.get('user_email'):
        user_email = session.get('user_email')
        user_name = session.get('user_name', user_email.split('@')[0])
        return render_template('login.html', logged_in=True, user_email=user_email, user_name=user_name)
    
    # Check for Google OAuth authentication
    if not google.authorized:
        return render_template('login.html', logged_in=False)
    
    try:
        resp = google.get('/oauth2/v2/userinfo')
    except TokenExpiredError:
        print("🔄 OAuth token expired, clearing session and redirecting to login")
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        print(f"❌ OAuth error: {e}")
        session.clear()
        return redirect(url_for('login'))
    
    if resp.ok:
        user_info = resp.json()
        user_email = user_info['email']
        full_name = user_info.get('name', user_email.split('@')[0])
        first_name = full_name.split()[0] if ' ' in full_name else full_name  # Extract first name only
        session['user_email'] = user_email
        session['user_name'] = first_name  # Store first name in session
        return render_template('login.html', logged_in=True, user_email=user_email, user_name=first_name)
    else:
        print(f"❌ OAuth response not OK: {resp.status_code} - {resp.text}")
        session.clear()
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/api/documents')
@login_required
def get_documents():
    """Get documents for the current user"""
    user_email = session.get('user_email')
    if user_email and user_email in user_documents:
        documents = user_documents[user_email]["documents"]
        return jsonify({
            "documents": [
                {
                    "title": doc["title"],
                    "content_length": doc["content_length"],
                    "chunks": len([c for c in user_documents[user_email]["chunks"] if c["source"] == doc["title"]])
                }
                for doc in documents
            ]
        })
    return jsonify({"documents": []})

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload a document for the current user"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({"error": "User not authenticated"}), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_path = f"temp_{filename}"
        file.save(temp_path)
        
        # Process document
        result = hr_qa.add_document_from_file(temp_path, filename, user_email=user_email)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            "message": f"Added document: {filename} ({result['content_length']} characters, {result['urls_found']} URLs found)",
            "documents": [
                {
                    "title": doc["title"],
                    "content_length": doc["content_length"],
                    "chunks": len([c for c in user_documents[user_email]["chunks"] if c["source"] == doc["title"]])
                }
                for doc in user_documents[user_email]["documents"]
            ]
        })
    
    except Exception as e:
        return jsonify({"error": f"Error processing document: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat requests for the current user"""
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    if not user_email:
        return jsonify({"error": "User not authenticated"}), 401
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    question = data['message']
    print(f"💬 Employee Question: {question}")
    
    if user_email in user_documents:
        print(f"📚 Documents available: {len(user_documents[user_email]['documents'])}")
        print(f"🔍 Chunks available: {len(user_documents[user_email]['chunks'])}")
    
    try:
        response = hr_qa.ask_question(question, user_email, user_name)
        return jsonify({
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return jsonify({
            "response": "I apologize, but I encountered an error while processing your question. Please try again.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/fetched-urls')
@login_required
def get_fetched_urls():
    """Get fetched URLs for the current user"""
    user_email = session.get('user_email')
    if user_email and user_email in user_fetched_urls:
        urls_info = {}
        for url, content in user_fetched_urls[user_email].items():
            urls_info[url] = f"{len(content)} characters"
        return jsonify({"fetched_urls": urls_info})
    return jsonify({"fetched_urls": {}})

@app.route('/api/remove-document', methods=['POST'])
@login_required
def remove_document():
    """Remove a document for the current user"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({"error": "User not authenticated"}), 401
    
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "No document title provided"}), 400
    
    title = data['title']
    
    if user_email in user_documents:
        # Remove document
        user_documents[user_email]["documents"] = [
            doc for doc in user_documents[user_email]["documents"] 
            if doc["title"] != title
        ]
        
        # Remove associated chunks and embeddings
        chunks_to_keep = []
        embeddings_to_keep = []
        
        for i, chunk in enumerate(user_documents[user_email]["chunks"]):
            if chunk["source"] != title:
                chunks_to_keep.append(chunk)
                embeddings_to_keep.append(user_documents[user_email]["embeddings"][i])
        
        user_documents[user_email]["chunks"] = chunks_to_keep
        user_documents[user_email]["embeddings"] = embeddings_to_keep
        
        return jsonify({
            "message": f"Removed document: {title}",
            "documents": [
                {
                    "title": doc["title"],
                    "content_length": doc["content_length"],
                    "chunks": len([c for c in user_documents[user_email]["chunks"] if c["source"] == doc["title"]])
                }
                for doc in user_documents[user_email]["documents"]
            ]
        })
    
    return jsonify({"error": "No documents found"}), 404

# Helper: send OTP email with real SMTP support
def send_otp_email(recipient, otp):
    if EMAIL_ENABLED:
        try:
            # Create email message with better formatting
            email_body = f"""
Hello!

Your OTP (One-Time Password) for HR Document Q&A System login is:

🔐 **{otp}**

This code will expire in 2 minutes.

If you didn't request this code, please ignore this email.

Best regards,
{EMAIL_FROM_NAME}
            """
            
            msg = MIMEText(email_body, 'plain', 'utf-8')
            msg['Subject'] = f'Your Login OTP - {EMAIL_FROM_NAME}'
            msg['From'] = f'{EMAIL_FROM_NAME} <{EMAIL_FROM}>'
            msg['To'] = recipient
            
            # Get email configuration
            smtp_server = EMAIL_CONFIG['smtp_server']
            smtp_port = EMAIL_CONFIG['smtp_port']
            use_tls = EMAIL_CONFIG['use_tls']
            use_ssl = EMAIL_CONFIG['use_ssl']
            
            print(f"📧 Attempting to send email via {EMAIL_PROVIDER} ({smtp_server}:{smtp_port})")
            
            # Send email with retry logic
            for attempt in range(EMAIL_MAX_RETRIES):
                try:
                    if use_ssl:
                        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=EMAIL_TIMEOUT)
                    else:
                        server = smtplib.SMTP(smtp_server, smtp_port, timeout=EMAIL_TIMEOUT)
                    
                    if use_tls:
                        server.starttls()
                    
                    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    
                    print(f"✅ OTP email sent successfully to {recipient} (attempt {attempt + 1})")
                    return True
                    
                except smtplib.SMTPAuthenticationError as e:
                    print(f"❌ Authentication failed for {EMAIL_PROVIDER}: {e}")
                    if attempt == EMAIL_MAX_RETRIES - 1:
                        raise
                except smtplib.SMTPException as e:
                    print(f"❌ SMTP error (attempt {attempt + 1}): {e}")
                    if attempt == EMAIL_MAX_RETRIES - 1:
                        raise
                except Exception as e:
                    print(f"❌ Connection error (attempt {attempt + 1}): {e}")
                    if attempt == EMAIL_MAX_RETRIES - 1:
                        raise
                
                if attempt < EMAIL_MAX_RETRIES - 1:
                    print(f"🔄 Retrying in 2 seconds... (attempt {attempt + 2}/{EMAIL_MAX_RETRIES})")
                    import time
                    time.sleep(2)
            
        except Exception as e:
            print(f"❌ Failed to send OTP email to {recipient}: {e}")
            print(f"📧 Falling back to console output")
            # Fall back to console output
            print(f"[OTP DEMO] Sending OTP {otp} to {recipient}")
            return False
    else:
        # Demo mode: print OTP to console
        print(f"[OTP DEMO] Sending OTP {otp} to {recipient}")
        print(f"📧 To enable real email sending:")
        print(f"   1. Set EMAIL_ENABLED=true in your .env file")
        print(f"   2. Configure EMAIL_USERNAME and EMAIL_PASSWORD")
        print(f"   3. Set EMAIL_PROVIDER (gmail, outlook, yahoo, or custom)")
        return False

@app.route('/login/email', methods=['GET', 'POST'])
def email_login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email.', 'danger')
            return render_template('login.html', logged_in=False)
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expiry = datetime.now(timezone.utc) + timedelta(minutes=2)
        otp_store[email] = (otp, expiry)
        
        # Send OTP
        email_sent = send_otp_email(email, otp)
        
        if EMAIL_ENABLED:
            if email_sent:
                flash('OTP sent to your email successfully!', 'success')
            else:
                flash('Failed to send email. Please check console for OTP or try again.', 'warning')
        else:
            flash('OTP sent to your email (check console in demo mode).', 'info')
        
        return render_template('login.html', logged_in=False, otp_sent=True, email=email)
    return render_template('login.html', logged_in=False)

@app.route('/login/email/verify', methods=['POST'])
def email_verify():
    email = request.form.get('email')
    otp = request.form.get('otp')
    if not email or not otp:
        flash('Missing email or OTP.', 'danger')
        return render_template('login.html', logged_in=False)
    stored = otp_store.get(email)
    if not stored:
        flash('No OTP found for this email. Please request a new one.', 'danger')
        return render_template('login.html', logged_in=False)
    real_otp, expiry = stored
    if datetime.now(timezone.utc) > expiry:
        flash('OTP expired. Please request a new one.', 'danger')
        del otp_store[email]
        return render_template('login.html', logged_in=False)
    if otp != real_otp:
        flash('Invalid OTP. Please try again.', 'danger')
        return render_template('login.html', logged_in=False, otp_sent=True, email=email)
    # OTP correct: log in user
    session['user_email'] = email
    session['logged_in'] = True
    del otp_store[email]
    flash('Logged in successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    if hr_qa is None:
        print("❌ Failed to start server. Please check your configuration.")
    else:
        print("🚀 Starting HR Document Q&A Web Server with Google Authentication...")
        print("📚 Loaded documents: 0")
        print("🌐 Open your browser and go to: http://localhost:8080")
        app.run(host='0.0.0.0', port=8080, debug=True) 