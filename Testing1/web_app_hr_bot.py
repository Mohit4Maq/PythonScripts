#!/usr/bin/env python3
"""
Flask Web Application for Document-Based Q&A with Google Gemini
Provides a beautiful chat interface for querying documents with link-following capability
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from typing import List, Optional, Dict, Set
from dotenv import load_dotenv
import json
from datetime import datetime
import PyPDF2
import io
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

class HRDocumentQASystem:
    def __init__(self):
        """Initialize the HR Document Q&A System"""
        self.documents = []
        self.document_chunks = []
        self.fetched_urls = {}
        
        # Initialize Gemini API
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.gemini_api_key)
        self.genai = genai.GenerativeModel('gemini-pro')
        
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chunk_size = 1000
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
    def _extract_urls_from_text(self, text: str) -> Set[str]:
        """Extract URLs from text content"""
        urls = set()
        matches = self.url_pattern.findall(text)
        for url in matches:
            # Clean up URL (remove trailing punctuation)
            clean_url = url.rstrip('.,;:!?')
            if clean_url:
                urls.add(clean_url)
        return urls
    
    def _fetch_url_content(self, url: str, max_retries: int = 3) -> Optional[str]:
        """Fetch content from a URL with retry logic"""
        if url in self.fetched_urls:
            return self.fetched_urls[url]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for attempt in range(max_retries):
            try:
                print(f"🔗 Fetching URL (attempt {attempt + 1}): {url}")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit content length to avoid overwhelming the LLM
                if len(text) > 10000:
                    text = text[:10000] + "... [Content truncated]"
                
                self.fetched_urls[url] = text
                print(f"✅ Successfully fetched content from: {url} ({len(text)} characters)")
                return text
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to fetch {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"❌ Failed to fetch {url} after {max_retries} attempts")
                    return None
            except Exception as e:
                print(f"❌ Unexpected error fetching {url}: {e}")
                return None
        
        return None
    
    def _process_document_links(self, content: str, title: str, max_depth: int = 2) -> str:
        """Process document content and fetch linked content up to specified depth"""
        print(f"🔍 Found {len(self._extract_urls_from_text(content))} URLs in document: {title}")
        
        # Extract URLs from the main document
        urls = self._extract_urls_from_text(content)
        
        # Process URLs at depth 1
        enhanced_content = content
        for url in urls:
            if url not in self.fetched_urls:
                fetched_content = self._fetch_url_content(url)
                if fetched_content:
                    self.fetched_urls[url] = fetched_content
                    enhanced_content += f"\n\n[Content from {url}]:\n{fetched_content}"
        
        # If we have depth > 1, process links from fetched content (depth 2)
        if max_depth > 1 and self.fetched_urls:
            for url, fetched_content in self.fetched_urls.items():
                # Extract URLs from the fetched content
                nested_urls = self._extract_urls_from_text(fetched_content)
                
                # Only process new URLs that we haven't fetched yet
                for nested_url in nested_urls:
                    if nested_url not in self.fetched_urls and nested_url not in urls:
                        print(f"🔗 Fetching nested URL (depth 2): {nested_url}")
                        nested_content = self._fetch_url_content(nested_url)
                        if nested_content:
                            self.fetched_urls[nested_url] = nested_content
                            enhanced_content += f"\n\n[Content from {nested_url} (depth 2)]:\n{nested_content}"
        
        return enhanced_content
        
    def add_document(self, content: str, title: str = "Document", max_depth: int = 2):
        """Add a document to the system with link processing"""
        # Process links in the document
        enhanced_content = self._process_document_links(content, title, max_depth)
        
        # Chunk the enhanced content
        chunks = self._chunk_text(enhanced_content)
        
        # Store the document
        self.documents.append({
            "title": title,
            "content": enhanced_content,
            "chunks": chunks
        })
        
        # Add chunks to the searchable list
        for chunk in chunks:
            self.document_chunks.append((chunk, title))
        
        print(f"📄 Uploaded document: {title}")
        print(f"📊 Content length: {len(enhanced_content)} characters")
        print(f"📚 Total documents in system: {len(self.documents)}")
        print(f"🔍 Total chunks in system: {len(self.document_chunks)}")
    
    def _extract_urls_from_pdf_annotations(self, pdf_reader) -> set:
        """Extract URLs from PDF annotations (clickable hyperlinks)"""
        urls = set()
        for page in pdf_reader.pages:
            if '/Annots' in page:
                for annot in page['/Annots']:
                    annot_obj = annot.get_object()
                    if '/A' in annot_obj and '/URI' in annot_obj['/A']:
                        url = annot_obj['/A']['/URI']
                        if url:
                            urls.add(str(url))
        return urls

    def add_document_from_file(self, file_path: str, title: Optional[str] = None, max_depth: int = 2):
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
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
                    # Extract URLs from PDF annotations (clickable links)
                    extra_urls = self._extract_urls_from_pdf_annotations(pdf_reader)
                    print(f"🔍 Found {len(extra_urls)} URLs in PDF annotations: {extra_urls}")
            else:
                # Try UTF-8 first, then other encodings
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
        
        # If we found extra URLs in PDF annotations, process them separately
        if extra_urls:
            print(f"🔗 Processing {len(extra_urls)} URLs from PDF annotations")
            for url in extra_urls:
                if url not in content:
                    # Fetch content from the URL
                    fetched_content = self._fetch_url_content(url)
                    if fetched_content:
                        print(f"✅ Successfully fetched content from PDF link: {url} ({len(fetched_content)} characters)")
                        # Add the fetched content to our document
                        content += f"\n\n[Content from {url}]:\n{fetched_content}"
                    else:
                        print(f"❌ Failed to fetch content from PDF link: {url}")
        
        # Add document with link processing
        self.add_document(content, title, max_depth)
        return f"Added document: {title} ({len(content)} characters)"
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for better retrieval"""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]
            if i + self.chunk_size < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > self.chunk_size * 0.7:
                    chunk = chunk[:break_point + 1]
            chunks.append(chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _find_relevant_chunks(self, query: str, top_k: int = 5) -> List[str]:
        """Find the most relevant document chunks for a query"""
        query_words = set(query.lower().split())
        chunk_scores = []
        
        for chunk, title in self.document_chunks:
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            score = overlap / max(len(query_words), 1)
            chunk_scores.append((score, chunk, title))
        
        chunk_scores.sort(key=lambda x: x[0], reverse=True)
        relevant_chunks = []
        
        for score, chunk, title in chunk_scores[:top_k]:
            if score > 0:
                relevant_chunks.append(f"[From: {title}]\n{chunk}")
        
        return relevant_chunks
    
    def ask_question(self, question: str) -> str:
        """Ask a question and get answer as an HR bot with compassion and empathy"""
        # Check if this is a greeting or general conversation
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
        question_lower = question.lower().strip()
        
        # Handle greetings and general conversation
        if any(keyword in question_lower for keyword in greeting_keywords):
            return """**Hello! 👋 I'm your HR Assistant**

I'm here to help you with any questions about company policies, employee benefits, workplace guidelines, or any other HR-related matters. I have access to your company documents and I'm ready to provide you with compassionate, empathetic support.

**How can I assist you today?** I can help with:
• **Company Policies** - Work hours, dress code, leave policies
• **Employee Benefits** - Health insurance, vacation time, perks
• **Workplace Guidelines** - Professional conduct, safety protocols
• **General HR Questions** - Any concerns you might have

Please feel free to ask me anything - I'm here to support you! 🤝"""
        
        # Special handling for new employee questions
        new_employee_keywords = ['new employee', 'new hire', 'just started', 'first day', 'onboarding', 'critical details', 'important information']
        if any(keyword in question_lower for keyword in new_employee_keywords):
            return """**Welcome! 🎉** Here are the key policies from our documents:

**📅 Work Hours:** 9:00 AM to 5:00 PM, Monday-Friday
**🏖️ Vacation:** 20 days per year
**👔 Dress Code:** Business casual (Mon-Thu), Casual Friday
**💰 Expenses:** Submit within 30 days, receipts for $25+
**🔒 Confidentiality:** All company info is confidential

**Need anything specific?** I'm here to help! 💙"""
        
        if not self.documents:
            return """**Hello! 👋 I'm your HR Assistant**

I don't have any company documents loaded yet, but I'm here to help you with any HR-related questions or concerns you might have. 

**What would you like to know about?** I can assist with general HR topics, workplace guidance, or help you understand what kind of information would be useful to have available.

Please feel free to ask me anything - I'm here to support you with compassion and understanding! 🤝"""
        
        relevant_chunks = self._find_relevant_chunks(question)
        
        # DEBUG: Print the relevant chunks/context being sent to the LLM
        print("\n===== DEBUG: Relevant Chunks for Question =====")
        print(f"Question: {question}")
        for i, chunk in enumerate(relevant_chunks):
            print(f"--- Chunk {i+1} ---\n{chunk}\n")
        print("===== END DEBUG =====\n")
        
        if not relevant_chunks:
            return """**I understand your question, and I want to help! 🤝**

I couldn't find specific information about that in the company documents I have access to. However, I'm here to support you and can help in several ways:

**What I can do:**
• Help you rephrase your question to find relevant information
• Guide you to the right department or person for your specific needs
• Provide general HR guidance and support
• Listen to your concerns with empathy and understanding

**Please let me know:**
• Would you like to rephrase your question?
• Is this about a specific policy or benefit you're looking for?
• Do you need help finding the right person to contact?

I'm here to support you every step of the way! 💙"""
        
        context = "\n\n".join(relevant_chunks)
        
        prompt = f"""You are a professional, compassionate, and empathetic HR Assistant. Your role is to provide clear, structured, and specific answers based ONLY on the provided company documents and their linked content.

**YOUR ROLE AS HR ASSISTANT:**
• Provide accurate, document-based information
• Structure responses with clear bullet points and sections
• Be specific and actionable
• Show empathy and understanding
• Use professional HR language
• Format responses for easy reading

**RESPONSE STRUCTURE:**
1. **Brief acknowledgment** of the employee's question
2. **Clear, structured answer** with bullet points
3. **Specific details** from the documents
4. **Action items** if applicable
5. **Supportive closing** message

**FORMATTING REQUIREMENTS:**
• Use **bold headers** for sections
• Use bullet points (•) for lists
• Use numbered lists for steps or procedures
• Use emojis sparingly but appropriately
• Break information into digestible chunks
• Highlight important information

**CONTEXT FROM COMPANY DOCUMENTS:**
{context}

**EMPLOYEE QUESTION:** {question}

**HR ASSISTANT RESPONSE:**"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"""**I apologize for the technical difficulty! 😔**

I encountered an error while processing your question, but I want you to know that I'm here to help. 

**What you can do:**
• Try rephrasing your question
• Let me know if you need help with something else
• Contact HR directly if this is urgent

I'm committed to supporting you, and I'll do my best to get you the information you need! 💙"""
    
    def list_documents(self) -> List[dict]:
        """List all documents in the system"""
        return [
            {
                "title": doc["title"],
                "content_length": len(doc["content"]),
                "chunks": len(doc["chunks"])
            }
            for doc in self.documents
        ]
    
    def remove_document(self, title: str) -> str:
        """Remove a document and its chunks from the system"""
        # Find and remove the document
        for i, doc in enumerate(self.documents):
            if doc["title"] == title:
                # Remove document
                removed_doc = self.documents.pop(i)
                
                # Remove associated chunks
                self.document_chunks = [(chunk, doc_title) for chunk, doc_title in self.document_chunks if doc_title != title]
                
                return f"Document '{title}' removed successfully"
        
        return f"Document '{title}' not found"
    
    def get_fetched_urls(self) -> Dict[str, str]:
        """Get information about fetched URLs"""
        return {
            url: f"{len(content)} characters" 
            for url, content in self.fetched_urls.items()
        }

# Initialize the HR Q&A system
try:
    qa_system = HRDocumentQASystem()
    
    # Add sample document if it exists
    sample_doc_path = "sample_document.txt"
    if os.path.exists(sample_doc_path):
        qa_system.add_document_from_file(sample_doc_path)
        print("✅ Sample document loaded successfully")
    else:
        print("⚠️  sample_document.txt not found")
        
except Exception as e:
    print(f"❌ Error initializing HR Q&A system: {e}")
    qa_system = None

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not qa_system:
        return jsonify({
            "error": "HR Q&A system not initialized. Please check your API key."
        }), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Debug logging
        print(f"💬 Employee Question: {message}")
        print(f"📚 Documents available: {len(qa_system.documents)}")
        print(f"🔍 Chunks available: {len(qa_system.document_chunks)}")
        
        # Get response from HR Q&A system
        response = qa_system.ask_question(message)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of loaded documents"""
    if not qa_system:
        return jsonify({"error": "HR Q&A system not initialized"}), 500
    
    try:
        documents = qa_system.list_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload a new document"""
    if not qa_system:
        return jsonify({"error": "HR Q&A system not initialized"}), 500
    
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        allowed_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm', '.pdf'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            }), 400
        
        # Handle PDF files
        if file_ext == '.pdf':
            try:
                # Read PDF content
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
                content = ""
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text() + "\n"
                
                if not content.strip():
                    return jsonify({
                        "error": "PDF appears to be empty or contains no extractable text. It might be scanned or image-based."
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "error": f"Failed to read PDF: {str(e)}"
                }), 400
        else:
            # Handle text files with proper encoding handling
            try:
                # First try UTF-8
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # Try with latin-1 if UTF-8 fails
                    file.seek(0)  # Reset file pointer
                    content = file.read().decode('latin-1')
                except UnicodeDecodeError:
                    return jsonify({
                        "error": "Unable to read file. Please ensure it's a text file with UTF-8 or Latin-1 encoding."
                    }), 400
        
        title = file.filename
        
        # Add document to system
        result = qa_system.add_document(content, title, max_depth=2)
        
        # Debug logging
        print(f"📄 Uploaded document: {title}")
        print(f"📊 Content length: {len(content)} characters")
        print(f"📚 Total documents in system: {len(qa_system.documents)}")
        print(f"🔍 Total chunks in system: {len(qa_system.document_chunks)}")
        
        return jsonify({
            "message": result,
            "documents": qa_system.list_documents()
        })
        
    except Exception as e:
        print(f"Upload error: {str(e)}")  # Log the error for debugging
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/remove-document', methods=['POST'])
def remove_document():
    """Remove a document from the system"""
    if not qa_system:
        return jsonify({"error": "HR Q&A system not initialized"}), 500
    
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({"error": "Document title cannot be empty"}), 400
        
        result = qa_system.remove_document(title)
        
        return jsonify({
            "message": result,
            "documents": qa_system.list_documents()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetched-urls', methods=['GET'])
def get_fetched_urls():
    """Get information about fetched URLs"""
    if not qa_system:
        return jsonify({"error": "HR Q&A system not initialized"}), 500
    
    try:
        urls = qa_system.get_fetched_urls()
        return jsonify({"fetched_urls": urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if qa_system:
        print("🚀 Starting HR Document Q&A Web Server with Link Following...")
        print("📚 Loaded documents:", len(qa_system.documents))
        print("🌐 Open your browser and go to: http://localhost:8080")
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        print("❌ Failed to start server. Please check your configuration.") 