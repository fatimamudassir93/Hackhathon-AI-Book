"""
Deduplication service using content hashes
Prevents duplicate embeddings during re-ingestion
"""
import hashlib
from typing import Dict, Set, List, Optional
from pathlib import Path
import json


class DeduplicationService:
    """
    Tracks content hashes to prevent duplicate embeddings.
    Supports both in-memory and persistent storage.
    """

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the deduplication service.

        Args:
            cache_file: Optional path to persist hash cache
        """
        self.cache_file = cache_file
        self.content_hashes: Dict[str, str] = {}  # hash -> source_id
        self.source_hashes: Dict[str, str] = {}  # source_id -> hash

        if cache_file:
            self._load_cache()

    def compute_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content.

        Args:
            content: Text content to hash

        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_duplicate(self, content: str, source_id: str) -> bool:
        """
        Check if content is a duplicate.

        Args:
            content: Text content to check
            source_id: Identifier for the source (e.g., file path + chunk index)

        Returns:
            True if content is duplicate, False otherwise
        """
        content_hash = self.compute_hash(content)

        # Check if this exact content exists
        if content_hash in self.content_hashes:
            existing_source = self.content_hashes[content_hash]
            # Allow same source to update (re-ingestion)
            if existing_source == source_id:
                return False
            # Different source with same content is a duplicate
            return True

        return False

    def register(self, content: str, source_id: str) -> str:
        """
        Register content in the deduplication cache.

        Args:
            content: Text content
            source_id: Source identifier

        Returns:
            Content hash
        """
        content_hash = self.compute_hash(content)

        # Update mappings
        self.content_hashes[content_hash] = source_id
        self.source_hashes[source_id] = content_hash

        return content_hash

    def has_changed(self, content: str, source_id: str) -> bool:
        """
        Check if content has changed since last ingestion.

        Args:
            content: Current content
            source_id: Source identifier

        Returns:
            True if content changed or is new, False if unchanged
        """
        current_hash = self.compute_hash(content)

        # Check if we have a previous hash for this source
        if source_id in self.source_hashes:
            previous_hash = self.source_hashes[source_id]
            return current_hash != previous_hash

        # New source
        return True

    def clear_source(self, source_id: str):
        """
        Remove a source from the cache.

        Args:
            source_id: Source identifier to remove
        """
        if source_id in self.source_hashes:
            old_hash = self.source_hashes[source_id]
            del self.source_hashes[source_id]

            # Remove from content_hashes if no other source uses this hash
            if old_hash in self.content_hashes:
                if self.content_hashes[old_hash] == source_id:
                    del self.content_hashes[old_hash]

    def get_all_sources(self) -> Set[str]:
        """
        Get all registered source IDs.

        Returns:
            Set of source identifiers
        """
        return set(self.source_hashes.keys())

    def find_orphaned_sources(self, current_sources: Set[str]) -> Set[str]:
        """
        Find sources that are in cache but not in current source list.
        These represent deleted or moved files.

        Args:
            current_sources: Set of current source IDs

        Returns:
            Set of orphaned source IDs
        """
        cached_sources = self.get_all_sources()
        return cached_sources - current_sources

    def _load_cache(self):
        """Load cache from file if it exists"""
        if not self.cache_file:
            return

        cache_path = Path(self.cache_file)
        if not cache_path.exists():
            return

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.content_hashes = data.get('content_hashes', {})
                self.source_hashes = data.get('source_hashes', {})
        except Exception as e:
            print(f"Warning: Could not load cache from {self.cache_file}: {e}")

    def save_cache(self):
        """Save cache to file"""
        if not self.cache_file:
            return

        cache_path = Path(self.cache_file)
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'content_hashes': self.content_hashes,
                    'source_hashes': self.source_hashes
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache to {self.cache_file}: {e}")

    def compare_files(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Compare files against cache to determine which changed, which are new, and which unchanged.

        Args:
            file_paths: List of current file paths

        Returns:
            Dictionary with 'changed', 'new', 'unchanged', and 'deleted' file lists
        """
        changed = []
        new = []
        unchanged = []

        # Check each current file
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                source_id = f"file:{file_path}"

                if source_id not in self.source_hashes:
                    new.append(file_path)
                elif self.has_changed(content, source_id):
                    changed.append(file_path)
                else:
                    unchanged.append(file_path)

            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

        # Find deleted files
        current_source_ids = {f"file:{fp}" for fp in file_paths}
        orphaned = self.find_orphaned_sources(current_source_ids)
        deleted = [src.replace("file:", "") for src in orphaned if src.startswith("file:")]

        return {
            'changed': changed,
            'new': new,
            'unchanged': unchanged,
            'deleted': deleted
        }

    def get_file_hash(self, file_path: str) -> Optional[str]:
        """
        Get the cached hash for a file.

        Args:
            file_path: Path to the file

        Returns:
            Hash string or None if not cached
        """
        source_id = f"file:{file_path}"
        return self.source_hashes.get(source_id)

    def get_stats(self) -> Dict[str, int]:
        """
        Get deduplication statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "unique_hashes": len(self.content_hashes),
            "registered_sources": len(self.source_hashes),
        }


# Global instance
_dedup_service = None


def get_dedup_service(cache_file: Optional[str] = None) -> DeduplicationService:
    """
    Get or create the global deduplication service.

    Args:
        cache_file: Optional cache file path

    Returns:
        DeduplicationService instance
    """
    global _dedup_service
    if _dedup_service is None:
        _dedup_service = DeduplicationService(cache_file=cache_file)
    return _dedup_service


if __name__ == "__main__":
    # Test the deduplication service
    service = DeduplicationService()

    # Test basic operations
    content1 = "This is the first piece of content."
    content2 = "This is the second piece of content."
    content3 = "This is the first piece of content."  # Duplicate of content1

    print("Testing Deduplication Service")
    print("=" * 60)

    # Register first content
    hash1 = service.register(content1, "source1")
    print(f"Registered source1: {hash1[:16]}...")

    # Check for duplicate (different source, same content)
    is_dup = service.is_duplicate(content3, "source3")
    print(f"Is content3 duplicate of source1? {is_dup}")

    # Register second content
    hash2 = service.register(content2, "source2")
    print(f"Registered source2: {hash2[:16]}...")

    # Re-register same source (should allow)
    is_dup_same = service.is_duplicate(content1, "source1")
    print(f"Is source1 duplicate of itself? {is_dup_same}")

    # Test change detection
    modified_content = "This is modified content."
    has_changed = service.has_changed(modified_content, "source1")
    print(f"Has source1 changed? {has_changed}")

    unchanged = service.has_changed(content1, "source1")
    print(f"Is source1 unchanged? {not unchanged}")

    # Test orphan detection
    current = {"source1", "source2"}
    service.register("New content", "source_old")
    orphans = service.find_orphaned_sources(current)
    print(f"Orphaned sources: {orphans}")

    # Stats
    stats = service.get_stats()
    print(f"\nStats: {stats}")
