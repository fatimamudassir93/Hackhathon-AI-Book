#!/usr/bin/env python3
"""
Test script for embedding search and retrieval
Demonstrates vector similarity search in Qdrant
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

def test_embedding_search(query: str, top_k: int = 3):
    """
    Test embedding-based search for a given query

    Args:
        query: Search query text
        top_k: Number of results to return
    """
    print(f"\n{'='*70}")
    print(f"Query: \"{query}\"")
    print(f"{'='*70}\n")

    # Initialize Qdrant client
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_HOST", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    # Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate query embedding
    query_vector = model.encode(query).tolist()
    print(f"[OK] Query embedded (dimension: {len(query_vector)})\n")

    # Search in Qdrant
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_book")

    try:
        results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )

        print(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            score = result.score
            payload = result.payload

            # Extract content
            content = payload.get('content', payload.get('text', ''))
            # Clean up frontmatter if present
            if content.startswith('---'):
                parts = content.split('---', 2)
                content = parts[2].strip() if len(parts) > 2 else content

            print(f"Result #{i} (Score: {score:.4f})")
            print(f"  Chapter: {payload.get('chapter', 'N/A')}")
            print(f"  Title: {payload.get('title', 'N/A')}")
            print(f"  Header: {payload.get('header', 'N/A')}")
            print(f"  Source: {payload.get('source', 'N/A')}")
            print(f"  Text Preview:")
            print(f"    {content[:250].replace(chr(10), ' ')}...")
            print()

        return results

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return []


def main():
    """Run test queries"""
    print("\n" + "="*70)
    print("  EMBEDDING SEARCH & RETRIEVAL TEST")
    print("="*70)

    # Test queries covering different topics
    test_queries = [
        "What is embodied intelligence?",
        "How does ROS 2 work?",
        "Explain SLAM algorithms",
        "What are humanoid robots?",
    ]

    for query in test_queries:
        try:
            results = test_embedding_search(query, top_k=3)

            if not results:
                print("[WARNING] No results found for this query\n")

        except KeyboardInterrupt:
            print("\n\n[INFO] Test interrupted by user")
            break
        except Exception as e:
            print(f"[ERROR] Test failed: {e}\n")

    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
