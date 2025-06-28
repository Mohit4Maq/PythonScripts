#!/usr/bin/env python3
"""
Document-Based Q&A System with Google Gemini
This system allows Gemini to only respond based on the documents you provide
"""

import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json
import re
import PyPDF2
import io

# Load environment variables from .env file
load_dotenv()

class DocumentQASystem:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Document Q&A System
        
        Args:
            api_key (str): Google AI Studio API key
        """
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
        self.chunk_size = 1000  # Characters per chunk
        
    def add_document(self, content: str, title: str = "Document"):
        """
        Add a document to the system
        
        Args:
            content (str): Document content
            title (str): Document title/identifier
        """
        document = {
            "title": title,
            "content": content,
            "chunks": self._chunk_text(content)
        }
        self.documents.append(document)
        self.document_chunks.extend([(chunk, title) for chunk in document["chunks"]])
        print(f"✅ Added document: {title} ({len(content)} characters, {len(document['chunks'])} chunks)")
    
    def add_document_from_file(self, file_path: str, title: Optional[str] = None):
        """
        Add a document from a file
        
        Args:
            file_path (str): Path to the document file
            title (str): Optional title for the document
        """
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
                        print(f"❌ PDF appears to be empty or contains no extractable text: {file_path}")
                        return
            else:
                # Handle text files
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            
            if title is None:
                title = os.path.basename(file_path)
            
            self.add_document(content, title)
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file {file_path}: {e}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for better retrieval
        
        Args:
            text (str): Text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        # Simple chunking by character count
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]
            # Try to break at sentence boundaries
            if i + self.chunk_size < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > self.chunk_size * 0.7:  # Only break if we're not too early
                    chunk = chunk[:break_point + 1]
            chunks.append(chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def _find_relevant_chunks(self, query: str, top_k: int = 5) -> List[str]:
        """
        Find the most relevant document chunks for a query
        
        Args:
            query (str): User query
            top_k (int): Number of top chunks to return
            
        Returns:
            List[str]: Relevant document chunks
        """
        # Simple keyword-based retrieval
        query_words = set(query.lower().split())
        chunk_scores = []
        
        for chunk, title in self.document_chunks:
            chunk_words = set(chunk.lower().split())
            # Calculate simple word overlap score
            overlap = len(query_words.intersection(chunk_words))
            score = overlap / max(len(query_words), 1)
            chunk_scores.append((score, chunk, title))
        
        # Sort by score and return top chunks
        chunk_scores.sort(key=lambda x: x[0], reverse=True)
        relevant_chunks = []
        
        for score, chunk, title in chunk_scores[:top_k]:
            if score > 0:  # Only include chunks with some relevance
                relevant_chunks.append(f"[From: {title}]\n{chunk}")
        
        return relevant_chunks
    
    def ask_question(self, question: str) -> str:
        """
        Ask a question and get answer based only on provided documents
        
        Args:
            question (str): User question
            
        Returns:
            str: Answer based on documents
        """
        if not self.documents:
            return "I don't have any documents loaded yet. Please upload some documents first, and I'll be happy to help you analyze them!"
        
        # Find relevant document chunks
        relevant_chunks = self._find_relevant_chunks(question)
        
        if not relevant_chunks:
            return "I couldn't find specific information about that in the documents you've provided. However, I can help you with general questions or suggest what kind of information might be useful to look for. Could you rephrase your question or let me know what specific aspect you'd like to explore?"
        
        # Create context from relevant chunks
        context = "\n\n".join(relevant_chunks)
        
        # Create the prompt with improved instructions
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
    
    def list_documents(self) -> str:
        """
        List all documents in the system
        
        Returns:
            str: Formatted list of documents
        """
        if not self.documents:
            return "No documents have been added to the system."
        
        result = "📚 Documents in the system:\n"
        for i, doc in enumerate(self.documents, 1):
            result += f"{i}. {doc['title']} ({len(doc['content'])} characters, {len(doc['chunks'])} chunks)\n"
        
        return result
    
    def clear_documents(self):
        """Clear all documents from the system"""
        self.documents = []
        self.document_chunks = []
        print("✅ All documents cleared from the system")

def main():
    """Main function to run the Document Q&A system"""
    
    print("📚 Document-Based Q&A System with Google Gemini")
    print("=" * 60)
    print("This system allows Gemini to only respond based on your documents")
    print()
    
    try:
        # Initialize the system
        qa_system = DocumentQASystem()
        print("✅ Gemini API configured successfully!")
        print()
        
        # Add some example documents (you can replace these with your own)
        print("📖 Adding example documents...")
        
        # Example document 1
        example_doc1 = """
        Python Programming Language
        
        Python is a high-level, interpreted programming language created by Guido van Rossum and first released in 1991. 
        It is known for its simplicity and readability, making it an excellent choice for beginners and experienced developers alike.
        
        Key Features:
        - Easy to learn and use
        - Extensive standard library
        - Cross-platform compatibility
        - Strong community support
        - Used in web development, data science, AI, and more
        
        Python uses indentation to define code blocks, which enforces clean and readable code structure.
        """
        
        # Example document 2
        example_doc2 = """
        Machine Learning Basics
        
        Machine Learning is a subset of artificial intelligence that enables computers to learn and make decisions 
        without being explicitly programmed for every task. It focuses on developing algorithms that can access data 
        and use it to learn for themselves.
        
        Types of Machine Learning:
        1. Supervised Learning: Learning from labeled training data
        2. Unsupervised Learning: Finding patterns in unlabeled data
        3. Reinforcement Learning: Learning through interaction with environment
        
        Common applications include image recognition, natural language processing, recommendation systems, 
        and predictive analytics.
        """
        
        qa_system.add_document(example_doc1, "Python Programming Guide")
        qa_system.add_document(example_doc2, "Machine Learning Introduction")
        
        # Automatically add sample_document.txt if it exists
        sample_doc_path = "sample_document.txt"
        if os.path.exists(sample_doc_path):
            qa_system.add_document_from_file(sample_doc_path)
        
        print("\n🤖 Interactive Q&A Session")
        print("Type 'quit' to exit")
        print("Type 'docs' to list documents")
        print("Type 'clear' to clear all documents")
        print("Type 'add <filename>' to add a document from file")
        print("-" * 50)
        
        while True:
            user_input = input("\n❓ Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == 'docs':
                print("\n" + qa_system.list_documents())
                continue
            
            if user_input.lower() == 'clear':
                qa_system.clear_documents()
                continue
            
            if user_input.lower().startswith('add '):
                filename = user_input[4:].strip()
                qa_system.add_document_from_file(filename)
                continue
            
            if not user_input:
                continue
            
            print("\n🤖 Answer: ", end="")
            answer = qa_system.ask_question(user_input)
            print(answer)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your API key in the .env file")

if __name__ == "__main__":
    main() 