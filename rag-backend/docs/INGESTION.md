# Physical AI Book - Content Ingestion Guide

This guide explains how to set up and run the content ingestion pipeline for the Physical AI & Humanoid Robotics textbook.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Running Ingestion](#running-ingestion)
4. [Incremental Ingestion](#incremental-ingestion)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

Before running the ingestion pipeline, ensure you have:

- Python 3.8 or higher
- Access to Qdrant Cloud (or local Qdrant instance)
- Textbook content in the `physical-ai-book/docs/` directory in markdown format
- Proper API keys configured in environment variables

### Required Environment Variables

Create a `.env` file in the `rag-backend/` directory with the following variables:

```bash
# Qdrant Configuration
QDRANT_HOST=your-qdrant-host-url
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=physical_ai_book

# API Keys
GROQ_API_KEY=your-groq-api-key
COHERE_API_KEY=your-cohere-api-key
EMBEDDING_MODEL=embed-english-v3.0

# Directories
DOCS_DIRECTORY=../physical-ai-book/docs
```

### Required Dependencies

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. **Set up Qdrant Collection**
   ```bash
   python run_ingestion.py --setup-only
   ```

2. **Verify Environment Variables**
   Make sure your `.env` file contains all the required variables listed above.

3. **Prepare Documentation Directory**
   Ensure your textbook content exists in `physical-ai-book/docs/` in markdown format.

## Running Ingestion

### Basic Ingestion

To run a full ingestion of all textbook content:

```bash
python run_ingestion.py
```

### Force Re-indexing

To force re-indexing of all files (even unchanged ones):

```bash
python run_ingestion.py --force
```

### Specify Custom Directory

To specify a custom directory for ingestion:

```bash
python run_ingestion.py --docs /path/to/your/docs
```

### Verbose Output

To run with verbose logging:

```bash
python run_ingestion.py --verbose
```

## Incremental Ingestion

The system supports incremental ingestion to efficiently update only changed content and remove orphaned embeddings.

### Run Incremental Ingestion

```bash
python run_ingestion.py --incremental
```

This will:
- Only process files that have changed since the last ingestion
- Remove embeddings for deleted or moved files
- Update embeddings for modified files
- Preserve unchanged content

### Dry Run

To see what would be processed without making changes:

```bash
python run_ingestion.py --dry-run
```

To see what would be processed with incremental analysis:

```bash
python run_ingestion.py --dry-run --incremental
```

## Understanding the Ingestion Process

The ingestion pipeline consists of several stages:

1. **Scanning**: Discovers markdown files in the docs directory
2. **Parsing**: Extracts chapter/section structure and metadata
3. **Chunking**: Splits content into semantically meaningful chunks
4. **Embedding**: Generates vector embeddings for each chunk
5. **Uploading**: Stores vectors in Qdrant with metadata
6. **Caching**: Maintains hash cache to prevent duplication

### Deduplication

The system uses content hashing to prevent duplicate embeddings during re-ingestion. It maintains a cache file (`.ingestion_cache.json`) that tracks the hash of each file.

### Orphan Detection

When running in incremental mode, the system detects and removes embeddings for files that no longer exist in the source directory.

## Troubleshooting

### Common Issues

#### Qdrant Connection Errors
- Verify your `QDRANT_HOST` and `QDRANT_API_KEY` are correct
- Check that your Qdrant instance is accessible
- Ensure the Qdrant collection exists or run setup command

#### API Rate Limits
- The system uses API keys that may have rate limits
- Consider implementing backoff strategies for large ingests
- Check your API provider's usage limits

#### File Permissions
- Ensure the script has read access to the docs directory
- Check that you have write permissions for cache files

#### Large File Issues
- Very large markdown files may cause memory issues
- Consider splitting large files into smaller sections

### Error Recovery

If ingestion fails partway through:
1. Check the log file for specific error details
2. Address the underlying issue (API keys, connectivity, permissions)
3. Run with `--force` flag to restart the entire process

## Performance Optimization

### Chunking Parameters
The default chunk size is 1000 characters with 200-character overlap. You can modify these in the ingestion pipeline for better retrieval performance.

### Batch Sizes
- Embedding batch size: Controls how many chunks are processed together
- Upload batch size: Controls how many vectors are uploaded together
- Adjust these based on your API limits and performance needs

### Monitoring
Use the ingestion status endpoint to monitor the progress:
```
GET /api/ingestion/status
```

## Monitoring and Validation

### Check Ingestion Status
```bash
curl http://localhost:8000/api/ingestion/status
```

### Verify Content
After ingestion, test the chat endpoint to ensure content is properly indexed:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is embodied intelligence?"}'
```

## Best Practices

1. **Regular Incremental Updates**: Use incremental mode for regular updates to improve performance
2. **Backup Cache File**: The `.ingestion_cache.json` file is important for deduplication
3. **Monitor API Usage**: Keep track of API key usage to avoid unexpected limits
4. **Validate Content**: Regularly verify that ingested content is correctly retrievable
5. **Clean Up Orphans**: Regular incremental runs help maintain data quality by removing orphaned embeddings