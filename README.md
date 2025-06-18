> This project was completed as the Final Project for 'Generative AI and Blockchain 2025' at GIST, supervised by Professor Heung-No Lee.

# Sillok

A confidence-driven note-taking application that leverages **Generative AI**, **Blockchain**, and **IPFS** for secure, verifiable, and intelligent document management.

## Overview

Sillok is an innovative note-taking application that combines traditional document management with cutting-edge technologies to provide:

-   **Secure Storage**: Documents stored on IPFS with metadata integrity guaranteed by Ethereum blockchain ([Worldland](https://worldland.foundation))
-   **AI-Powered Assistance**: RAG (Retrieval Augmented Generation) chatbot that can answer questions about your notes
-   **Verifiable Integrity**: Cryptographic verification of document authenticity using blockchain records
-   **Semantic Search**: Vector embeddings enable intelligent content discovery and retrieval

## Demo Video

<div align="center">

[![sillok demo](https://img.youtube.com/vi/4QAgxsqWezs/0.jpg)](https://youtu.be/4QAgxsqWezs)

</div>

## Objectives

-   **Data Integrity**: Ensure document authenticity and prevent tampering through blockchain verification
-   **Decentralized Storage**: Leverage IPFS for censorship-resistant and distributed file storage
-   **Intelligent Interaction**: Provide AI-powered insights and Q&A capabilities for stored documents
-   **User Privacy**: Maintain user control over their data while enabling collaborative features
-   **Educational Research**: Demonstrate practical integration of AI, blockchain, and decentralized technologies

## Scope

### Core Features

-   ✅ **Document Management**: Create, read, update, delete markdown documents
-   ✅ **Blockchain Integration**: Store file metadata on an Ethereum-compatible private chain, WorldLand (chainId 250407), for integrity verification
-   ✅ **IPFS Storage**: Decentralized storage of document content and embeddings
-   ✅ **Vector Database**: PostgreSQL with pgvector for semantic search capabilities
-   ✅ **AI Chat Interface**: LangChain-powered RAG system for intelligent document interaction
-   ✅ **User Authentication**: Secure login and user-specific document management
-   ✅ **Real-time Interface**: Gradio-based web application with live markdown preview

### Technical Architecture

-   **Frontend**: Gradio web interface with real-time markdown editing and preview
-   **Backend**: FastAPI with SQLAlchemy ORM and PostgreSQL database
-   **AI/ML**: OpenAI embeddings with LangChain for RAG implementation
-   **Blockchain**: Ethereum smart contracts (via Ganache) for metadata storage
-   **Storage**: IPFS for decentralized file and embedding storage
-   **Infrastructure**: Docker Compose for multi-service orchestration

## Problem Definition

Traditional note-taking applications face several critical challenges:

1. **Data Integrity**: No cryptographic proof of document authenticity or tamper detection
2. **Centralized Risk**: Single points of failure and potential censorship
3. **Limited Intelligence**: Lack of AI-powered insights and semantic understanding
4. **Privacy Concerns**: User data controlled by third-party services
5. **Verification Gap**: Difficulty in proving document authenticity and ownership

Sillok addresses these challenges by:

-   Using blockchain for immutable metadata records
-   Leveraging IPFS for decentralized, censorship-resistant storage
-   Implementing AI-powered semantic search and Q&A capabilities
-   Providing cryptographic verification of document integrity
-   Maintaining user sovereignty over their data

## Architecture

![Project Architecture Overview](/images/image.png)

## AI Methods Used

### 1. **Text Embeddings**

-   **Model**: OpenAI `text-embedding-3-large` (3072 dimensions)
-   **Purpose**: Convert document chunks into vector representations for semantic search
-   **Implementation**: LangChain integration with OpenAI embeddings API

### 2. **Retrieval Augmented Generation (RAG)**

-   **Components**:
    -   Vector retriever using pgvector similarity search
    -   Context formatting and prompt engineering
    -   OpenAI GPT-4.1 for response generation
-   **Workflow**: Query → Vector Search → Context Retrieval → LLM Generation

### 3. **Document Processing**

-   **Text Splitting**: LangChain `RecursiveCharacterTextSplitter`
    -   Chunk size: 1000 characters
    -   Overlap: 200 characters
-   **Preprocessing**: Unicode normalization and encoding validation

### 4. **Vector Database**

-   **Storage**: PostgreSQL with pgvector extension
-   **Indexing**: Efficient similarity search using vector indexes
-   **Metadata**: JSON storage for document metadata and relationships

## Technical Implementation

### Smart Contract Integration

```solidity
contract MetaDataStoreContract {
    struct FileMetadata {
        string CID;           // IPFS Content Identifier
        string fileType;      // Document type (markdown, etc.)
        uint256 lastUpdate;   // Timestamp of last modification
        bool isDeleted;       // Soft delete flag
        string userId;        // Document owner identifier
    }

    function storeFileMetadata(...) public;
    function getFileMetadata(string memory _CID) public view returns (...);
}
```

### IPFS Data Structure

```json
{
    "metadata": {
        "fname": "document.md",
        "user_id": "user_hash",
        "last_update": "2025-06-17_10:30:00",
        "is_deleted": false,
        "raw_content_type": "markdown",
        "embeddings": "text-embedding-3-large",
        "text_splitter": "RecursiveCharacterTextSplitter"
    },
    "raw_content": "# Document content...",
    "splits": [{"page_content": "chunk1", "metadata": {...}}],
    "split_ids": ["doc_id-0", "doc_id-1"],
    "vectors": [[0.1, 0.2, ...], [0.3, 0.4, ...]]
}
```

## Achievement

### Successful Implementation

-   ✅ **Full-Stack Integration**: Complete system with frontend, backend, database, blockchain, and storage
-   ✅ **AI-Powered Features**: Working RAG system with semantic search and intelligent Q&A
-   ✅ **Blockchain Verification**: Smart contract deployment and metadata storage on Ethereum
-   ✅ **IPFS Integration**: Decentralized storage with content addressing
-   ✅ **Vector Database**: Efficient similarity search using pgvector
-   ✅ **User Experience**: Intuitive web interface with real-time markdown editing
-   ✅ **Data Integrity**: Cryptographic verification of document authenticity

### Performance Metrics

-   **Embedding Dimension**: 3072 (OpenAI text-embedding-3-large)
-   **Vector Search**: Sub-second similarity search on document collections
-   **Blockchain Transaction**: Metadata storage with transaction hash verification
-   **IPFS Retrieval**: Content-addressed storage with hash-based integrity

## Results

### Functional Achievements

1. **Document Lifecycle Management**: Complete CRUD operations with blockchain/IPFS backing
2. **AI Integration**: Successfully implemented RAG system with context-aware responses
3. **Data Verification**: Cryptographic proof of document integrity and ownership
4. **Decentralized Architecture**: Reduced single points of failure through distributed storage
5. **User-Friendly Interface**: Intuitive web application with markdown editing and preview

### Technical Validation

-   **Smart Contract Deployment**: Verified on local Ethereum network (Ganache)
-   **IPFS Content Addressing**: Documents retrievable via content hash
-   **Vector Similarity**: Semantic search with cosine similarity matching
-   **Database Integrity**: PostgreSQL with vector extension handling embedding storage
-   **API Performance**: FastAPI endpoints with sub-second response times

## Open-source Code Used

### Core Dependencies

-   **[FastAPI](https://fastapi.tiangolo.com/)**: Modern Python web framework for API development
-   **[Gradio](https://gradio.app/)**: Python library for building web interfaces
-   **[LangChain](https://python.langchain.com/)**: Framework for developing LLM applications
-   **[OpenAI API](https://openai.com/api/)**: Text embeddings and language model services
-   **[Web3.py](https://web3py.readthedocs.io/)**: Python library for Ethereum blockchain interaction
-   **[SQLAlchemy](https://sqlalchemy.org/)**: Python ORM for database operations
-   **[pgvector](https://github.com/pgvector/pgvector)**: PostgreSQL extension for vector operations

### Infrastructure

-   **[PostgreSQL](https://postgresql.org/)**: Open-source relational database
-   **[IPFS (Kubo)](https://ipfs.tech/)**: Distributed file system implementation
-   **[Ganache](https://trufflesuite.com/ganache/)**: Personal Ethereum blockchain for development
-   **[Truffle](https://trufflesuite.com/)**: Ethereum development framework
-   **[Docker](https://docker.com/)**: Containerization platform
-   **[NGINX](https://nginx.org/)**: Web server and reverse proxy

## AI Methods We Used

### Development and Implementation Tools

-   **Claude Opus 4 - Extended Thinking Mode**: Most frequently utilized for highly complex coding tasks and debugging processes. Served as the primary development assistant for intricate technical implementations.
-   **Claude Sonnet 4 - Extended Thinking Mode**: Primarily employed for documentation writing, README creation, and technical writing tasks requiring structured and comprehensive content generation.
-   **OpenAI ChatGPT o3 / o4-mini-high / GPT-4.1**: Used as supplementary tools when Claude usage limits were exceeded, providing additional support for development and problem-solving tasks.
-   **Google Gemini & AI Studio Pro 2.5**: Utilized as an alternative solution during the OpenAI ChatGPT service outage that occurred on June 10th, ensuring continuous development progress.
-   **OpenAI Codex**: Experimentally integrated alongside Claude Opus 4 for complex debugging scenarios and advanced coding challenges, providing additional code analysis and generation capabilities.

### Usage Strategy

Our development approach leveraged multiple AI assistants strategically, with Claude models serving as primary tools for their superior reasoning capabilities in extended thinking mode, while maintaining backup options through OpenAI and Google services to ensure uninterrupted development workflow during service limitations or outages.

## Quick-start Guide

### Prerequisites

-   Docker and Docker Compose
-   OpenAI API key
-   8GB+ RAM recommended

### Environment Setup

#### **1. Clone the repository**

```bash
git clone 2025-AIBC/sillok
cd sillok
```

#### **2. Create environment file**

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_api_key_here
```

#### **3. Launch the application**

```bash
docker compose up --build
```

#### **4. WorldLand Setup:** Attach to Container & Manage Accounts

    If you don’t yet have an account, either copy its JSON key file into /workspace/worldland-bcai_{NETWORK_ID}-{CHAIN_ID}/keystore inside the worldland-bcai container, or create a new account instead.
```bash
# Open Other Terminal
docker attach worldland-bcai
eth.accounts; # Check Accounts
admin.datadir # Check workspace of worldland-bcai

# You should remember workspace path when you choose import exist account

## if you want to create the new account
personal.newAccount("your_password");

## else if you want to import exist account
# Open Another Terminal
docker cp PVKEY/PVKEY.json worldland-bcai:/workspace/worldland-bcia_{num}-{num}/keystore

# Finally, Check Accounts
eth.accounts;
```

#### **5. WorldLand Mining:** Mine WLC to fund transactions
```bash
# Set the coinbase (replace the index if you imported/created a different account)
miner.setEtherbase(eth.accounts[0])

# Start a single mining thread
miner.start(1)

# Let it run for ~10 s, then stop
miner.stop()

# Check that the account was credited
eth.getBalance(eth.accounts[0])
```



#### **6. Access the application**

-   **Web Interface**: http://localhost (via NGINX)
-   **Direct Gradio**: http://localhost:7860
-   **API Documentation**: http://localhost:8000/docs
-   **IPFS Gateway**: http://localhost:8080

### Default Credentials

-   **Username**: `admin` / **Password**: `1234`

### Usage Workflow

1. **Login** using provided credentials
2. **Connect** WorldLand and Metamask
3. **Check** Current Block and Connection Status
4. **Create Documents** using the markdown editor
5. **Save to Blockchain** - documents automatically stored on IPFS with metadata on Ethereum
6. **Chat with AI** about your documents using the integrated chatbot
7. **Verify Integrity** - check document authenticity via blockchain records
8. **Manage Files** - view, edit, delete documents with full version history

### Service Architecture

```
Port 80    → NGINX (Reverse Proxy)
Port 7860  → Gradio (Web Interface)
Port 8000  → FastAPI (Backend API)
Port 5432  → PostgreSQL (Database)
Port 8545  → Ganache (Ethereum)
Port 8546  → WorldLand (WorldLand RPC endpoint)
Port 5001  → IPFS (API)
Port 8080  → IPFS (Gateway)
Port 8081  → WebUI (Connects WorldLand to Metamask)
```

### Development

For development with hot reload:

```bash
# API development
cd api && poetry install && poetry run uvicorn main:app --reload

# Frontend development
cd app && poetry install && poetry run gradio main.py
```

### Testing (unstable)

```bash
# Run integration tests
poetry install
poetry run pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Contributing

This project was developed as an academic research project. For questions or collaboration opportunities, please contact the development team.

---

**Note**: This application is designed for educational and research purposes. For production use, additional security measures and optimizations would be required.
