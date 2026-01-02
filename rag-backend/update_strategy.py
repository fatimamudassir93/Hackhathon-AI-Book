"""
Update strategy for managing content updates without duplication
Handles deletion of old embeddings before inserting new ones
"""
from typing import List, Dict, Any, Optional, Set
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import os
from dotenv import load_dotenv

load_dotenv()


class UpdateStrategy:
    """
    Manages updates to Qdrant collection by replacing old embeddings with new ones.
    Prevents duplication during content updates.
    """

    def __init__(self, collection_name: str = None):
        """
        Initialize the update strategy.

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

    def delete_source_embeddings(self, source_path: str) -> int:
        """
        Delete all embeddings from a specific source file.

        Args:
            source_path: Path to the source file

        Returns:
            Number of points deleted
        """
        try:
            # Query to find all points from this source
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=source_path)
                        )
                    ]
                ),
                limit=1000,
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
                return len(point_ids)

            return 0

        except Exception as e:
            print(f"Error deleting embeddings for {source_path}: {e}")
            return 0

    def delete_sources_batch(self, source_paths: List[str]) -> Dict[str, int]:
        """
        Delete embeddings for multiple source files.

        Args:
            source_paths: List of source file paths

        Returns:
            Dictionary mapping source path to number of deletions
        """
        results = {}

        for source_path in source_paths:
            deleted = self.delete_source_embeddings(source_path)
            results[source_path] = deleted

        return results

    def delete_orphaned_embeddings(self, valid_sources: Set[str]) -> int:
        """
        Delete embeddings whose source files no longer exist.

        Args:
            valid_sources: Set of valid source file paths

        Returns:
            Number of orphaned points deleted
        """
        try:
            # Get all unique sources in the collection
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=10000,  # Adjust based on collection size
                with_payload=True,
                with_vectors=False
            )

            # Find orphaned points
            orphaned_ids = []
            for point in result[0]:
                source = point.payload.get('source', '')
                if source and source not in valid_sources:
                    orphaned_ids.append(point.id)

            # Delete orphaned points
            if orphaned_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=orphaned_ids
                )

            return len(orphaned_ids)

        except Exception as e:
            print(f"Error deleting orphaned embeddings: {e}")
            return 0

    def get_source_count(self, source_path: str) -> int:
        """
        Count how many embeddings exist for a source file.

        Args:
            source_path: Path to the source file

        Returns:
            Number of embeddings for this source
        """
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=source_path)
                        )
                    ]
                ),
                limit=1,
                with_payload=False,
                with_vectors=False
            )

            # Get total count by scrolling through all
            total = 0
            scroll_result = result
            while scroll_result[0]:
                total += len(scroll_result[0])
                if scroll_result[1] is None:  # No more results
                    break
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="source",
                                match=MatchValue(value=source_path)
                            )
                        ]
                    ),
                    offset=scroll_result[1],
                    limit=100,
                    with_payload=False,
                    with_vectors=False
                )

            return total

        except Exception as e:
            print(f"Error counting embeddings for {source_path}: {e}")
            return 0

    def prepare_update(self, source_paths: List[str], dry_run: bool = False) -> Dict[str, Any]:
        """
        Prepare for updating source files by analyzing what will be deleted.

        Args:
            source_paths: List of source files to update
            dry_run: If True, only report what would be deleted without actually deleting

        Returns:
            Dictionary with update plan details
        """
        plan = {
            'sources': [],
            'total_points_to_delete': 0,
            'dry_run': dry_run
        }

        for source_path in source_paths:
            count = self.get_source_count(source_path)
            plan['sources'].append({
                'source': source_path,
                'existing_points': count
            })
            plan['total_points_to_delete'] += count

        return plan

    def execute_update(self, source_paths: List[str]) -> Dict[str, Any]:
        """
        Execute update by deleting old embeddings for the specified sources.
        New embeddings should be uploaded separately after this.

        Args:
            source_paths: List of source files to update

        Returns:
            Dictionary with execution results
        """
        # Prepare update plan
        plan = self.prepare_update(source_paths, dry_run=False)

        # Execute deletions
        deletion_results = self.delete_sources_batch(source_paths)

        return {
            'plan': plan,
            'deletions': deletion_results,
            'total_deleted': sum(deletion_results.values())
        }


def create_update_strategy(collection_name: str = None) -> UpdateStrategy:
    """
    Factory function to create an UpdateStrategy instance.

    Args:
        collection_name: Optional collection name

    Returns:
        UpdateStrategy instance
    """
    return UpdateStrategy(collection_name=collection_name)


if __name__ == "__main__":
    # Test the update strategy
    import sys

    strategy = UpdateStrategy()

    # Example: Check count for a source
    if len(sys.argv) > 1 and sys.argv[1] == "count":
        if len(sys.argv) > 2:
            source = sys.argv[2]
            count = strategy.get_source_count(source)
            print(f"Source '{source}' has {count} embeddings")
        else:
            print("Usage: python update_strategy.py count <source_path>")

    # Example: Dry run update
    elif len(sys.argv) > 1 and sys.argv[1] == "dry-run":
        if len(sys.argv) > 2:
            sources = sys.argv[2:]
            plan = strategy.prepare_update(sources, dry_run=True)
            print(f"\nUpdate Plan (Dry Run)")
            print(f"{'='*60}")
            for item in plan['sources']:
                print(f"  {item['source']}: {item['existing_points']} points")
            print(f"{'='*60}")
            print(f"Total points to delete: {plan['total_points_to_delete']}")
        else:
            print("Usage: python update_strategy.py dry-run <source_path> [<source_path> ...]")

    else:
        print("Update Strategy Module")
        print(f"{'='*60}")
        print("Usage:")
        print("  python update_strategy.py count <source_path>")
        print("  python update_strategy.py dry-run <source_path> [<source_path> ...]")
        print(f"{'='*60}")
