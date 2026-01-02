"""
Citation formatter for RAG responses
Extracts and formats chapter/section references from search results
"""
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict


class CitationFormatter:
    """
    Formats citations from retrieved chunks for display in responses.
    """

    def __init__(
        self,
        style: str = "inline",  # 'inline', 'footnote', or 'bibliography'
        include_scores: bool = False
    ):
        """
        Initialize the citation formatter.

        Args:
            style: Citation style ('inline', 'footnote', or 'bibliography')
            include_scores: Whether to include relevance scores
        """
        self.style = style
        self.include_scores = include_scores

    def format_citations(
        self,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Format citations from search result chunks.

        Args:
            chunks: List of search results with metadata

        Returns:
            Dictionary with formatted citations and sources
        """
        if not chunks:
            return {
                'citations': [],
                'formatted': '',
                'sources': []
            }

        # Extract unique sources
        sources = self._extract_sources(chunks)

        # Format based on style
        if self.style == "inline":
            formatted = self._format_inline(sources)
        elif self.style == "footnote":
            formatted = self._format_footnote(sources)
        elif self.style == "bibliography":
            formatted = self._format_bibliography(sources)
        else:
            formatted = self._format_inline(sources)

        return {
            'citations': sources,
            'formatted': formatted,
            'sources': self._get_source_list(chunks)
        }

    def _extract_sources(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract unique sources from chunks.

        Args:
            chunks: Search result chunks

        Returns:
            List of unique source citations
        """
        # Group chunks by chapter
        chapter_groups = defaultdict(list)

        for chunk in chunks:
            chapter = chunk.get('chapter', 'Unknown')
            chapter_groups[chapter].append(chunk)

        # Build citations
        sources = []
        for chapter, chapter_chunks in chapter_groups.items():
            # Get highest scoring chunk for this chapter
            best_chunk = max(chapter_chunks, key=lambda x: x.get('score', 0))

            citation = {
                'chapter': chapter,
                'chapter_number': best_chunk.get('chapter_number'),
                'title': best_chunk.get('title', chapter),
                'section': best_chunk.get('section'),
                'subsection': best_chunk.get('subsection'),
                'header': best_chunk.get('header'),
                'score': best_chunk.get('score', 0),
                'source_file': best_chunk.get('source', ''),
                'breadcrumb': best_chunk.get('breadcrumb', [])
            }

            sources.append(citation)

        # Sort by chapter number
        sources.sort(key=lambda x: x.get('chapter_number') or 999)

        return sources

    def _format_inline(self, sources: List[Dict[str, Any]]) -> str:
        """Format citations inline (Chapter X, Section Y)."""
        if not sources:
            return ""

        citations = []
        for source in sources:
            parts = [source['chapter']]

            if source.get('section'):
                parts.append(source['section'])

            citation = " - ".join(parts)

            if self.include_scores:
                score = source.get('score', 0)
                citation += f" (relevance: {score:.2f})"

            citations.append(citation)

        return "Sources: " + " | ".join(citations)

    def _format_footnote(self, sources: List[Dict[str, Any]]) -> str:
        """Format citations as footnotes [1], [2]."""
        if not sources:
            return ""

        lines = ["Sources:"]
        for i, source in enumerate(sources, 1):
            citation = f"[{i}] {source['chapter']}"

            if source.get('title'):
                citation += f": {source['title']}"

            if source.get('section'):
                citation += f" - {source['section']}"

            if self.include_scores:
                score = source.get('score', 0)
                citation += f" (relevance: {score:.2f})"

            lines.append(citation)

        return "\n".join(lines)

    def _format_bibliography(self, sources: List[Dict[str, Any]]) -> str:
        """Format citations as bibliography entries."""
        if not sources:
            return ""

        lines = ["References:"]
        for source in sources:
            # Build breadcrumb path
            breadcrumb = source.get('breadcrumb', [])
            if breadcrumb:
                path = " > ".join(breadcrumb)
            else:
                parts = [source['chapter']]
                if source.get('section'):
                    parts.append(source['section'])
                if source.get('subsection'):
                    parts.append(source['subsection'])
                path = " > ".join(parts)

            citation = f"- {path}"

            if self.include_scores:
                score = source.get('score', 0)
                citation += f"\n  Relevance: {score:.2f}"

            lines.append(citation)

        return "\n".join(lines)

    def _get_source_list(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Get list of sources for frontend display.

        Args:
            chunks: Search result chunks

        Returns:
            List of source dictionaries for UI
        """
        sources = []
        seen = set()

        for chunk in chunks:
            chapter = chunk.get('chapter', 'Unknown')
            title = chunk.get('title', chapter)
            key = (chapter, title)

            if key not in seen:
                seen.add(key)
                sources.append({
                    'chapter': chapter,
                    'title': title,
                    'section': chunk.get('section', ''),
                    'url': self._build_url(chunk)
                })

        return sources

    def _build_url(self, chunk: Dict[str, Any]) -> str:
        """
        Build URL to textbook section (for future navigation).

        Args:
            chunk: Chunk with metadata

        Returns:
            URL string (placeholder for now)
        """
        # Extract chapter number from chapter string (e.g., "Chapter 1" -> "1")
        chapter = chunk.get('chapter', '')
        chapter_num = ''.join(filter(str.isdigit, chapter))

        if chapter_num:
            return f"/docs/chapters/chapter{chapter_num}"

        return "/docs"

    def create_inline_citation(self, chunk: Dict[str, Any]) -> str:
        """
        Create a short inline citation for a single chunk.

        Args:
            chunk: Single search result chunk

        Returns:
            Short citation string
        """
        parts = []

        if chunk.get('chapter'):
            parts.append(chunk['chapter'])

        if chunk.get('header'):
            parts.append(chunk['header'])

        if not parts:
            return "Textbook"

        citation = " - ".join(parts)

        if self.include_scores and chunk.get('score'):
            citation += f" ({chunk['score']:.2f})"

        return citation


def create_citation_formatter(
    style: str = "inline",
    include_scores: bool = False
) -> CitationFormatter:
    """
    Factory function to create a citation formatter.

    Args:
        style: Citation style
        include_scores: Whether to include scores

    Returns:
        Configured CitationFormatter instance
    """
    return CitationFormatter(
        style=style,
        include_scores=include_scores
    )


# Example usage
if __name__ == "__main__":
    # Sample chunks (simulated search results)
    sample_chunks = [
        {
            'content': 'Physical AI refers to...',
            'chapter': 'Chapter 1',
            'chapter_number': 1,
            'title': 'Introduction to Physical AI',
            'section': 'Defining Physical AI',
            'header': 'What is Physical AI?',
            'score': 0.85,
            'breadcrumb': ['Chapter 1: Introduction', '1.1 Defining Physical AI']
        },
        {
            'content': 'Embodied intelligence...',
            'chapter': 'Chapter 1',
            'chapter_number': 1,
            'title': 'Introduction to Physical AI',
            'section': 'Embodied Intelligence',
            'header': 'Core Concepts',
            'score': 0.78,
            'breadcrumb': ['Chapter 1: Introduction', '1.2 Embodied Intelligence']
        },
        {
            'content': 'ROS 2 provides...',
            'chapter': 'Chapter 3',
            'chapter_number': 3,
            'title': 'Getting Started with ROS 2',
            'section': 'ROS 2 Basics',
            'header': 'Introduction to ROS 2',
            'score': 0.65,
            'breadcrumb': ['Chapter 3: ROS 2', '3.1 Basics']
        }
    ]

    # Test different styles
    for style in ['inline', 'footnote', 'bibliography']:
        print(f"\n{'=' * 70}")
        print(f"Style: {style.upper()}")
        print('=' * 70)

        formatter = create_citation_formatter(style=style, include_scores=True)
        result = formatter.format_citations(sample_chunks)

        print(result['formatted'])
        print(f"\nSources for UI: {len(result['sources'])} items")
