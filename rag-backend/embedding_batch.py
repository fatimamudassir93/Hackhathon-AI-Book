"""
Batch embedding generation with rate limiting and error handling
Processes chunks in batches for efficient embedding creation
"""
import time
from typing import List, Dict, Any, Optional
from embeddings_service import get_embeddings_service, EmbeddingsService


class EmbeddingBatchProcessor:
    """
    Processes text chunks in batches to generate embeddings efficiently.
    Includes rate limiting and error handling.
    """

    def __init__(
        self,
        batch_size: int = 32,
        rate_limit_delay: float = 0.1,
        max_retries: int = 3,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the batch processor.

        Args:
            batch_size: Number of texts to process per batch
            rate_limit_delay: Seconds to wait between batches
            max_retries: Maximum retry attempts for failed batches
            model_name: Embedding model name
        """
        self.batch_size = batch_size
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.embeddings_service = get_embeddings_service(model_name=model_name)

        self.stats = {
            "total_processed": 0,
            "batches_processed": 0,
            "errors": 0,
            "retries": 0
        }

    def process_chunks(
        self,
        chunks: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Process chunks and add embeddings.

        Args:
            chunks: List of chunk dictionaries with 'content' key
            show_progress: Whether to print progress

        Returns:
            List of chunks with added 'embedding' key
        """
        total = len(chunks)
        results = []

        if show_progress:
            print(f"Generating embeddings for {total} chunks...")

        # Process in batches
        for i in range(0, total, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total + self.batch_size - 1) // self.batch_size

            if show_progress:
                print(f"  Batch {batch_num}/{total_batches}: {len(batch)} chunks", end='')

            # Extract texts
            texts = [chunk['content'] for chunk in batch]

            # Generate embeddings with retry
            embeddings = self._generate_with_retry(texts)

            if embeddings:
                # Add embeddings to chunks
                for chunk, embedding in zip(batch, embeddings):
                    chunk['embedding'] = embedding
                    results.append(chunk)

                self.stats["batches_processed"] += 1
                self.stats["total_processed"] += len(batch)

                if show_progress:
                    print(" [OK]")
            else:
                if show_progress:
                    print(" [FAILED]")
                self.stats["errors"] += len(batch)

            # Rate limiting
            if i + self.batch_size < total:
                time.sleep(self.rate_limit_delay)

        if show_progress:
            print(f"[OK] Generated {self.stats['total_processed']} embeddings")
            if self.stats['errors'] > 0:
                print(f"  [WARNING] {self.stats['errors']} failed")

        return results

    def _generate_with_retry(
        self,
        texts: List[str]
    ) -> Optional[List[List[float]]]:
        """
        Generate embeddings with retry logic.

        Args:
            texts: List of text strings

        Returns:
            List of embeddings or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                embeddings = self.embeddings_service.embed_batch(
                    texts,
                    batch_size=len(texts)
                )
                return embeddings

            except Exception as e:
                self.stats["retries"] += 1
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                else:
                    print(f"    Error after {self.max_retries} attempts: {e}")
                    return None

        return None

    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_processed": 0,
            "batches_processed": 0,
            "errors": 0,
            "retries": 0
        }


def generate_embeddings_for_chunks(
    chunks: List[Dict[str, Any]],
    batch_size: int = 32,
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate embeddings for chunks.

    Args:
        chunks: List of chunk dictionaries
        batch_size: Batch size for processing
        show_progress: Whether to show progress

    Returns:
        Chunks with embeddings added
    """
    processor = EmbeddingBatchProcessor(batch_size=batch_size)
    return processor.process_chunks(chunks, show_progress=show_progress)


if __name__ == "__main__":
    # Test the batch processor
    test_chunks = [
        {"content": f"This is test chunk number {i}. It contains sample text for testing the embedding batch processor."}
        for i in range(10)
    ]

    print("Testing Embedding Batch Processor")
    print("=" * 60)

    processor = EmbeddingBatchProcessor(batch_size=3)
    result_chunks = processor.process_chunks(test_chunks)

    print(f"\nResults:")
    print(f"  Input chunks: {len(test_chunks)}")
    print(f"  Output chunks: {len(result_chunks)}")
    print(f"  Embedding dimensions: {len(result_chunks[0]['embedding']) if result_chunks else 0}")

    stats = processor.get_stats()
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Show sample embedding
    if result_chunks:
        print(f"\nSample embedding (first 5 values):")
        print(f"  {result_chunks[0]['embedding'][:5]}")
