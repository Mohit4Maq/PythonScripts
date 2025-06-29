# HR Document Q&A System

A sophisticated Flask-based web application that provides an intelligent HR assistant capable of answering questions about company policies, employee benefits, and workplace guidelines using document analysis and link-following capabilities.

## 🚀 Features

### Core Functionality
- **Document Upload & Processing**: Support for PDF and text files
- **Intelligent Q&A**: Powered by Google Gemini AI for natural language understanding
- **HR Persona**: Professional, empathetic responses with structured formatting
- **Link Following**: Automatically extracts and fetches content from URLs in documents
- **PDF Link Extraction**: Detects and processes clickable hyperlinks in PDF files
- **Authentication**: Google OAuth and Email OTP login options

### Advanced Capabilities
- **Multi-Document Support**: Handle multiple documents simultaneously
- **Semantic Search**: Find relevant information using embeddings
- **Context-Aware Responses**: Maintain conversation context
- **Real Email OTP**: Secure one-time password authentication via email
- **Multi-Provider Email Support**: Gmail, Outlook, Yahoo, and custom SMTP
- **Enhanced Security**: 2-minute OTP expiry for improved security
- **Retry Logic**: Automatic email delivery retry with fallback to console output

## 🔐 Authentication Options

The system supports two authentication methods:

### 1. Google OAuth
- Sign in with your Google account
- Secure and convenient
- No additional setup required

### 2. Email OTP (One-Time Password)
- Receive a secure code via email
- Works with any email address
- **2-minute expiry** for enhanced security
- Configurable for multiple email providers

#### Email OTP Setup

**Quick Setup:**
1. Copy `env_example.txt` to `.env`
2. Configure your email settings:
   ```bash
   EMAIL_ENABLED=true
   EMAIL_PROVIDER=gmail
   EMAIL_USERNAME=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_FROM=your-email@gmail.com
   ```
3. Test your configuration: `python test_email_otp.py`

**Supported Email Providers:**
- **Gmail**: Most popular, easy setup
- **Outlook/Hotmail**: Microsoft email services
- **Yahoo**: Yahoo Mail accounts
- **Custom SMTP**: Any email provider with SMTP support

**Detailed Setup Instructions:**
See [EMAIL_SETUP.md](EMAIL_SETUP.md) for comprehensive setup and troubleshooting guides.

## 🚀 Usage

### Starting the Server

Run the HR bot server with authentication:
```bash
python web_app_hr_bot_auth.py
```

The application will be available at `http://localhost:8080`

### Testing Email Configuration

Before using email OTP, test your configuration:
```bash
python test_email_otp.py
```

This will:
- Validate your email settings
- Test SMTP connection
- Send a test email
- Provide detailed feedback

### Testing OTP Login Flow

Use the provided test script to verify OTP functionality:
```bash
python test_otp_login_flow.py
```

This script will:
- Automate the OTP login process
- Prompt for OTP from console output
- Verify successful authentication
- Test the complete login flow

### Available Applications

1. **HR Bot with Auth** (`web_app_hr_bot_auth.py`): Main HR assistant with authentication
2. **HR Bot** (`web_app_hr_bot.py`): Main HR assistant with professional persona
3. **Multi-Model** (`web_app_multi_model.py`): Support for multiple AI models
4. **Link Following** (`web_app_with_links.py`): Enhanced link processing
5. **Basic** (`web_app.py`): Simple document Q&A

### API Endpoints

- `GET /` - Main interface
- `GET /login` - Login page
- `GET /email` - Email OTP login page
- `POST /login/email` - Request OTP
- `POST /login/email/verify` - Verify OTP
- `POST /api/upload` - Upload documents (requires authentication)
- `POST /api/chat` - Ask questions (requires authentication)
- `GET /api/documents` - List uploaded documents (requires authentication)
- `GET /api/fetched-urls` - View fetched URL content (requires authentication)

## 📁 Project Structure

```
Testing1/
├── web_app_hr_bot_auth.py      # Main application with authentication
├── web_app_hr_bot.py           # HR assistant with professional persona
├── web_app_multi_model.py      # Multi-model support
├── web_app_with_links.py       # Enhanced link following
├── web_app.py                  # Basic document Q&A
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── EMAIL_SETUP.md             # Email configuration guide
├── test_email_otp.py          # Email testing script
├── test_otp_login_flow.py     # OTP login flow test script
├── env_example.txt            # Environment variables template
├── templates/                 # HTML templates
│   ├── index.html            # Main interface
│   ├── login.html            # Login page
│   └── index_multi_model.html # Multi-model interface
└── documents/                # Sample documents
    ├── sample_document.txt   # Sample HR policy
    └── test_*.txt           # Test documents with links
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env_example.txt`:

```bash
# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GEMINI_API_KEY=your-gemini-api-key
FLASK_SECRET_KEY=your-secret-key

# Email Configuration
EMAIL_ENABLED=true
EMAIL_PROVIDER=gmail
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=HR Document Q&A System
```

### Email Provider Configuration

**Gmail (Recommended):**
```bash
EMAIL_PROVIDER=gmail
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-digit-app-password
```

**Outlook/Hotmail:**
```bash
EMAIL_PROVIDER=outlook
EMAIL_USERNAME=your-email@outlook.com
EMAIL_PASSWORD=your-app-password
```

**Custom SMTP:**
```bash
EMAIL_PROVIDER=custom
EMAIL_SMTP_SERVER=smtp.your-provider.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USERNAME=your-email@domain.com
EMAIL_PASSWORD=your-password
```

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Testing1
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp env_example.txt .env
   # Edit .env with your credentials
   ```

5. **Test email configuration (optional):**
   ```bash
   python test_email_otp.py
   ```

6. **Test OTP login flow (optional):**
   ```bash
   python test_otp_login_flow.py
   ```

7. **Start the application:**
   ```bash
   python web_app_hr_bot_auth.py
   ```

## 🔒 Security Features

- **OAuth Authentication**: Secure Google OAuth integration
- **Email OTP**: Time-limited one-time passwords (2-minute expiry)
- **Session Management**: Secure session handling
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Graceful error management
- **Rate Limiting**: Built-in protection against abuse
- **Retry Logic**: Automatic email delivery retry with fallback

## 📧 Email OTP Security

- **Time-Limited**: OTPs expire after **2 minutes** (enhanced security)
- **Single-Use**: Each OTP can only be used once
- **Secure Delivery**: Sent via encrypted SMTP
- **Fallback Protection**: Console output if email fails
- **Retry Logic**: Automatic retry on connection issues
- **Multiple Providers**: Support for Gmail, Outlook, Yahoo, and custom SMTP

## 🚀 Deployment

### Local Development
```bash
python web_app_hr_bot_auth.py
```

### Production Deployment
1. Set up environment variables
2. Configure email provider
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up reverse proxy (Nginx, Apache)
5. Configure SSL/TLS certificates

### Docker Deployment
```bash
docker build -t hr-document-qa .
docker run -p 8080:8080 --env-file .env hr-document-qa
```

## 🔧 Troubleshooting

### Common Issues

1. **Email OTP not working:**
   - Check `EMAIL_ENABLED=true` in `.env`
   - Verify email credentials
   - Run `python test_email_otp.py`
   - See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed troubleshooting

2. **Google OAuth issues:**
   - Verify OAuth credentials in Google Cloud Console
   - Check redirect URIs configuration
   - Ensure HTTPS in production

3. **Document upload problems:**
   - Check file format (PDF, TXT supported)
   - Verify file size limits
   - Check authentication status

4. **OTP expiry issues:**
   - OTPs now expire after 2 minutes (reduced from 5 minutes)
   - Request a new OTP if the current one expires
   - Check console output for OTP during testing

### Getting Help

1. Check the troubleshooting sections in this README
2. Review [EMAIL_SETUP.md](EMAIL_SETUP.md) for email-specific issues
3. Run the test scripts to isolate problems:
   - `python test_email_otp.py` for email configuration
   - `python test_otp_login_flow.py` for OTP login flow
4. Check application logs for detailed error messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
1. Check the documentation
2. Review troubleshooting guides
3. Test with provided scripts
4. Open an issue with detailed information

## 🆕 Recent Updates

- **Enhanced Security**: OTP expiry reduced to 2 minutes for better security
- **Improved Email OTP**: Added retry logic and fallback to console output
- **Better Error Handling**: Enhanced error messages and user feedback
- **Test Scripts**: Added comprehensive testing tools for email and OTP functionality
- **Documentation**: Updated guides and troubleshooting information

---

**🎉 Ready to get started?** Follow the installation guide above and test your email configuration with `python test_email_otp.py`!