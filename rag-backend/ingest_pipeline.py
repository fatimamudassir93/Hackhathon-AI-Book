"""
Ingestion pipeline orchestrator
Coordinates: scan → parse → chunk → embed → upload
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import pipeline components
from file_scanner import FileScanner
from chunker import DocumentChunker
from embedding_batch import EmbeddingBatchProcessor
from qdrant_uploader import QdrantUploader
from dedup_service import DeduplicationService
from logging_config import get_ingestion_logger

load_dotenv()


class IngestionPipeline:
    """
    Orchestrates the complete ingestion pipeline:
    1. Scan for markdown files
    2. Parse and chunk documents
    3. Generate embeddings
    4. Upload to Qdrant
    5. Track for deduplication
    """

    def __init__(
        self,
        docs_directory: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_batch_size: int = 32,
        upload_batch_size: int = 100,
        dedup_cache_file: Optional[str] = None,
        log_file: Optional[str] = None
    ):
        """
        Initialize the ingestion pipeline.

        Args:
            docs_directory: Path to docs directory with markdown files
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            embedding_batch_size: Batch size for embedding generation
            upload_batch_size: Batch size for Qdrant upload
            dedup_cache_file: Optional cache file for deduplication
            log_file: Optional log file path
        """
        self.docs_directory = docs_directory

        # Initialize components
        self.scanner = FileScanner()
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.embedder = EmbeddingBatchProcessor(
            batch_size=embedding_batch_size
        )
        self.uploader = QdrantUploader()
        self.dedup = DeduplicationService(cache_file=dedup_cache_file)
        self.logger = get_ingestion_logger(log_file=log_file)

        # Pipeline statistics
        self.stats = {
            "files_found": 0,
            "files_processed": 0,
            "files_skipped": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "vectors_uploaded": 0,
            "errors": 0
        }

    def run(self, force_reindex: bool = False, incremental: bool = False) -> Dict[str, Any]:
        """
        Run the complete ingestion pipeline.

        Args:
            force_reindex: If True, reindex all files even if unchanged
            incremental: If True, only process changed files and delete orphaned embeddings

        Returns:
            Dictionary with pipeline statistics
        """
        self.logger.start()

        try:
            # Step 1: Scan for files
            self.logger.logger.info("Step 1: Scanning for markdown files...")
            files = self.scanner.get_textbook_files(self.docs_directory)
            self.stats["files_found"] = len(files)
            self.logger.logger.info(f"  Found {len(files)} textbook files")

            if not files:
                self.logger.logger.warning("  No files found to process")
                return self.stats

            # Convert file paths to source IDs for comparison
            current_sources = {f"file:{file_path}" for file_path in files}

            # Step 2: Handle incremental mode - delete orphaned embeddings first
            if incremental:
                self.logger.logger.info("Step 2: Checking for orphaned embeddings...")
                from orphan_detector import create_orphan_detector
                orphan_detector = create_orphan_detector()

                # Find and delete orphaned embeddings
                orphan_result = orphan_detector.delete_orphaned_embeddings(current_sources)
                self.logger.logger.info(f"  Deleted {orphan_result.get('deleted_points', 0)} orphaned embeddings from {len(orphan_result.get('deleted_sources', []))} sources")

            # Step 3: Process each file
            self.logger.logger.info("Step 3: Processing documents...")
            all_chunks = []

            for file_path in files:
                try:
                    self.logger.log_file_processing(file_path)

                    # Check if file needs processing
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    source_id = f"file:{file_path}"

                    if not force_reindex and not self.dedup.has_changed(content, source_id):
                        self.logger.logger.info(f"  ↷ Skipped (unchanged)")
                        self.stats["files_skipped"] += 1

                        # In incremental mode, we still need to track this file
                        if incremental:
                            # Register the file to update its hash in the cache
                            self.dedup.register(content, source_id)
                        continue

                    # In incremental mode, delete existing embeddings for this source first
                    if incremental:
                        from update_strategy import create_update_strategy
                        update_strategy = create_update_strategy()
                        deleted_count = update_strategy.delete_source_embeddings(file_path)
                        if deleted_count > 0:
                            self.logger.logger.info(f"  Deleted {deleted_count} existing embeddings for {file_path}")

                    # Chunk the file
                    chunks = self.chunker.chunk_file(file_path)
                    self.logger.log_chunks_created(len(chunks), file_path)

                    # Add source ID to each chunk for dedup tracking
                    for i, chunk in enumerate(chunks):
                        chunk['source_id'] = f"{source_id}:chunk{i}"

                    all_chunks.extend(chunks)
                    self.stats["chunks_created"] += len(chunks)
                    self.stats["files_processed"] += 1

                    # Register in dedup cache
                    self.dedup.register(content, source_id)

                except Exception as e:
                    self.logger.log_error(f"Failed to process {file_path}", e)
                    self.stats["errors"] += 1

            if not all_chunks:
                self.logger.logger.info("  No new chunks to process")
                self.logger.complete()
                return self.stats

            self.logger.logger.info(f"  Created {len(all_chunks)} chunks total")

            # Step 4: Generate embeddings
            self.logger.logger.info("Step 4: Generating embeddings...")
            chunks_with_embeddings = self.embedder.process_chunks(
                all_chunks,
                show_progress=True
            )
            self.stats["embeddings_generated"] = len(chunks_with_embeddings)
            self.logger.log_embeddings_generated(len(chunks_with_embeddings))

            # Step 5: Upload to Qdrant
            self.logger.logger.info("Step 5: Uploading vectors to Qdrant...")
            success = self.uploader.upload_chunks(
                chunks_with_embeddings,
                show_progress=True
            )

            if success:
                self.stats["vectors_uploaded"] = len(chunks_with_embeddings)
                self.logger.log_upload(len(chunks_with_embeddings))
            else:
                self.logger.log_error("Some uploads failed")

            # Step 6: Save dedup cache
            self.logger.logger.info("Step 6: Saving deduplication cache...")
            self.dedup.save_cache()

            # Complete
            final_stats = self.logger.complete()
            self.stats.update(final_stats)

            return self.stats

        except Exception as e:
            self.logger.log_error(f"Pipeline failed", e)
            self.stats["errors"] += 1
            return self.stats

    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return self.stats.copy()


def run_ingestion(
    docs_directory: str = None,
    force_reindex: bool = False,
    incremental: bool = False,
    log_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run the ingestion pipeline.

    Args:
        docs_directory: Path to docs directory (default: from env or ../physical-ai-book/docs)
        force_reindex: Whether to force reindexing of all files
        incremental: Whether to run incremental ingestion (only process changed files)
        log_file: Optional log file path

    Returns:
        Pipeline statistics
    """
    # Default docs directory
    if docs_directory is None:
        docs_directory = os.getenv(
            "DOCS_DIRECTORY",
            str(Path(__file__).parent / "../physical-ai-book/docs")
        )

    # Resolve path
    docs_path = Path(docs_directory).resolve()

    if not docs_path.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_path}")

    print(f"Ingestion Pipeline")
    print(f"{'='*60}")
    print(f"Docs directory: {docs_path}")
    print(f"Force reindex: {force_reindex}")
    print(f"Incremental: {incremental}")
    print(f"{'='*60}\n")

    # Create and run pipeline
    pipeline = IngestionPipeline(
        docs_directory=str(docs_path),
        dedup_cache_file=".ingestion_cache.json",
        log_file=log_file
    )

    stats = pipeline.run(force_reindex=force_reindex, incremental=incremental)

    return stats


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    force = "--force" in sys.argv or "-f" in sys.argv
    docs_dir = None

    for arg in sys.argv[1:]:
        if not arg.startswith('-') and Path(arg).exists():
            docs_dir = arg
            break

    # Run pipeline
    try:
        stats = run_ingestion(
            docs_directory=docs_dir,
            force_reindex=force,
            log_file="ingestion.log"
        )

        print(f"\n{'='*60}")
        print("Pipeline Complete")
        print(f"{'='*60}")
        print(f"Files found: {stats.get('files_found', 0)}")
        print(f"Files processed: {stats.get('files_processed', 0)}")
        print(f"Files skipped: {stats.get('files_skipped', 0)}")
        print(f"Chunks created: {stats.get('chunks_created', 0)}")
        print(f"Embeddings generated: {stats.get('embeddings_generated', 0)}")
        print(f"Vectors uploaded: {stats.get('vectors_uploaded', 0)}")
        print(f"Errors: {stats.get('errors', 0)}")

    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}")
        sys.exit(1)
