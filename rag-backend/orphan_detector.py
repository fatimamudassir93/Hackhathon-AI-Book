"""
Orphaned embedding detector
Identifies embeddings whose source files no longer exist
"""
from typing import Set, Dict, Any, List
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()


class OrphanDetector:
    """
    Detects and manages orphaned embeddings whose source files have been deleted.
    """

    def __init__(self, collection_name: str = None):
        """
        Initialize the orphan detector.

        Args:
            collection_name: Qdrant collection name
        """
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "physical_ai_book")

        # Initialize Qdrant client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_HOST"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=30
        )

    def find_orphaned_sources(self, valid_sources: Set[str]) -> Dict[str, Any]:
        """
        Find embeddings whose source files no longer exist.

        Args:
            valid_sources: Set of currently valid source file paths

        Returns:
            Dictionary with orphaned source information
        """
        try:
            # Get all unique sources in the collection
            all_sources_in_collection = set()
            unique_sources = {}

            # Scroll through all points to collect sources
            offset = None
            while True:
                result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=1000,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                points, next_offset = result

                for point in points:
                    source = point.payload.get('source', '')
                    if source:
                        all_sources_in_collection.add(source)
                        if source not in unique_sources:
                            unique_sources[source] = 0
                        unique_sources[source] += 1

                if next_offset is None:
                    break
                offset = next_offset

            # Find orphaned sources (in collection but not in valid sources)
            orphaned_sources = all_sources_in_collection - valid_sources

            return {
                'orphaned_sources': list(orphaned_sources),
                'total_orphaned_sources': len(orphaned_sources),
                'total_orphaned_points': sum(unique_sources.get(src, 0) for src in orphaned_sources),
                'all_sources_in_collection': list(all_sources_in_collection),
                'valid_sources_count': len(valid_sources),
                'orphaned_details': {src: unique_sources[src] for src in orphaned_sources}
            }

        except Exception as e:
            print(f"Error finding orphaned sources: {e}")
            return {
                'orphaned_sources': [],
                'total_orphaned_sources': 0,
                'total_orphaned_points': 0,
                'all_sources_in_collection': [],
                'valid_sources_count': 0,
                'orphaned_details': {},
                'error': str(e)
            }

    def delete_orphaned_embeddings(self, valid_sources: Set[str]) -> Dict[str, Any]:
        """
        Delete embeddings whose source files no longer exist.

        Args:
            valid_sources: Set of currently valid source file paths

        Returns:
            Dictionary with deletion results
        """
        try:
            # Find orphaned sources first
            orphan_info = self.find_orphaned_sources(valid_sources)
            orphaned_sources = set(orphan_info['orphaned_sources'])

            if not orphaned_sources:
                return {
                    'deleted_points': 0,
                    'deleted_sources': [],
                    'message': 'No orphaned embeddings found'
                }

            # Delete all points from orphaned sources
            deleted_points = 0
            deleted_sources = []

            for source in orphaned_sources:
                # Get all point IDs for this source
                result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=self.client.models.Filter(
                        must=[
                            self.client.models.FieldCondition(
                                key="source",
                                match=self.client.models.MatchValue(value=source)
                            )
                        ]
                    ),
                    limit=10000,  # Adjust if needed based on expected max points per source
                    with_payload=False,
                    with_vectors=False
                )

                point_ids = [point.id for point in result[0]]

                if point_ids:
                    # Delete the points
                    self.client.delete(
                        collection_name=self.collection_name,
                        points_selector=point_ids
                    )
                    deleted_points += len(point_ids)
                    deleted_sources.append(source)

            return {
                'deleted_points': deleted_points,
                'deleted_sources': deleted_sources,
                'message': f'Deleted {deleted_points} orphaned embeddings from {len(deleted_sources)} sources'
            }

        except Exception as e:
            print(f"Error deleting orphaned embeddings: {e}")
            return {
                'deleted_points': 0,
                'deleted_sources': [],
                'error': str(e)
            }

    def get_collection_sources(self) -> Dict[str, int]:
        """
        Get all sources currently in the collection with their point counts.

        Returns:
            Dictionary mapping source paths to point counts
        """
        try:
            sources_count = {}

            # Scroll through all points to collect sources and their counts
            offset = None
            while True:
                result = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=1000,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                points, next_offset = result

                for point in points:
                    source = point.payload.get('source', '')
                    if source:
                        sources_count[source] = sources_count.get(source, 0) + 1

                if next_offset is None:
                    break
                offset = next_offset

            return sources_count

        except Exception as e:
            print(f"Error getting collection sources: {e}")
            return {}

    def compare_sources(self, current_sources: Set[str]) -> Dict[str, Any]:
        """
        Compare current sources with those in the collection.

        Args:
            current_sources: Set of currently valid source file paths

        Returns:
            Dictionary with comparison results
        """
        collection_sources = self.get_collection_sources()
        collection_source_set = set(collection_sources.keys())

        # Find differences
        new_sources = current_sources - collection_source_set  # Sources not yet in collection
        existing_sources = current_sources & collection_source_set  # Sources in both
        orphaned_sources = collection_source_set - current_sources  # Sources in collection but not current

        return {
            'new_sources': list(new_sources),
            'existing_sources': list(existing_sources),
            'orphaned_sources': list(orphaned_sources),
            'collection_source_counts': collection_sources,
            'summary': {
                'current_sources_count': len(current_sources),
                'collection_sources_count': len(collection_source_set),
                'new_sources_count': len(new_sources),
                'existing_sources_count': len(existing_sources),
                'orphaned_sources_count': len(orphaned_sources)
            }
        }


def create_orphan_detector(collection_name: str = None) -> OrphanDetector:
    """
    Factory function to create an OrphanDetector instance.

    Args:
        collection_name: Optional collection name

    Returns:
        OrphanDetector instance
    """
    return OrphanDetector(collection_name=collection_name)


if __name__ == "__main__":
    # Test the orphan detector
    import sys

    detector = OrphanDetector()

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print("All sources in collection:")
        sources = detector.get_collection_sources()
        for source, count in sources.items():
            print(f"  {source}: {count} points")

    elif len(sys.argv) > 1 and sys.argv[1] == "find":
        print("Finding orphaned sources...")
        # In a real scenario, you'd pass the actual current source files
        # For this test, we'll just show what would be considered orphaned
        # compared to an empty set (which would make all sources orphans)
        result = detector.find_orphaned_sources(set())
        print(f"Orphaned sources: {result['orphaned_sources']}")
        print(f"Total orphaned points: {result['total_orphaned_points']}")

    else:
        print("Orphan Detector Module")
        print("=" * 50)
        print("Usage:")
        print("  python orphan_detector.py list          # List all sources in collection")
        print("  python orphan_detector.py find          # Find orphaned sources")
        print("=" * 50)

        # Example usage
        print("\nExample: Finding orphaned sources")
        # This would typically be called with the actual current source files
        # current_sources = {"path/to/file1.md", "path/to/file2.md", ...}
        # result = detector.find_orphaned_sources(current_sources)