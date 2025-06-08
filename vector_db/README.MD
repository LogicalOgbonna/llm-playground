# Vector Database API

A FastAPI-based vector database service that provides document embedding and similarity search capabilities using Ollama's `nomic-embed-text` model and ChromaDB for storage.

## Features

- **Document Embedding**: Upload and process PDF documents into vector embeddings
- **Similarity Search**: Query documents using natural language with metadata filtering
- **Background Processing**: Non-blocking document processing using FastAPI background tasks
- **Metadata Filtering**: Role-based access control with user permission filters
- **RESTful API**: Clean REST endpoints for embedding and searching operations

## Architecture

- **FastAPI**: Modern web framework for building APIs
- **ChromaDB**: Vector database for storing and querying embeddings
- **Ollama**: Local LLM service for generating embeddings using `nomic-embed-text`
- **LangChain**: Framework for working with language models and document processing

## Prerequisites

Before setting up this project, you need to install and configure the following:

### 1. Install Ollama

Ollama is a tool for running large language models locally.

#### macOS (using Homebrew)
```bash
brew install ollama
```

#### macOS/Linux (using curl)
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download the installer from [https://ollama.ai/download](https://ollama.ai/download)

### 2. Start Ollama Service

```bash
# Start Ollama service (runs in background)
ollama serve
```

### 3. Install nomic-embed-text Model

```bash
# Pull the embedding model
ollama pull nomic-embed-text
```

Verify the installation:
```bash
# List installed models
ollama list
```

You should see `nomic-embed-text` in the list.

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:LogicalOgbonna/llm-playground.git
cd llm
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Server Configuration
PORT=5002
env=development

# Ollama Configuration
OPENAI_API_URL=http://localhost:11434
```

**Environment Variables:**
- `PORT`: The port on which the FastAPI server will run (default: 5002)
- `env`: Environment mode (`development` or `production`)
- `OPENAI_API_URL`: Ollama server URL (default: http://localhost:11434)

### 5. Prepare Document Directory

Create a `data` directory in the `vector_db` folder and add your PDF documents:

```bash
mkdir vector_db/data
# Copy your PDF files to vector_db/data/
```

## Usage

### 1. Start the Server

```bash
cd vector_db
python main.py
```

The server will start at `http://localhost:5002` (or your configured port).

### 2. API Endpoints

#### Embed Documents
Upload and process PDF documents into vector embeddings.

```bash
POST /api/embed
```

**Request Body:**
```json
{
  "index_name": "my_documents",
  "chunk_size": 400,
  "chunk_overlap": 40
}
```

**Parameters:**
- `index_name`: Name of the collection/index to store embeddings
- `chunk_size`: Size of text chunks (default: 400)
- `chunk_overlap`: Overlap between chunks (default: 40)

**Example:**
```bash
curl -X POST "http://localhost:5002/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "index_name": "research_papers",
    "chunk_size": 500,
    "chunk_overlap": 50
  }'
```

#### Search Documents
Perform similarity search on embedded documents.

```bash
POST /api/search
```

**Request Body:**
```json
{
  "query": "What is machine learning?",
  "index_name": "my_documents",
  "k": 5
}
```

**Parameters:**
- `query`: Natural language search query
- `index_name`: Name of the collection to search
- `k`: Number of results to return (default: 2)

**Example:**
```bash
curl -X POST "http://localhost:5002/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence applications",
    "index_name": "research_papers",
    "k": 3
  }'
```

### 3. Using the API with Python

```python
import requests

# Embed documents
embed_response = requests.post(
    "http://localhost:5002/api/embed",
    json={
        "index_name": "my_collection",
        "chunk_size": 400,
        "chunk_overlap": 40
    }
)

# Search documents
search_response = requests.post(
    "http://localhost:5002/api/search",
    json={
        "query": "machine learning algorithms",
        "index_name": "my_collection",
        "k": 5
    }
)

results = search_response.json()
print(results)
```


## Development

### Running in Development Mode

Set `env=development` in your `.env` file to enable:
- Auto-reload on code changes
- Detailed logging
- Development-specific configurations

### Adding New Features

1. **New Endpoints**: Add routes in `src/app.py`
2. **Vector Operations**: Extend `src/chroma.py`
3. **Configuration**: Update `src/constants.py`

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   ```
   Error: Connection refused to http://localhost:11434
   ```
   **Solution**: Ensure Ollama service is running (`ollama serve`)

2. **Model Not Found**
   ```
   Error: model 'nomic-embed-text' not found
   ```
   **Solution**: Install the model (`ollama pull nomic-embed-text`)

3. **Port Already in Use**
   ```
   Error: Port 5002 is already in use
   ```
   **Solution**: Change the `PORT` in your `.env` file or stop the conflicting service

4. **No Documents Found**
   ```
   No new valid documents to add
   ```
   **Solution**: Ensure PDF files are in the `vector_db/data/` directory

### Logs and Debugging

- Check server logs for detailed error messages
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Test embeddings: `ollama run nomic-embed-text "test query"`

## Performance Considerations

- **Chunk Size**: Larger chunks (800-1000) for better context, smaller chunks (200-400) for precise matching
- **Batch Processing**: Documents are processed in batches of 100 for memory efficiency
- **Background Tasks**: Embedding operations run asynchronously to avoid blocking the API

## Security

The API includes basic metadata filtering for user permissions:
- `user:editor`, `user:owner`, `user:admin`, etc.
- Documents are filtered based on user roles during search

For production deployment, consider adding:
- Authentication middleware
- Rate limiting
- Input validation
- HTTPS configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request