#!/usr/bin/env python3
"""
Flask Web Application for Document-Based Q&A with Google Gemini
Provides a beautiful chat interface for querying documents
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from typing import List, Optional
from dotenv import load_dotenv
import json
from datetime import datetime
import PyPDF2
import io

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

class DocumentQASystem:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Document Q&A System"""
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("Please provide an API key or set GOOGLE_API_KEY in .env file")
            genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.documents = []
        self.document_chunks = []
        self.chunk_size = 1000
        
    def add_document(self, content: str, title: str = "Document"):
        """Add a document to the system"""
        document = {
            "title": title,
            "content": content,
            "chunks": self._chunk_text(content)
        }
        self.documents.append(document)
        self.document_chunks.extend([(chunk, title) for chunk in document["chunks"]])
        return f"Added document: {title} ({len(content)} characters, {len(document['chunks'])} chunks)"
    
    def add_document_from_file(self, file_path: str, title: Optional[str] = None):
        """Add a document from a file"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                # Handle PDF files
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    
                    # Extract text from all pages
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        content += page.extract_text() + "\n"
                    
                    if not content.strip():
                        return f"PDF appears to be empty or contains no extractable text: {file_path}"
            else:
                # Handle text files
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            
            if title is None:
                title = os.path.basename(file_path)
            
            return self.add_document(content, title)
            
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {e}"
    
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
        """Ask a question and get answer based only on provided documents"""
        if not self.documents:
            return "I don't have any documents loaded yet. Please upload some documents first, and I'll be happy to help you analyze them!"
        
        relevant_chunks = self._find_relevant_chunks(question)
        
        if not relevant_chunks:
            return "I couldn't find specific information about that in the documents you've provided. However, I can help you with general questions or suggest what kind of information might be useful to look for. Could you rephrase your question or let me know what specific aspect you'd like to explore?"
        
        context = "\n\n".join(relevant_chunks)
        
        prompt = f"""You are a knowledgeable and helpful assistant who specializes in analyzing documents. Your top priority is to answer questions as directly, precisely, and to-the-point as possible, while still being friendly and helpful.

CORE PRINCIPLES:
1. **Directness**: Start with a clear, concise answer to the question.
2. **Precision**: Be as specific and succinct as possible. Avoid unnecessary elaboration unless asked.
3. **Document Grounding**: Base your answer on the provided documents.
4. **Reasoning**: Only provide detailed reasoning or analysis if the question requests it, or if clarification is needed.
5. **Conversational Tone**: Remain approachable and helpful.

WHEN ANSWERING:
- Begin with a direct, precise answer.
- Only elaborate with reasoning or details if the question asks for it or if it improves clarity.
- Reference specific parts of the documents if relevant.
- If the answer is not in the documents, say so clearly.

DOCUMENTS TO ANALYZE:
{context}

QUESTION: {question}

Please provide a direct, precise, and to-the-point answer based on the documents above. Only elaborate if necessary or requested."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {e}. Please try rephrasing your question or let me know if you need help with something else."
    
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

# Initialize the Q&A system
try:
    qa_system = DocumentQASystem()
    
    # Add sample document if it exists
    sample_doc_path = "sample_document.txt"
    if os.path.exists(sample_doc_path):
        qa_system.add_document_from_file(sample_doc_path)
        print("✅ Sample document loaded successfully")
    else:
        print("⚠️  sample_document.txt not found")
        
except Exception as e:
    print(f"❌ Error initializing Q&A system: {e}")
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
            "error": "Q&A system not initialized. Please check your API key."
        }), 500
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Debug logging
        print(f"💬 Question: {message}")
        print(f"📚 Documents available: {len(qa_system.documents)}")
        print(f"🔍 Chunks available: {len(qa_system.document_chunks)}")
        
        # Get response from Q&A system
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
        return jsonify({"error": "Q&A system not initialized"}), 500
    
    try:
        documents = qa_system.list_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload a new document"""
    if not qa_system:
        return jsonify({"error": "Q&A system not initialized"}), 500
    
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
        result = qa_system.add_document(content, title)
        
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

if __name__ == '__main__':
    if qa_system:
        print("🚀 Starting Document Q&A Web Server...")
        print("📚 Loaded documents:", len(qa_system.documents))
        print("🌐 Open your browser and go to: http://localhost:8080")
        app.run(debug=True, host='0.0.0.0', port=8080)
    else:
        print("❌ Failed to start server. Please check your configuration.") 