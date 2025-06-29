# HR Document Q&A System

A sophisticated Flask-based web application that provides an intelligent HR assistant capable of answering questions about company policies, employee benefits, and workplace guidelines using document analysis and link-following capabilities.

## 🚀 Features

### Core Functionality
- **Document Upload & Processing**: Support for PDF and text files
- **Intelligent Q&A**: Powered by Google Gemini AI for natural language understanding
- **HR Persona**: Professional, empathetic responses with structured formatting
- **Link Following**: Automatically extracts and fetches content from URLs in documents
- **PDF Link Extraction**: Detects and processes clickable hyperlinks in PDF files

### Advanced Capabilities
- **Multi-Document Support**: Handle multiple documents simultaneously
- **Context-Aware Responses**: Provides relevant information from uploaded documents
- **Structured Output**: Professional formatting with bullet points and clear sections
- **Real-time Processing**: Instant responses with document analysis

## 📋 Requirements

- Python 3.8+
- Google Gemini API Key
- Internet connection (for link following)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Testing1
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 🚀 Usage

### Starting the Server

Run the HR bot server:
```bash
python web_app_hr_bot.py
```

The application will be available at `http://localhost:8080`

### Available Applications

1. **HR Bot** (`web_app_hr_bot.py`): Main HR assistant with professional persona
2. **Multi-Model** (`web_app_multi_model.py`): Support for multiple AI models
3. **Link Following** (`web_app_with_links.py`): Enhanced link processing
4. **Basic** (`web_app.py`): Simple document Q&A

### API Endpoints

- `GET /` - Main interface
- `POST /api/upload` - Upload documents
- `POST /api/chat` - Ask questions
- `GET /api/documents` - List uploaded documents
- `GET /api/fetched-urls` - View fetched URL content

## 📁 Project Structure

```
Testing1/
├── web_app_hr_bot.py          # Main HR bot application
├── web_app_multi_model.py     # Multi-model support
├── web_app_with_links.py      # Enhanced link following
├── web_app.py                 # Basic document Q&A
├── requirements.txt           # Python dependencies
├── templates/                 # HTML templates
│   ├── index.html
│   └── index_multi_model.html
├── sample_document.txt        # Sample company policy
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### Customization

You can customize the HR bot persona by modifying the prompt in `web_app_hr_bot.py`:

```python
HR_PROMPT = """
You are a professional HR Assistant with expertise in employee relations, 
company policies, and workplace guidelines. Provide empathetic, accurate, 
and helpful responses based on the available documents.
"""
```

## 📖 Example Usage

### Uploading Documents

1. Open the web interface at `http://localhost:8080`
2. Click "Choose File" and select your document (PDF or text)
3. Click "Upload Document"

### Asking Questions

Ask questions like:
- "What are the work hours?"
- "What is the maternity leave policy?"
- "Tell me about expense reimbursement"
- "What are the work from home policies?"

### Example Response Format

The system provides structured responses with:
- **Acknowledgment** of the question
- **Clear, structured answer** with bullet points
- **Specific details** from documents
- **Action items** when applicable
- **Supportive closing** message

## 🔗 Link Following

The system automatically:
1. Detects URLs in uploaded documents
2. Fetches content from those URLs
3. Integrates the fetched content into responses
4. Provides comprehensive answers using both document and linked content

## 🛡️ Security

- API keys are stored in environment variables
- Sensitive data is excluded from version control
- Virtual environment isolation
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔄 Updates

The system supports:
- Real-time document processing
- Dynamic link following
- Continuous learning from new documents
- Regular updates and improvements

---

**Note**: This system is designed for internal company use and should be deployed in a secure environment with appropriate access controls. 