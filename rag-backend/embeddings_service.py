"""
Embeddings service wrapper for OpenAI-compatible models
Provides a unified interface for generating text embeddings
"""
import os
from typing import List, Union
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class EmbeddingsService:
    """
    Wrapper for embedding generation using local or API-based models.
    Defaults to HuggingFace sentence-transformers for local generation.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embeddings service.

        Args:
            model_name: Name of the embedding model to use.
                       Default: 'all-MiniLM-L6-v2' (384 dimensions, fast, local)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the embedding model (lazy loading)"""
        print(f"Loading embedding model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"[OK] Model loaded. Embedding dimensions: {self.embedding_dim}")

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not self.model:
            self._initialize_model()

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors (one per input text)
        """
        if not self.model:
            self._initialize_model()

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    def get_dimensions(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            Integer representing embedding dimensions (e.g., 384 for all-MiniLM-L6-v2)
        """
        if not self.embedding_dim:
            self._initialize_model()
        return self.embedding_dim


# Singleton instance for reuse across modules
_embeddings_service = None

def get_embeddings_service(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingsService:
    """
    Get or create a singleton embeddings service instance.

    Args:
        model_name: Name of the embedding model (default: all-MiniLM-L6-v2)

    Returns:
        EmbeddingsService instance
    """
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService(model_name=model_name)
    return _embeddings_service


if __name__ == "__main__":
    # Test the embeddings service
    service = get_embeddings_service()

    # Test single embedding
    text = "This is a test of the embeddings service."
    embedding = service.embed_text(text)
    print(f"\nSingle embedding test:")
    print(f"Input: {text}")
    print(f"Output dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch embedding
    texts = [
        "Physical AI combines embodied intelligence with robotics.",
        "Humanoid robots require complex control systems.",
        "ROS 2 is a popular framework for robot development."
    ]
    embeddings = service.embed_batch(texts)
    print(f"\nBatch embedding test:")
    print(f"Input: {len(texts)} texts")
    print(f"Output: {len(embeddings)} embeddings")
    print(f"Each embedding has {len(embeddings[0])} dimensions")
