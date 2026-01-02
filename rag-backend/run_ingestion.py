#!/usr/bin/env python3
"""
CLI entry point for manual pipeline execution
Provides command-line interface for textbook content ingestion
"""
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import pipeline
from ingest_pipeline import run_ingestion
from qdrant_setup import create_qdrant_collection


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Physical AI Textbook Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run ingestion with default settings
  python run_ingestion.py

  # Force re-index all content
  python run_ingestion.py --force

  # Run incremental ingestion (only changed files, remove orphaned embeddings)
  python run_ingestion.py --incremental

  # Dry run - see what would be processed without making changes
  python run_ingestion.py --dry-run

  # Dry run with incremental analysis
  python run_ingestion.py --dry-run --incremental

  # Specify custom docs directory
  python run_ingestion.py --docs ../my-docs

  # Initialize Qdrant collection only
  python run_ingestion.py --setup-only

  # Run with verbose logging
  python run_ingestion.py --verbose
        """
    )

    parser.add_argument(
        '--docs',
        type=str,
        default=None,
        help='Path to docs directory (default: ../physical-ai-book/docs)'
    )

    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force re-index all files (ignore cache)'
    )

    parser.add_argument(
        '--setup-only',
        action='store_true',
        help='Only setup Qdrant collection, do not run ingestion'
    )

    parser.add_argument(
        '--recreate-collection',
        action='store_true',
        help='Recreate Qdrant collection (deletes existing data)'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        default='ingestion.log',
        help='Path to log file (default: ingestion.log)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scan and chunk files without uploading to Qdrant'
    )

    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Run incremental ingestion (only process changed files and remove orphaned embeddings)'
    )

    args = parser.parse_args()

    # Banner
    print("=" * 70)
    print("  Physical AI & Humanoid Robotics Textbook")
    print("  Content Ingestion Pipeline")
    print("=" * 70)
    print()

    # Setup Qdrant collection
    if args.recreate_collection or args.setup_only:
        print("Setting up Qdrant collection...")
        try:
            create_qdrant_collection(force_recreate=args.recreate_collection)
            print("[OK] Qdrant collection ready\n")
        except Exception as e:
            print(f"[ERROR] Failed to setup Qdrant collection: {e}")
            return 1

        if args.setup_only:
            print("Setup complete. Exiting (--setup-only specified)")
            return 0

    # Resolve docs directory
    docs_dir = args.docs
    if docs_dir:
        docs_path = Path(docs_dir).resolve()
        if not docs_path.exists():
            print(f"[ERROR] Docs directory not found: {docs_path}")
            return 1
    else:
        # Default to physical-ai-book/docs
        default_path = Path(__file__).parent / "../physical-ai-book/docs"
        docs_path = default_path.resolve()

    if args.verbose:
        print(f"Configuration:")
        print(f"  Docs directory: {docs_path}")
        print(f"  Force reindex: {args.force}")
        print(f"  Log file: {args.log_file}")
        print(f"  Dry run: {args.dry_run}")
        print()

    # Dry run mode
    if args.dry_run:
        print("DRY RUN MODE - No vectors will be uploaded")
        print()
        from file_scanner import FileScanner
        from chunker import DocumentChunker
        from dedup_service import get_dedup_service

        scanner = FileScanner()
        chunker = DocumentChunker()
        dedup_service = get_dedup_service(cache_file=".ingestion_cache.json")

        files = scanner.get_textbook_files(str(docs_path))
        print(f"Found {len(files)} files")

        # Determine what would be processed vs skipped
        files_to_process = []
        files_to_skip = []
        total_chunks = 0

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            source_id = f"file:{file_path}"

            if args.force or dedup_service.has_changed(content, source_id):
                files_to_process.append(file_path)
                chunks = chunker.chunk_file(file_path)
                total_chunks += len(chunks)
                if args.verbose:
                    print(f"  {Path(file_path).name}: {len(chunks)} chunks (WILL PROCESS)")
            else:
                files_to_skip.append(file_path)
                if args.verbose:
                    print(f"  {Path(file_path).name}: 0 chunks (SKIPPED - unchanged)")

        print(f"\nFiles to process: {len(files_to_process)}")
        print(f"Files to skip: {len(files_to_skip)}")
        print(f"Total chunks that would be created: {total_chunks}")

        # If in incremental mode, also check for orphaned embeddings
        if args.incremental:
            print("\nIncremental mode analysis:")
            from orphan_detector import create_orphan_detector
            from pathlib import Path as PathLib

            # Get current sources
            current_sources = {f"file:{str(PathLib(file_path).resolve())}" for file_path in files}

            # Create detector and find what would be deleted
            detector = create_orphan_detector()
            orphan_info = detector.find_orphaned_sources(current_sources)

            print(f"  Orphaned sources that would be deleted: {orphan_info['total_orphaned_sources']}")
            print(f"  Orphaned points that would be deleted: {orphan_info['total_orphaned_points']}")

            if args.verbose and orphan_info['orphaned_sources']:
                print("  Orphaned sources:")
                for source in orphan_info['orphaned_sources']:
                    print(f"    - {source}")

        print("(Dry run complete - no data uploaded or deleted)")
        return 0

    # Run ingestion
    try:
        print("Starting ingestion pipeline...\n")
        stats = run_ingestion(
            docs_directory=str(docs_path),
            force_reindex=args.force,
            incremental=args.incremental,
            log_file=args.log_file
        )

        # Print summary
        print("\n" + "=" * 70)
        print("  Ingestion Complete")
        print("=" * 70)
        print(f"  Files found:          {stats.get('files_found', 0)}")
        print(f"  Files processed:      {stats.get('files_processed', 0)}")
        print(f"  Files skipped:        {stats.get('files_skipped', 0)}")
        print(f"  Chunks created:       {stats.get('chunks_created', 0)}")
        print(f"  Embeddings generated: {stats.get('embeddings_generated', 0)}")
        print(f"  Vectors uploaded:     {stats.get('vectors_uploaded', 0)}")
        print(f"  Errors:               {stats.get('errors', 0)}")
        print("=" * 70)

        if stats.get('errors', 0) > 0:
            print(f"\n[WARNING] Completed with {stats['errors']} errors")
            print(f"   Check log file: {args.log_file}")
            return 1
        else:
            print("\n[SUCCESS] Ingestion completed successfully")
            return 0

    except KeyboardInterrupt:
        print("\n\n[WARNING] Ingestion interrupted by user")
        return 130

    except Exception as e:
        print(f"\n[ERROR] Ingestion failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
