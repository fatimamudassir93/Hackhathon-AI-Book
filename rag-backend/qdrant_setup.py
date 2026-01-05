"""
Qdrant Cloud connection and collection setup
Configures the vector database for Physical AI textbook content
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

COLLECTION_NAME = "physical_ai_book"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding dimensions

def get_qdrant_client():
    """
    Create and return a configured Qdrant client.
    Uses environment variables for connection details.
    """
    client = QdrantClient(
        url=os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY"),
        prefer_grpc=False
    )
    return client

def create_qdrant_collection(force_recreate=False):
    """
    Create the Qdrant collection for textbook content.

    Args:
        force_recreate: If True, deletes existing collection before creating

    Collection schema:
        - Vector size: 384 (all-MiniLM-L6-v2)
        - Distance: COSINE
        - Metadata fields:
            - chapter: str (e.g., "Chapter 1", "Chapter 2")
            - title: str (chapter title)
            - section: str (section heading)
            - subsection: str (subsection heading, optional)
            - source: str (file path)
            - content: str (original text chunk)
            - chunk_index: int (position in document)
    """
    client = get_qdrant_client()

    try:
        # Check if collection exists
        existing = client.get_collection(COLLECTION_NAME)
        if force_recreate:
            print(f"Collection '{COLLECTION_NAME}' exists. Deleting for recreate...")
            client.delete_collection(COLLECTION_NAME)
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists with {existing.points_count} points")
            return client
    except Exception:
        print(f"Collection '{COLLECTION_NAME}' does not exist. Creating...")

    # Create collection with correct vector dimensions
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
    )

    print(f"[OK] Qdrant collection '{COLLECTION_NAME}' created successfully")
    print(f"  - Vector size: {VECTOR_SIZE}")
    print(f"  - Distance metric: COSINE")
    print(f"  - Ready for ingestion")

    return client

if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "-f" in sys.argv
    create_qdrant_collection(force_recreate=force)
