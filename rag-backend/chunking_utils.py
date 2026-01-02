"""
Document chunking utilities with semantic splitting logic
Splits markdown content following document structure (headers + paragraphs)
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TextChunk:
    """Represents a semantically meaningful chunk of text"""
    content: str
    metadata: Dict[str, Any]
    chunk_index: int
    char_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary format"""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "chunk_index": self.chunk_index,
            "char_count": self.char_count
        }


class SemanticChunker:
    """
    Chunks markdown documents following semantic boundaries.
    Preserves header hierarchy and groups related paragraphs.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 160,
        min_chunk_size: int = 100
    ):
        """
        Initialize the semantic chunker.

        Args:
            chunk_size: Target maximum characters per chunk (optimized for retrieval performance)
            chunk_overlap: Number of overlapping characters between chunks (20% of chunk_size)
            min_chunk_size: Minimum characters for a valid chunk
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    def chunk_markdown(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> List[TextChunk]:
        """
        Chunk markdown content following header boundaries.

        Args:
            content: Markdown text to chunk
            metadata: Base metadata to attach to all chunks

        Returns:
            List of TextChunk objects
        """
        if metadata is None:
            metadata = {}

        # Split by headers while preserving them
        sections = self._split_by_headers(content)

        chunks = []
        chunk_index = 0

        for section in sections:
            section_chunks = self._chunk_section(
                section["content"],
                section["header"],
                section["level"],
                metadata
            )

            for chunk_content in section_chunks:
                chunk_meta = {
                    **metadata,
                    "header": section["header"],
                    "header_level": section["level"],
                }

                chunks.append(TextChunk(
                    content=chunk_content,
                    metadata=chunk_meta,
                    chunk_index=chunk_index,
                    char_count=len(chunk_content)
                ))
                chunk_index += 1

        return chunks

    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """
        Split content by markdown headers while preserving hierarchy.

        Returns:
            List of dicts with 'header', 'level', and 'content'
        """
        sections = []
        lines = content.split('\n')
        current_section = {"header": "", "level": 0, "content": ""}

        for line in lines:
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)

                # Start new section
                level = len(header_match.group(1))
                header_text = header_match.group(2)
                current_section = {
                    "header": header_text,
                    "level": level,
                    "content": line + "\n"
                }
            else:
                current_section["content"] += line + "\n"

        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        content: str,
        header: str,
        level: int,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Chunk a single section's content, respecting paragraph boundaries.

        Args:
            content: Section text (includes header)
            header: Header text
            level: Header level (1-6)
            metadata: Metadata dict

        Returns:
            List of chunk strings
        """
        # If section is small enough, return as single chunk
        if len(content) <= self.chunk_size:
            return [content.strip()]

        # Split into paragraphs
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) + 2 > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap (last few sentences)
                current_chunk = self._get_overlap(current_chunk) + "\n\n" + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap(self, text: str) -> str:
        """
        Extract overlapping text from the end of a chunk.

        Args:
            text: Source text

        Returns:
            Last portion of text up to chunk_overlap characters
        """
        if len(text) <= self.chunk_overlap:
            return text

        # Try to break at sentence boundary
        overlap_text = text[-self.chunk_overlap:]
        sentence_end = max(
            overlap_text.rfind('. '),
            overlap_text.rfind('! '),
            overlap_text.rfind('? ')
        )

        if sentence_end > 0:
            return overlap_text[sentence_end+2:]
        else:
            return overlap_text


def chunk_document(
    content: str,
    metadata: Dict[str, Any] = None,
    chunk_size: int = 800,
    chunk_overlap: int = 160
) -> List[TextChunk]:
    """
    Convenience function to chunk a document.

    Args:
        content: Document text
        metadata: Metadata to attach to chunks
        chunk_size: Target chunk size in characters (optimized for retrieval performance)
        chunk_overlap: Overlap between chunks (20% of chunk_size)

    Returns:
        List of TextChunk objects
    """
    chunker = SemanticChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return chunker.chunk_markdown(content, metadata)


if __name__ == "__main__":
    # Test the chunker
    sample_markdown = """
# Chapter 1: Introduction to Physical AI

Physical AI represents the convergence of artificial intelligence and embodied systems.

## What is Embodied Intelligence?

Embodied intelligence refers to AI systems that interact with the physical world through sensors and actuators.

### Key Concepts

1. Perception through sensors
2. Action through actuators
3. Learning from interaction

## Applications

Physical AI has applications in robotics, autonomous vehicles, and smart manufacturing.

### Robotics

Humanoid robots are a prime example of physical AI systems.

### Autonomous Vehicles

Self-driving cars use physical AI to navigate complex environments.
"""

    chunks = chunk_document(
        sample_markdown,
        metadata={"chapter": "Chapter 1", "source": "test.md"},
        chunk_size=300,
        chunk_overlap=50
    )

    print(f"Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Characters: {chunk.char_count}")
        print(f"  Header: {chunk.metadata.get('header', 'None')}")
        print(f"  Content preview: {chunk.content[:100]}...")
