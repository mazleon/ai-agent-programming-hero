# Gemini AI Chatbot

![Gemini AI Chatbot Cover](res/cover_photo.jpeg)

A powerful chatbot application powered by Google's Agent Development Kit (ADK), featuring multiple specialized agents for different domains.

## Features

- **Weather Agent**: Provides current weather information and time for various cities.
- **Phone Shop Agent**: A comprehensive phone shop assistant with RAG capabilities that can:
  - Provide phone specifications, prices, and comparisons
  - Answer warranty policy questions using document retrieval
  - Help with replacement and return procedures
  - Provide customer support information
  - Search through all store policies and procedures

## Installation Process

1. **Create Virtual Environment**:
   You can use Python's built-in venv or uv for managing the virtual environment:

   ```bash
   python -m venv .venv
   ```

   or

   ```bash
   uv venv
   ```

2. **Activate Virtual Environment**:

   ```bash
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**:
   Install the core dependencies:

   ```bash
   uv pip install -r requirements.txt
   ```

   **For Full RAG Capabilities (Optional):**

   ```bash
   uv pip install chromadb sentence-transformers
   ```

   **Note:** If you skip the optional extras, the agent automatically falls back to keyword search over the markdown policy files—so it still answers policy questions without ChromaDB.

4. **Prime the RAG Store (Recommended):**

   ```bash
   python setup_rag.py
   ```

   This script builds the `chroma_db/` directory, loads all policy documents, and verifies retrieval before you start answering questions.

## Project Structure

```
gemini-ai-bot/
├── src/
│   ├── phone_shop_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                 # Main phone shop agent configuration
│   │   ├── .env                     # Environment variables
│   │   ├── data/
│   │   │   ├── phone_specifications.json    # Phone data with specs and prices
│   │   │   ├── warranty_policy.md           # Warranty policy document
│   │   │   ├── replacement_policy.md        # Replacement policy document
│   │   │   └── customer_support_faq.md      # Customer support FAQ
│   │   ├── rag/                     # RAG (Retrieval-Augmented Generation) module
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # ChromaDB vector store implementation
│   │   │   └── retriever.py         # RAG retrieval tools for ADK
│   │   └── tools/
│   │       └── tool.py              # Tool functions for phone queries and RAG
│   └── weather_agent/
│       ├── __init__.py
│       ├── agent.py                 # Weather agent configuration
│       └── .env
├── chroma_db/                       # ChromaDB persistence directory (auto-created)
├── requirements.txt                 # Python dependencies
├── pyproject.toml                   # Project configuration
├── uv.lock                          # Dependency lock file
└── README.md
```

## Running the Agents

Navigate to the `src` directory and run the desired agent:

### Phone Shop Agent (Enhanced with RAG)

```bash
cd src
adk run phone_shop_agent
```

This agent now includes RAG (Retrieval-Augmented Generation) capabilities and can:

**Phone Information:**
- Get phone prices by model name
- Retrieve detailed specifications
- List all available phones
- Compare specifications between two phones

**Policy & Support (RAG-powered):**
- Answer warranty questions using document retrieval
- Provide replacement and return policy information
- Help with customer support inquiries
- Search through all store policies and procedures

**Example queries:**

*Phone Information:*
- "What's the price of Samsung Galaxy S23?"
- "Tell me the specs of iPhone 15"
- "What phones do you have?"
- "Compare Google Pixel 8 and OnePlus 12"

*Warranty & Policy (RAG):*
- "How long is the warranty on new phones?"
- "What's covered under warranty?"
- "Can I return my phone if I don't like it?"
- "How do I contact customer support?"
- "What are your store hours?"
- "Do you offer extended warranty?"

### Weather Agent
```bash
cd src
adk run weather_agent
```

Provides weather and time information for cities.

## RAG (Retrieval-Augmented Generation) Setup

The phone shop agent now includes RAG capabilities for intelligent document retrieval. Here's how it works:

### Automatic Setup

The RAG system automatically initializes when you first run the phone shop agent:

1. **Vector Database**: ChromaDB creates a persistent vector store in the `chroma_db/` directory
2. **Document Loading**: Policy documents are automatically chunked and embedded
3. **Ready to Use**: The agent can immediately answer policy-related questions

### Manual RAG Operations

If you need to manually manage or debug the RAG system:

```bash
# Navigate to the repository root
python setup_rag.py                 # Rebuild embeddings and verify search (optional)

# Run vector-store diagnostics from src/
cd src
python -m phone_shop_agent.rag.vector_store
python -m phone_shop_agent.rag.retriever

# Alternatively with uv
uv run -m phone_shop_agent.rag.retriever
```

### Adding New Policy Documents

To add new policy documents to the RAG system:

1. **Add Document**: Place new `.md` files in `src/phone_shop_agent/data/`
2. **Restart Agent**: The system will automatically detect and index new documents
3. **Verify**: Ask the agent questions about the new content

### RAG Architecture

- **Vector Store**: ChromaDB with cosine similarity
- **Embeddings**: Default sentence transformers model
- **Chunking**: 500 characters with 50-character overlap
- **Retrieval**: Top-K similarity search with relevance scoring

### Troubleshooting RAG

**Issue**: Agent can't find policy information
**Solution**: 
```bash
# Delete and recreate the vector database
rm -rf chroma_db/
# Restart the agent to rebuild the index
```

**Issue**: New documents not being indexed
**Solution**: Ensure documents are in `.md` format in the `data/` directory

## Configuration

Each agent has its own `.env` file for configuration. Make sure to set up any required API keys or environment variables there.

### Environment Variables

For the phone shop agent with RAG:
- No additional environment variables required
- ChromaDB runs locally without external dependencies
- All policy documents are included in the repository

## Step-by-Step Usage Guide

### 1. First Time Setup

```bash
# Clone and navigate to project
cd gemini-ai-bot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
python setup_rag.py  # optional but recommended
```

### 2. Run the Enhanced Phone Shop Agent

```bash
cd src
adk run phone_shop_agent
```

### 3. Test RAG Capabilities

Try these example conversations:

**Warranty Questions:**
```
User: "How long is the warranty on new phones?"
Agent: [Retrieves and provides warranty period information]

User: "What's covered under warranty?"
Agent: [Lists covered items from warranty policy]
```

**Replacement Policy:**
```
User: "Can I return my phone?"
Agent: [Provides return policy details]

User: "What's the return window?"
Agent: [Explains return timeframes]
```

**Customer Support:**
```
User: "How do I contact support?"
Agent: [Provides contact information]

User: "What are your store hours?"
Agent: [Lists store hours and locations]
```

### 4. Monitor RAG Performance

The agent logs whether responses came from vector search or fallback keyword search. Look for `phone_shop_agent.rag.retriever` messages indicating:
- Documents successfully loaded into the vector store
- Vector results found vs. fallback keyword results
- Relevance scores for each returned policy chunk

If the logs mention fallback usage unexpectedly, rerun `python setup_rag.py` to rebuild embeddings.

## Contributing

This project uses the Agent Development Kit for building modular AI agents. The RAG system is built with ChromaDB and integrates seamlessly with ADK's tool system.

### Adding New RAG Features

1. **New Document Types**: Add documents to `data/` directory
2. **Custom Retrievers**: Extend classes in `rag/retriever.py`
3. **Enhanced Chunking**: Modify `rag/vector_store.py`
4. **New Tools**: Add RAG-powered functions to `tools/tool.py`
