"""
Vector search service for RAG retrieval
Implements similarity search with threshold and top-k retrieval
"""
from typing import List, Dict, Any, Optional
from qdrant_client.http import models as rest
from qdrant_setup import get_qdrant_client, COLLECTION_NAME
from embeddings_service import get_embeddings_service


class VectorSearchService:
    """
    Service for searching vectors in Qdrant with configurable parameters.
    """

    def __init__(
        self,
        collection_name: str = COLLECTION_NAME,
        similarity_threshold: float = 0.5,
        top_k: int = 5
    ):
        """
        Initialize the vector search service.

        Args:
            collection_name: Name of Qdrant collection
            similarity_threshold: Minimum similarity score (0-1, higher = more similar)
            top_k: Maximum number of results to return
        """
        self.client = get_qdrant_client()
        self.collection_name = collection_name
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        self.embeddings_service = get_embeddings_service()

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_conditions: Optional[rest.Filter] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query: User's question or search query
            top_k: Override default top_k
            similarity_threshold: Override default similarity threshold
            filter_conditions: Optional Qdrant filter for metadata

        Returns:
            List of search results with payload and score
        """
        # Use defaults if not provided
        k = top_k if top_k is not None else self.top_k
        threshold = similarity_threshold if similarity_threshold is not None else self.similarity_threshold

        # Generate query embedding
        query_vector = self.embeddings_service.embed_text(query)

        # Search in Qdrant
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter_conditions,
            limit=k,
            score_threshold=threshold,
            with_payload=True,
            with_vectors=False
        )

        # Format results
        results = []
        for hit in search_results:
            result = {
                'score': hit.score,
                'content': hit.payload.get('content', ''),
                'source': hit.payload.get('source', ''),
                'chapter': hit.payload.get('chapter', ''),
                'title': hit.payload.get('title', ''),
                'section': hit.payload.get('section', ''),
                'subsection': hit.payload.get('subsection', ''),
                'chapter_number': hit.payload.get('chapter_number'),
                'header': hit.payload.get('header', ''),
                'breadcrumb': hit.payload.get('breadcrumb', []),
                'metadata': hit.payload
            }
            results.append(result)

        return results

    def search_by_chapter(
        self,
        query: str,
        chapter: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search within a specific chapter.

        Args:
            query: User's question
            chapter: Chapter name or number (e.g., "Chapter 1" or "1")
            top_k: Number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of search results from the specified chapter
        """
        # Create filter for chapter
        chapter_filter = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="chapter",
                    match=rest.MatchValue(value=chapter)
                )
            ]
        )

        return self.search(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filter_conditions=chapter_filter
        )

    def search_with_metadata_filter(
        self,
        query: str,
        metadata_filters: Dict[str, Any],
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with custom metadata filters.

        Args:
            query: User's question
            metadata_filters: Dictionary of field -> value filters
            top_k: Number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of filtered search results
        """
        # Build filter conditions
        conditions = []
        for field, value in metadata_filters.items():
            conditions.append(
                rest.FieldCondition(
                    key=field,
                    match=rest.MatchValue(value=value)
                )
            )

        filter_obj = rest.Filter(must=conditions) if conditions else None

        return self.search(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filter_conditions=filter_obj
        )

    def search_with_selected_text(
        self,
        query: str,
        selected_text: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with selected text context, boosting relevance for related results.

        Args:
            query: User's question
            selected_text: Text selected by user for context
            top_k: Number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of search results with boosted scores
        """
        # Perform regular search
        results = self.search(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )

        # Boost scores based on selected text relevance
        selected_keywords = set(selected_text.lower().split())

        boosted_results = []
        for result in results:
            content = result.get('content', '')
            content_keywords = set(content.lower().split())

            # Calculate keyword overlap
            overlap = len(selected_keywords & content_keywords)
            overlap_ratio = overlap / max(len(selected_keywords), 1)

            # Boost score by overlap ratio (up to 20% boost)
            boost_factor = 1.0 + (overlap_ratio * 0.2)
            original_score = result['score']
            boosted_score = min(original_score * boost_factor, 1.0)

            boosted_result = {
                **result,
                'original_score': original_score,
                'score': boosted_score,
                'boost_factor': boost_factor,
                'has_selected_text_context': True
            }

            boosted_results.append(boosted_result)

        # Re-sort by boosted score
        boosted_results.sort(key=lambda x: x['score'], reverse=True)

        return boosted_results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the search service.

        Returns:
            Dictionary with service configuration
        """
        return {
            'collection_name': self.collection_name,
            'similarity_threshold': self.similarity_threshold,
            'top_k': self.top_k,
            'embedding_dimensions': self.embeddings_service.embedding_dim
        }


def create_vector_search_service(
    similarity_threshold: float = 0.5,
    top_k: int = 5
) -> VectorSearchService:
    """
    Factory function to create a vector search service.

    Args:
        similarity_threshold: Minimum similarity score
        top_k: Maximum results to return

    Returns:
        Configured VectorSearchService instance
    """
    return VectorSearchService(
        similarity_threshold=similarity_threshold,
        top_k=top_k
    )


# Example usage
if __name__ == "__main__":
    # Create service
    search_service = create_vector_search_service(
        similarity_threshold=0.5,
        top_k=3
    )

    # Test search
    query = "What is embodied intelligence?"
    print(f"Searching for: '{query}'")
    print(f"Config: {search_service.get_stats()}\n")

    results = search_service.search(query)

    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"Result {i} (score: {result['score']:.4f}):")
        print(f"  Chapter: {result['chapter']}")
        print(f"  Header: {result['header']}")
        print(f"  Content: {result['content'][:150]}...")
        print()
