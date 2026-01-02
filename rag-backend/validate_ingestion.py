"""
Validation script for verifying ingestion success
Queries Qdrant for sample chapters and checks data integrity
"""
import sys
import os
from typing import List, Dict, Any
from qdrant_client.http import models
from qdrant_setup import get_qdrant_client, COLLECTION_NAME
from embeddings_service import get_embeddings_service

# Fix Windows console encoding issues
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class IngestionValidator:
    """
    Validates ingestion by checking Qdrant collection and querying samples.
    """

    def __init__(self):
        """Initialize the validator"""
        self.client = get_qdrant_client()
        self.collection_name = COLLECTION_NAME
        self.embeddings_service = get_embeddings_service()

    def validate_collection_exists(self) -> bool:
        """
        Check if the collection exists.

        Returns:
            True if collection exists, False otherwise
        """
        try:
            self.client.get_collection(self.collection_name)
            print(f"✓ Collection '{self.collection_name}' exists")
            return True
        except Exception as e:
            print(f"✗ Collection '{self.collection_name}' not found: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection stats
        """
        try:
            info = self.client.get_collection(self.collection_name)
            stats = {
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status),
                "vector_size": info.config.params.vectors.size,
                "distance": str(info.config.params.vectors.distance)
            }

            print(f"\nCollection Statistics:")
            print(f"  Vectors count: {stats['vectors_count']}")
            print(f"  Points count: {stats['points_count']}")
            print(f"  Status: {stats['status']}")
            print(f"  Vector size: {stats['vector_size']}")
            print(f"  Distance metric: {stats['distance']}")

            return stats

        except Exception as e:
            print(f"✗ Failed to get collection stats: {e}")
            return {}

    def sample_points(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve sample points from the collection.

        Args:
            limit: Number of points to retrieve

        Returns:
            List of point payloads
        """
        try:
            # Scroll through collection to get samples
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            points = result[0] if result else []

            print(f"\nSample Points ({len(points)}):")
            for i, point in enumerate(points, 1):
                payload = point.payload
                print(f"\n  Point {i}:")
                print(f"    Chapter: {payload.get('chapter', 'N/A')}")
                print(f"    Title: {payload.get('title', 'N/A')}")
                print(f"    Section: {payload.get('section', 'N/A')}")
                print(f"    Source: {payload.get('source', 'N/A')}")
                content_preview = payload.get('content', '')[:100]
                print(f"    Content: {content_preview}...")

            return [p.payload for p in points]

        except Exception as e:
            print(f"✗ Failed to retrieve sample points: {e}")
            return []

    def test_search(self, query: str = "What is physical AI?", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Test vector search with a sample query.

        Args:
            query: Test query string
            top_k: Number of results to retrieve

        Returns:
            List of search results
        """
        print(f"\nTest Search Query: \"{query}\"")

        try:
            # Generate query embedding
            query_embedding = self.embeddings_service.embed_text(query)
            print(f"  Generated query embedding ({len(query_embedding)} dims)")

            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True
            )

            print(f"  Found {len(results)} results:\n")

            for i, hit in enumerate(results, 1):
                print(f"  Result {i} (score: {hit.score:.4f}):")
                print(f"    Chapter: {hit.payload.get('chapter', 'N/A')}")
                print(f"    Section: {hit.payload.get('section', 'N/A')}")
                print(f"    Content: {hit.payload.get('content', '')[:150]}...")
                print()

            return [{"score": hit.score, "payload": hit.payload} for hit in results]

        except Exception as e:
            print(f"✗ Search failed: {e}")
            return []

    def validate_metadata(self) -> bool:
        """
        Validate that points have required metadata fields.

        Returns:
            True if validation passes, False otherwise
        """
        print("\nValidating Metadata:")

        required_fields = ['content', 'source', 'chapter']
        optional_fields = ['title', 'section', 'subsection', 'chapter_number']

        try:
            # Get a sample
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=10,
                with_payload=True
            )

            points = result[0] if result else []

            if not points:
                print("  ⚠ No points found to validate")
                return False

            missing_fields = set()
            points_with_issues = []

            for i, point in enumerate(points):
                point_missing = []
                for field in required_fields:
                    if field not in point.payload:
                        missing_fields.add(field)
                        point_missing.append(field)

                if point_missing:
                    points_with_issues.append({
                        'index': i,
                        'id': str(point.id),
                        'missing': point_missing,
                        'has_keys': list(point.payload.keys())
                    })

            if missing_fields:
                print(f"  ✗ Missing required fields: {missing_fields}")
                print(f"\n  Found {len(points_with_issues)} points with missing fields:")
                for issue in points_with_issues[:3]:  # Show first 3
                    print(f"    Point {issue['index']} (ID: {issue['id'][:8]}...)")
                    print(f"      Missing: {issue['missing']}")
                    print(f"      Has keys: {issue['has_keys']}")
                if len(points_with_issues) > 3:
                    print(f"    ... and {len(points_with_issues) - 3} more")
                print(f"\n  ⚠️  This indicates mixed data formats in the collection.")
                print(f"  ℹ️  Solution: Run cleanup_and_reingest.py to reset the collection")
                return False

            print(f"  ✓ All required fields present: {required_fields}")
            print(f"  ℹ Optional fields: {optional_fields}")

            return True

        except Exception as e:
            print(f"  ✗ Metadata validation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_validation(self) -> bool:
        """
        Run complete validation suite.

        Returns:
            True if all validations pass, False otherwise
        """
        print("=" * 70)
        print("  Ingestion Validation")
        print("=" * 70)

        all_passed = True

        # 1. Collection exists
        if not self.validate_collection_exists():
            return False

        # 2. Collection stats
        stats = self.get_collection_stats()
        if not stats or stats.get('points_count', 0) == 0:
            print("\n✗ Collection is empty - ingestion may have failed")
            all_passed = False

        # 3. Sample points
        samples = self.sample_points(limit=3)
        if not samples:
            print("\n✗ Could not retrieve sample points")
            all_passed = False

        # 4. Metadata validation
        if not self.validate_metadata():
            all_passed = False

        # 5. Test search
        results = self.test_search("What is embodied intelligence?", top_k=3)
        if not results:
            print("✗ Search test failed")
            all_passed = False

        # Summary
        print("\n" + "=" * 70)
        if all_passed:
            print("✓ All validation checks passed")
            print("  Ingestion appears successful!")
        else:
            print("✗ Some validation checks failed")
            print("  Review errors above and check ingestion logs")
        print("=" * 70)

        return all_passed


def validate_ingestion() -> bool:
    """
    Convenience function to validate ingestion.

    Returns:
        True if validation passes, False otherwise
    """
    validator = IngestionValidator()
    return validator.run_validation()


if __name__ == "__main__":
    try:
        passed = validate_ingestion()
        sys.exit(0 if passed else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
