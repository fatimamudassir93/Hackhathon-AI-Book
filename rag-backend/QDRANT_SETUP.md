# Qdrant Cloud Setup Guide

## Overview

This project uses Qdrant Cloud as the vector database for storing and querying textbook content embeddings.

## Prerequisites

- Qdrant Cloud account (free tier available)
- API access credentials

## Setup Steps

### 1. Create Qdrant Cloud Account

1. Visit [https://cloud.qdrant.io](https://cloud.qdrant.io)
2. Sign up for a free account
3. Create a new cluster (free tier: 1GB storage, sufficient for textbook content)

### 2. Get Connection Credentials

1. Navigate to your cluster dashboard
2. Copy the **Cluster URL** (e.g., `https://xxx.qdrant.io`)
3. Generate an **API Key** from the API Keys section
4. Store credentials securely

### 3. Configure Environment Variables

Add to your `.env` file (or copy from `.env.example`):

```bash
QDRANT_HOST=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

### 4. Collection Setup

The ingestion pipeline automatically creates a collection named `physical_ai_book` with:

- **Vector dimensions**: 384 (for all-MiniLM-L6-v2 embeddings)
- **Distance metric**: COSINE
- **Metadata fields**:
  - `chapter`: Chapter number/title
  - `section`: Section title
  - `subsection`: Subsection title
  - `source`: File path
  - `content`: Original text chunk

### 5. Verify Connection

Test your Qdrant connection:

```python
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Test connection
collections = client.get_collections()
print(f"Connected! Collections: {collections}")
```

## Collection Management

### View Collection Info

```python
info = client.get_collection("physical_ai_book")
print(f"Vectors: {info.vectors_count}")
print(f"Points: {info.points_count}")
```

### Delete Collection (if needed)

```python
client.delete_collection("physical_ai_book")
```

### Recreate Collection

The ingestion pipeline handles this automatically, but you can manually recreate:

```python
from qdrant_client.http import models

client.recreate_collection(
    collection_name="physical_ai_book",
    vectors_config=models.VectorParams(
        size=384,
        distance=models.Distance.COSINE
    ),
)
```

## Troubleshooting

### Connection Errors

- **Invalid API Key**: Check your `.env` file for correct API key
- **Network Issues**: Ensure firewall allows HTTPS connections
- **Quota Exceeded**: Check your free tier limits (1GB storage)

### Collection Not Found

- Run the ingestion pipeline to create the collection
- Verify collection name is exactly `physical_ai_book`

### Slow Queries

- Free tier has rate limits (100 requests/second)
- Consider upgrading for production workloads
- Optimize vector dimensions if needed

## Production Considerations

For production deployments:

1. **Upgrade to paid tier** for:
   - Higher storage limits
   - Better performance
   - SLA guarantees

2. **Enable backups**:
   - Qdrant Cloud offers automated backups
   - Configure backup schedule in dashboard

3. **Monitor usage**:
   - Track storage consumption
   - Monitor query latency
   - Set up alerts for quota limits

4. **Security**:
   - Rotate API keys regularly
   - Use environment variables, never commit keys
   - Restrict API key permissions if possible

## Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud Console](https://cloud.qdrant.io)
- [Python Client Docs](https://github.com/qdrant/qdrant-client)
