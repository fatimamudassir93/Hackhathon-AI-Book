"""
Qdrant uploader for storing vectors with metadata
Handles batch uploads to Qdrant Cloud
"""
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_setup import get_qdrant_client, COLLECTION_NAME


class QdrantUploader:
    """
    Uploads vector embeddings with metadata to Qdrant Cloud.
    """

    def __init__(self, collection_name: str = COLLECTION_NAME):
        """
        Initialize the Qdrant uploader.

        Args:
            collection_name: Name of the Qdrant collection
        """
        self.client = get_qdrant_client()
        self.collection_name = collection_name
        self.stats = {
            "uploaded": 0,
            "batches": 0,
            "errors": 0
        }

    def upload_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> bool:
        """
        Upload chunks with embeddings to Qdrant.

        Args:
            chunks: List of chunk dicts with 'embedding', 'content', and 'metadata'
            batch_size: Number of points to upload per batch
            show_progress: Whether to print progress

        Returns:
            True if all uploads successful, False otherwise
        """
        total = len(chunks)
        success = True

        if show_progress:
            print(f"Uploading {total} vectors to Qdrant...")

        # Process in batches
        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            if show_progress:
                print(f"  Batch {batch_num}/{total_batches}: {len(batch)} points", end='')

            try:
                points = self._create_points(batch)
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                self.stats["uploaded"] += len(batch)
                self.stats["batches"] += 1

                if show_progress:
                    print(" [OK]")

            except Exception as e:
                self.stats["errors"] += len(batch)
                success = False
                if show_progress:
                    print(f" [ERROR] {e}")

        if show_progress:
            if success:
                print(f"[OK] Successfully uploaded {self.stats['uploaded']} vectors")
            else:
                print(f"[WARNING] Uploaded {self.stats['uploaded']} vectors with {self.stats['errors']} errors")

        return success

    def _create_points(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[rest.PointStruct]:
        """
        Convert chunks to Qdrant points.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of PointStruct objects
        """
        points = []

        for chunk in chunks:
            # Generate unique ID
            point_id = str(uuid.uuid4())

            # Extract vector
            vector = chunk.get('embedding')
            if not vector:
                raise ValueError(f"Chunk missing embedding: {chunk.get('metadata', {}).get('source', 'unknown')}")

            # Prepare payload (metadata + content)
            payload = {
                **chunk.get('metadata', {}),
                "content": chunk.get('content', ''),
            }

            # Remove any numpy types or non-serializable data
            payload = self._sanitize_payload(payload)

            # Create point
            point = rest.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
            points.append(point)

        return points

    def _sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize payload to ensure JSON serializability.

        Args:
            payload: Raw payload dictionary

        Returns:
            Sanitized payload
        """
        sanitized = {}

        for key, value in payload.items():
            # Convert list values to strings if needed
            if isinstance(value, list):
                # Keep breadcrumbs as lists
                if key == 'breadcrumb':
                    sanitized[key] = [str(item) for item in value]
                else:
                    sanitized[key] = str(value)
            # Convert other types
            elif isinstance(value, (str, int, float, bool, type(None))):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)

        return sanitized

    def delete_by_source(self, source_path: str) -> int:
        """
        Delete all points from a specific source.

        Args:
            source_path: Source file path to delete

        Returns:
            Number of points deleted
        """
        # Use scroll to find points with matching source
        # Then delete them (Qdrant doesn't support direct filter delete in all versions)
        # For now, we'll use collection recreation as the safest method

        print(f"Warning: delete_by_source not fully implemented. Consider recreating collection.")
        return 0

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the Qdrant collection.

        Returns:
            Dictionary with collection stats
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_stats(self) -> Dict[str, int]:
        """Get upload statistics"""
        return self.stats.copy()


def upload_to_qdrant(
    chunks: List[Dict[str, Any]],
    batch_size: int = 100,
    show_progress: bool = True
) -> bool:
    """
    Convenience function to upload chunks to Qdrant.

    Args:
        chunks: List of chunks with embeddings
        batch_size: Upload batch size
        show_progress: Whether to show progress

    Returns:
        True if successful
    """
    uploader = QdrantUploader()
    return uploader.upload_chunks(chunks, batch_size, show_progress)


if __name__ == "__main__":
    # Test requires actual Qdrant connection
    print("Testing Qdrant Uploader")
    print("=" * 60)

    # Create test chunks (with fake embeddings)
    test_chunks = [
        {
            "content": f"Test content {i}",
            "embedding": [0.1 * i] * 384,  # Fake 384-dim embedding
            "metadata": {
                "source": f"test_{i}.md",
                "chapter": "Test Chapter",
                "chunk_index": i
            }
        }
        for i in range(5)
    ]

    try:
        uploader = QdrantUploader()

        # Get collection info
        info = uploader.get_collection_info()
        print(f"Collection info:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Test upload (uncomment to actually upload)
        # success = uploader.upload_chunks(test_chunks, batch_size=2)

        # if success:
        #     stats = uploader.get_stats()
        #     print(f"\nUpload stats:")
        #     for key, value in stats.items():
        #         print(f"  {key}: {value}")

        print("\n[OK] Uploader initialized successfully")
        print("  (Uncomment test upload code to actually upload)")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("  Make sure Qdrant is configured and accessible")
