"""
Cleanup script to remove old data and re-ingest with correct format
"""
import sys
from qdrant_setup import get_qdrant_client, create_qdrant_collection, COLLECTION_NAME

def cleanup():
    """Delete and recreate the collection"""
    print("=" * 70)
    print("  Cleanup and Re-ingestion")
    print("=" * 70)
    print()

    client = get_qdrant_client()

    # Check if collection exists
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"Found existing collection '{COLLECTION_NAME}'")
        print("This collection contains mixed data formats (old and new)")
        print()

        response = input("Delete and recreate collection? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted")
            return False

        print(f"\nDeleting collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)
        print("✓ Collection deleted")

    except Exception as e:
        print(f"Collection does not exist or error: {e}")

    # Recreate collection
    print(f"\nCreating fresh collection '{COLLECTION_NAME}'...")
    create_qdrant_collection(force_recreate=True)
    print("✓ Collection created")

    # Delete cache file
    import os
    cache_file = ".ingestion_cache.json"
    if os.path.exists(cache_file):
        print(f"\nDeleting cache file '{cache_file}'...")
        os.remove(cache_file)
        print("✓ Cache deleted")

    print("\n" + "=" * 70)
    print("✓ Cleanup complete")
    print("\nNext step: Run ingestion pipeline")
    print("  python run_ingestion.py")
    print("=" * 70)

    return True

if __name__ == "__main__":
    try:
        success = cleanup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nAborted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
