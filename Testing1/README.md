# Document Q&A System with Google Gemini

A powerful document-based question-answering system that uses Google's Gemini AI to provide intelligent, conversational responses based on your uploaded documents. The system supports multiple file formats including PDFs and provides a beautiful web interface.

## 🌟 Features

- **📄 Multi-Format Support**: Upload PDF, TXT, MD, CSV, JSON, XML, HTML files
- **🤖 Conversational AI**: Intelligent, analytical responses with detailed reasoning
- **🌐 Beautiful Web Interface**: Modern, responsive design with real-time chat
- **📊 Document Analysis**: Deep analysis and insights from your documents
- **🔍 Smart Retrieval**: Finds the most relevant document chunks for each question
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google AI Studio API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Testing1
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_ai_studio_api_key_here
   ```

5. **Run the application**
   ```bash
   python web_app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8080`

## 📋 Usage

### Web Interface

1. **Upload Documents**: Click "Choose File" to upload your documents
2. **Ask Questions**: Type your questions in the chat interface
3. **Get Insights**: Receive detailed, analytical responses based on your documents

### Supported File Types

- **PDF** (.pdf) - Full text extraction from all pages
- **Text** (.txt, .md) - Plain text and markdown files
- **Data** (.csv, .json, .xml) - Structured data files
- **Web** (.html, .htm) - HTML documents

### Example Questions

- "What are the key points in this document?"
- "Can you analyze the company culture described here?"
- "What are the main benefits mentioned?"
- "Are there any potential concerns or red flags?"
- "How does this compare to industry standards?"

## 🏗️ Architecture

### Core Components

- **`web_app.py`**: Flask web application with REST API
- **`document_qa.py`**: Core document processing and Q&A logic
- **`templates/index.html`**: Modern web interface with CSS/JavaScript
- **`requirements.txt`**: Python dependencies

### Key Features

- **Document Chunking**: Intelligent text segmentation for better retrieval
- **Relevant Retrieval**: Finds the most pertinent document sections
- **Conversational AI**: Friendly, analytical responses with reasoning
- **Error Handling**: Graceful handling of various file formats and errors

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google AI Studio API key (required)

### Customization

You can modify the following parameters in the code:

- **Chunk Size**: Adjust `chunk_size` in `DocumentQASystem` class
- **Retrieval Count**: Change `top_k` in `_find_relevant_chunks` method
- **Server Port**: Modify port in `web_app.py` (default: 8080)

## 📊 API Endpoints

- `GET /`: Main web interface
- `POST /api/chat`: Send questions and get responses
- `POST /api/upload`: Upload new documents
- `GET /api/documents`: List loaded documents

## 🛠️ Development

### Project Structure

```
Testing1/
├── web_app.py              # Main Flask application
├── document_qa.py          # Core Q&A system
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Web interface template
└── venv/                  # Virtual environment (auto-created)
```

### Adding New Features

1. **New File Formats**: Add parsing logic in `add_document_from_file` method
2. **UI Enhancements**: Modify `templates/index.html` and associated CSS/JS
3. **AI Improvements**: Update prompts in `ask_question` method

## 🔒 Security

- API keys are stored in environment variables
- File uploads are validated for type and content
- No sensitive data is logged or stored permanently

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing process
   pkill -f "python web_app.py"
   # Or change port in web_app.py
   ```

2. **API Key Issues**
   - Ensure your `.env` file contains the correct API key
   - Verify the key is active in Google AI Studio

3. **PDF Upload Problems**
   - Ensure PDF contains extractable text (not scanned images)
   - Check file size (large files may take time to process)

4. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

## 📈 Performance

- **Document Processing**: ~1000 characters per chunk
- **Response Time**: 2-5 seconds depending on document size
- **Memory Usage**: Scales with document size and number of chunks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google AI Studio for providing the Gemini API
- Flask framework for the web application
- PyPDF2 for PDF text extraction
- All contributors and users

---

**Happy Document Analysis! 📚✨** 