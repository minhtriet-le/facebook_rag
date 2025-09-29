# 🤖 Facebook RAG System

A sophisticated **Retrieval-Augmented Generation (RAG)** system designed to crawl, process, and analyze Facebook's policy documentation using advanced AI techniques.

## 📖 Overview

This project implements an end-to-end RAG pipeline that:
- 🕷️ **Crawls** Facebook transparency and policy documents
- 🧠 **Processes** content using advanced text chunking strategies
- 🔍 **Embeds** text using state-of-the-art sentence transformers
- 💾 **Stores** data in PostgreSQL with vector search capabilities
- 🤖 **Generates** intelligent responses using Google Gemini AI

## 🏗️ Architecture

```
Facebook Policy Sites → Web Crawler → Text Chunking → Embedding Model → PostgreSQL (pgvector)
                                                                              ↓
User Query → Query Embedding → Vector Search → Context Retrieval → Gemini AI → Response
```

## 📁 Project Structure

```
facebook_rag/
├── 🕷️ crawler.py          # Web crawler for Facebook policy sites
├── 🧠 embedding.py        # Text embedding and vector processing
├── 🤖 RAG.py              # Main RAG system implementation
├── 🔍 top_k.py            # Top-K similarity search functionality
├── 📄 roots.txt           # Target URLs for crawling
├── 📋 requirements.txt    # Python dependencies
├── 📝 README.md          # Project documentation
└── 🔐 credential/        # Configuration and API keys
    └── config.py         # Database and API configurations
```

## 🛠️ Technologies Used

- **AI/ML**: Google Gemini AI, Sentence Transformers (BAAI/bge-m3)
- **Database**: PostgreSQL with pgvector extension
- **Web Scraping**: requests, BeautifulSoup4
- **Language**: Python 3.8+
- **Vector Search**: Cosine similarity with PostgreSQL

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL with pgvector extension**
2. **Google Gemini API key**
3. **Python 3.8+**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/minhtriet-le/facebook_rag.git
cd facebook_rag
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database and API credentials**
```python
# credential/config.py
DB_NAME = "your_database_name"
DB_USER = "your_username"
DB_PASS = "your_password"
DB_HOST = "localhost"
DB_PORT = 5432
GEMINI_API_KEY = "your_gemini_api_key"
```

### Usage

1. **Crawl Facebook policy documents**
```bash
python crawler.py
```

2. **Generate embeddings for crawled content**
```bash
python embedding.py
```

3. **Run RAG queries**
```bash
python RAG.py
```

4. **Test top-K similarity search**
```bash
python top_k.py
```

## 🔧 Configuration

### Database Setup

```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tables are automatically created by crawler.py
-- documents: stores webpage metadata
-- chunks: stores text chunks with embeddings
```

### Crawling Targets

Edit `roots.txt` to modify crawling targets:
```
https://transparency.meta.com/vi-vn/
# Add more URLs here
```

## 📊 Features

- **🎯 Intelligent Chunking**: Auto-splits documents with configurable overlap
- **🔍 Semantic Search**: Vector-based similarity search using cosine distance  
- **🤖 AI-Powered QA**: Context-aware responses using Google Gemini
- **⚡ Efficient Storage**: PostgreSQL with vector indexing for fast retrieval
- **🛡️ Robust Crawling**: Handles various HTML structures and content types

## 🔍 Example Queries

The system can answer questions like:
- "Đăng tải nội dung bóc lột trẻ em có đúng với chính sách Facebook?"
- "Facebook xử lý thông tin cá nhân như thế nào?"
- "Quy định về nội dung bạo lực trên Facebook là gì?"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Facebook/Meta** for providing transparent policy documentation
- **Google** for Gemini AI API
- **Sentence Transformers** for embedding models
- **PostgreSQL** community for pgvector extension

## 📞 Contact

- **Repository**: [facebook_rag](https://github.com/minhtriet-le/facebook_rag)
- **Issues**: [Report bugs or request features](https://github.com/minhtriet-le/facebook_rag/issues)

---

*Built with ❤️ for AI-powered content analysis*