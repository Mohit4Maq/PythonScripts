#!/usr/bin/env python3
"""
Flask Web Application for Document-Based Q&A with Google Gemini
Provides a beautiful chat interface for querying documents with model selection
"""

import os
import json
from typing import List, Optional
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import PyPDF2
import io
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

class DocumentQASystem:
    def __init__(self):
        self.documents = []
        self.document_chunks = []
        self.chunk_size = 1000
        
        # Initialize Google Gemini API
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
    
    def add_document(self, content: str, title: str = "Document"):
        """Add a document to the system"""
        # Split content into chunks
        chunks = self._chunk_text(content)
        
        # Store document
        document = {
            "title": title,
            "content": content,
            "chunks": chunks
        }
        self.documents.append(document)
        
        # Add chunks to searchable index
        for chunk in chunks:
            self.document_chunks.append((chunk, title))
        
        return f"Document '{title}' added successfully with {len(chunks)} chunks"
    
    def add_document_from_file(self, file_path: str, title: Optional[str] = None):
        """Add a document from a file"""
        try:
            if file_path.lower().endswith('.pdf'):
                # Handle PDF files
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    
                    # Extract text from all pages
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
                    
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
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini API Error: {e}"
    
    def ask_question(self, question: str) -> str:
        """Ask a question and get answer based only on provided documents"""
        if not self.documents:
            return "I don't have any documents loaded yet. Please upload some documents first, and I'll be happy to help you analyze them!"
        
        if not self.google_api_key:
            return "Google Gemini API key not configured. Please set GOOGLE_API_KEY in your .env file."
        
        relevant_chunks = self._find_relevant_chunks(question)
        
        if not relevant_chunks:
            return "I couldn't find specific information about that in the documents you've provided. However, I can help you with general questions or suggest what kind of information might be useful to look for. Could you rephrase your question or let me know what specific aspect you'd like to explore?"
        
        context = "\n\n".join(relevant_chunks)
        
        prompt = f"""You are a knowledgeable and helpful assistant who specializes in analyzing documents. Your top priority is to provide clear, well-formatted, and easy-to-read responses.

FORMATTING REQUIREMENTS:
- Use bullet points (• or -) for lists and key points
- Add proper spacing between sections (double line breaks)
- Use bold text (**text**) for important terms or headings
- Structure information in clear, organized sections
- Use numbered lists when presenting steps or sequences
- Keep paragraphs short and readable

CORE PRINCIPLES:
1. **Clarity**: Present information in a clear, organized manner
2. **Readability**: Use proper formatting with bullets, spacing, and structure
3. **Document Grounding**: Base your answer on the provided documents
4. **Completeness**: Provide comprehensive but well-organized information
5. **Professional Tone**: Be helpful and informative

WHEN ANSWERING:
- Start with a brief overview or direct answer
- Use bullet points for lists and key information
- Add proper spacing between different sections
- Use bold formatting for important terms
- Structure complex information in clear sections
- If providing multiple points, use numbered or bulleted lists
- Reference specific parts of the documents when relevant

DOCUMENTS TO ANALYZE:
{context}

QUESTION: {question}

Please provide a clear, well-formatted response with proper bullets, spacing, and structure based on the documents above. Make the information easy to read and understand."""
        
        return self._call_gemini_api(prompt)
    
    def remove_document(self, title: str) -> str:
        """Remove a document from the system"""
        # Find and remove the document
        document_to_remove = None
        for doc in self.documents:
            if doc["title"] == title:
                document_to_remove = doc
                break
        
        if not document_to_remove:
            return f"Document '{title}' not found"
        
        # Remove document from documents list
        self.documents.remove(document_to_remove)
        
        # Remove all chunks associated with this document
        self.document_chunks = [(chunk, doc_title) for chunk, doc_title in self.document_chunks if doc_title != title]
        
        return f"Document '{title}' removed successfully"
    
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
        
    print("🤖 Using Google Gemini API")
        
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
            "error": "Q&A system not initialized. Please check your API keys."
        }), 500
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        response = qa_system.ask_question(message)
        return jsonify({
            "response": response,
            "model_used": "gemini"
        })
    except Exception as e:
        return jsonify({
            "error": f"Error processing question: {str(e)}"
        }), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of loaded documents"""
    if not qa_system:
        return jsonify({"error": "Q&A system not initialized"})
    
    return jsonify({
        "documents": qa_system.list_documents(),
        "total_documents": len(qa_system.documents)
    })

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload a new document"""
    if not qa_system:
        return jsonify({"error": "Q&A system not initialized"})
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    title = file.filename
    try:
        if title.lower().endswith('.pdf'):
            # Handle PDF files
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
            if not content.strip():
                return jsonify({"error": f"PDF appears to be empty or contains no extractable text: {title}"}), 400
        else:
            # Handle text files
            try:
                content = file.read().decode('utf-8')
            except Exception as e:
                return jsonify({"error": f"Could not decode file as UTF-8 text: {e}"}), 400
        result = qa_system.add_document(content, title)
        return jsonify({"message": result, "documents": qa_system.list_documents()})
    except Exception as e:
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500

@app.route('/api/remove-document', methods=['POST'])
def remove_document():
    """Remove a document from the system"""
    if not qa_system:
        return jsonify({"error": "Q&A system not initialized"})
    
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({"error": "Document title is required"}), 400
    
    try:
        result = qa_system.remove_document(title)
        return jsonify({
            "message": result,
            "documents": qa_system.list_documents(),
            "total_documents": len(qa_system.documents)
        })
    except Exception as e:
        return jsonify({"error": f"Error removing document: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 Starting Document Q&A Web Server...")
    print(f"📚 Loaded documents: {len(qa_system.documents) if qa_system else 0}")
    print("🌐 Open your browser and go to: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True) 