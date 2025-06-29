# Document Q&A System with Link Following

## Overview

The Document Q&A system now includes advanced link-following functionality that automatically extracts URLs from uploaded documents and fetches their content to provide more comprehensive answers.

## Features

### 🔗 Link Following Capability
- **Automatic URL Detection**: The system automatically detects URLs in uploaded documents using regex patterns
- **Content Fetching**: Fetches content from detected URLs using web scraping
- **Content Integration**: Merges fetched content with original document content
- **Caching**: Caches fetched URLs to avoid repeated requests
- **Error Handling**: Robust error handling with retry logic and fallback mechanisms

### 📄 Document Processing
- **Text Files**: Supports .txt, .md, .csv, .json, .xml, .html, .htm files
- **PDF Files**: Extracts text from PDF documents
- **Encoding Support**: Handles UTF-8 and Latin-1 encoding
- **Link Processing**: Automatically processes links during document upload

### 🤖 AI Integration
- **Enhanced Context**: LLM receives both original document content and fetched linked content
- **Comprehensive Answers**: Provides answers based on both local and external content
- **Source Attribution**: Mentions when information comes from linked content

## How It Works

### 1. Document Upload Process
```
Document Upload → URL Detection → Content Fetching → Content Integration → Chunking → Storage
```

### 2. Link Following Process
1. **URL Extraction**: Uses regex pattern to find URLs in document content
2. **Content Fetching**: Makes HTTP requests to fetch content from URLs
3. **HTML Parsing**: Uses BeautifulSoup to extract clean text from HTML
4. **Content Cleaning**: Removes scripts, styles, and formats text
5. **Content Limiting**: Truncates content to prevent overwhelming the LLM
6. **Integration**: Merges fetched content with original document content

### 3. Question Answering Process
1. **Relevance Scoring**: Finds most relevant document chunks
2. **Context Building**: Includes both original and linked content
3. **AI Processing**: Sends enhanced context to Gemini LLM
4. **Response Generation**: Returns comprehensive answers

## API Endpoints

### Core Endpoints
- `POST /api/upload` - Upload documents with link processing
- `POST /api/chat` - Ask questions (now includes linked content)
- `GET /api/documents` - List uploaded documents
- `POST /api/remove-document` - Remove documents

### New Endpoints
- `GET /api/fetched-urls` - Get information about fetched URLs

## Technical Implementation

### Dependencies Added
```python
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
```

### Key Methods

#### URL Extraction
```python
def _extract_urls_from_text(self, text: str) -> Set[str]:
    """Extract URLs from text content using regex"""
```

#### Content Fetching
```python
def _fetch_url_content(self, url: str, max_retries: int = 3) -> Optional[str]:
    """Fetch content from URL with retry logic and error handling"""
```

#### Link Processing
```python
def _process_document_links(self, content: str, title: str) -> str:
    """Process document content to extract and fetch linked content"""
```

## Example Usage

### 1. Upload Document with Links
```bash
curl -X POST "http://localhost:8080/api/upload" \
  -F "file=@document_with_links.txt"
```

### 2. Ask Questions About Linked Content
```bash
curl -X POST "http://localhost:8080/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What information about Python is available from the linked resources?"}'
```

### 3. Check Fetched URLs
```bash
curl -X GET "http://localhost:8080/api/fetched-urls"
```

## Example Results

### Document with Links
```
Simple Test Document with Links

This document contains a few simple links to test the link-following functionality.

LINKS TO TEST:
- Python documentation: https://docs.python.org
- GitHub: https://github.com

WORK HOURS:
- Standard work hours are 9:00 AM to 5:00 PM, Monday through Friday
```

### Enhanced Content (After Link Processing)
The document grows from ~500 characters to ~13,000 characters, including:
- Python documentation content (versions, licensing, resources)
- GitHub platform information (features, services, performance data)

### Sample AI Response
```
**Information about Python from Linked Resources**

The provided `simple_test_links.txt` file contains a link to the Python documentation: `https://docs.python.org`. Based on the snippets from that website included in `simple_test_links.txt`, we can glean the following information:

- **Python Versions:** The documentation mentions various Python versions, ranging from Python 3.15 (in development) down to Python 2.7 (EOL – End of Life).

- **Licensing:** The Python documentation specifies that it is licensed under the Python Software Foundation License Version 2.

- **Resources:** The documentation provides access to various resources, including:
  - A PEP (Python Enhancement Proposal) Index
  - A Beginner's Guide
  - A Book List
  - Audio/Visual Talks
  - A Python Developer's Guide
```

## Benefits

### 1. **Comprehensive Information**
- Access to external content referenced in documents
- More complete and accurate answers
- Real-time information from live websites

### 2. **Enhanced User Experience**
- No need to manually visit linked resources
- Seamless integration of local and external content
- Source attribution for transparency

### 3. **Scalable Architecture**
- Caching prevents redundant requests
- Error handling ensures system stability
- Configurable content limits prevent overload

## Configuration

### Content Limits
- **Max Content Length**: 10,000 characters per URL (configurable)
- **Retry Attempts**: 3 attempts with exponential backoff
- **Timeout**: 10 seconds per request

### User Agent
- Uses realistic browser user agent to avoid blocking
- Configurable headers for different websites

## Error Handling

### Network Errors
- Automatic retry with exponential backoff
- Graceful fallback if URLs are inaccessible
- Detailed logging for debugging

### Content Processing
- Handles various HTML structures
- Removes scripts and styles for clean text
- Handles encoding issues

## Future Enhancements

### Potential Improvements
1. **Selective Link Following**: Allow users to choose which links to follow
2. **Content Filtering**: Filter content based on relevance
3. **Link Validation**: Validate URLs before fetching
4. **Rate Limiting**: Implement rate limiting for external requests
5. **Content Summarization**: Summarize long fetched content
6. **Link Categories**: Categorize links by type (documentation, news, etc.)

## Testing

### Test Documents Created
1. `test_document_real_links.txt` - Document with real, accessible URLs
2. `simple_test_links.txt` - Simple test document with Python and GitHub links
3. `test_document_with_links.txt` - Document with example URLs

### Test Results
- ✅ URL detection working correctly
- ✅ Content fetching from real websites
- ✅ Content integration with original documents
- ✅ AI responses include linked content
- ✅ Caching prevents duplicate requests
- ✅ Error handling for inaccessible URLs

## Conclusion

The link-following functionality significantly enhances the Document Q&A system by:

1. **Expanding Knowledge Base**: Access to external content referenced in documents
2. **Improving Answer Quality**: More comprehensive and up-to-date information
3. **Enhancing User Experience**: Seamless access to linked resources
4. **Maintaining Reliability**: Robust error handling and caching

The system now provides a truly comprehensive document analysis experience that goes beyond the uploaded content to include relevant external resources. 