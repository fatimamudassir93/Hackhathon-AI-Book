"""
Semantic chunking interface for document processing
Simplified wrapper around chunking_utils for ingestion pipeline
"""
from typing import List, Dict, Any
from chunking_utils import SemanticChunker, TextChunk, chunk_document
from chapter_parser import ChapterParser, DocumentStructure
from metadata_extractor import MetadataExtractor


class DocumentChunker:
    """
    High-level interface for chunking documents with metadata.
    Combines parsing, chunking, and metadata extraction.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        """
        Initialize the document chunker.

        Args:
            chunk_size: Target characters per chunk
            chunk_overlap: Overlapping characters between chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunker = SemanticChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            min_chunk_size=min_chunk_size
        )
        self.parser = ChapterParser()
        self.metadata_extractor = MetadataExtractor()

    def chunk_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Chunk a markdown file with full metadata.

        Args:
            file_path: Path to markdown file

        Returns:
            List of chunk dictionaries with content and metadata
        """
        # Extract document metadata
        doc_metadata = self.metadata_extractor.extract_from_file(file_path)

        # Parse document structure
        doc_structure = self.parser.parse_file(file_path)

        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Base metadata for all chunks
        base_metadata = {
            "source": file_path,
            "chapter": doc_metadata.chapter,
            "title": doc_metadata.title,
        }

        if doc_metadata.chapter_number:
            base_metadata["chapter_number"] = doc_metadata.chapter_number

        # Chunk the content
        chunks = self.chunker.chunk_markdown(content, base_metadata)

        # Convert to dict format with enhanced metadata
        chunk_dicts = []
        for chunk in chunks:
            # Enhance metadata with section information from parser
            breadcrumb = self.parser.build_breadcrumb(
                doc_structure,
                chunk.chunk_index * 20  # Approximate line number
            )

            enhanced_metadata = {
                **chunk.metadata,
                "breadcrumb": breadcrumb,
                "chunk_index": chunk.chunk_index,
                "char_count": chunk.char_count
            }

            chunk_dicts.append({
                "content": chunk.content,
                "metadata": enhanced_metadata
            })

        return chunk_dicts

    def chunk_multiple_files(
        self,
        file_paths: List[str],
        show_progress: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Chunk multiple files.

        Args:
            file_paths: List of file paths
            show_progress: Whether to print progress

        Returns:
            Dictionary mapping file_path -> list of chunks
        """
        results = {}

        for i, file_path in enumerate(file_paths, 1):
            if show_progress:
                print(f"Chunking [{i}/{len(file_paths)}]: {file_path}")

            try:
                chunks = self.chunk_file(file_path)
                results[file_path] = chunks

                if show_progress:
                    print(f"  ✓ Created {len(chunks)} chunks")

            except Exception as e:
                if show_progress:
                    print(f"  ✗ Error: {e}")
                results[file_path] = []

        return results


def chunk_markdown_file(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk a single markdown file.

    Args:
        file_path: Path to markdown file
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks

    Returns:
        List of chunk dictionaries
    """
    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return chunker.chunk_file(file_path)


if __name__ == "__main__":
    # Test the chunker
    import sys
    from pathlib import Path

    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        test_file = "../physical-ai-book/docs/chapters/chapter1.md"

    test_path = Path(test_file).resolve()

    if not test_path.exists():
        print(f"File not found: {test_path}")
        print("Usage: python chunker.py <path_to_markdown_file>")
        sys.exit(1)

    print(f"Chunking: {test_path}\n")

    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    chunks = chunker.chunk_file(str(test_path))

    print(f"Created {len(chunks)} chunks")
    print("=" * 60)

    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\nChunk {i}:")
        print(f"  Size: {chunk['metadata']['char_count']} characters")
        print(f"  Chapter: {chunk['metadata'].get('chapter', 'N/A')}")
        print(f"  Header: {chunk['metadata'].get('header', 'N/A')}")
        print(f"  Breadcrumb: {' > '.join(chunk['metadata'].get('breadcrumb', []))}")
        print(f"  Content preview: {chunk['content'][:150]}...")

    if len(chunks) > 3:
        print(f"\n... and {len(chunks) - 3} more chunks")

    # Summary
    total_chars = sum(c['metadata']['char_count'] for c in chunks)
    avg_size = total_chars / len(chunks) if chunks else 0
    print(f"\nSummary:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Total characters: {total_chars}")
    print(f"  Average chunk size: {avg_size:.0f} characters")
