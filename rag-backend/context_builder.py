"""
Context builder for RAG prompts
Formats retrieved chunks into coherent context for LLM
"""
from typing import List, Dict, Any, Optional


class ContextBuilder:
    """
    Builds context from retrieved chunks for LLM prompts.
    """

    def __init__(
        self,
        max_context_length: int = 4000,
        include_metadata: bool = True,
        separator: str = "\n\n---\n\n"
    ):
        """
        Initialize the context builder.

        Args:
            max_context_length: Maximum characters for context
            include_metadata: Whether to include source metadata
            separator: Separator between chunks
        """
        self.max_context_length = max_context_length
        self.include_metadata = include_metadata
        self.separator = separator

    def build_context(
        self,
        chunks: List[Dict[str, Any]],
        query: Optional[str] = None
    ) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: List of search results with content and metadata
            query: Optional user query for context

        Returns:
            Formatted context string for LLM
        """
        if not chunks:
            return ""

        context_parts = []
        current_length = 0

        for i, chunk in enumerate(chunks):
            # Build chunk text
            chunk_text = self._format_chunk(chunk, index=i+1)
            chunk_length = len(chunk_text)

            # Check if adding this chunk exceeds limit
            if current_length + chunk_length > self.max_context_length:
                # Try to add partial chunk
                remaining = self.max_context_length - current_length
                if remaining > 200:  # Only add if we have reasonable space
                    partial_text = self._format_chunk(
                        chunk,
                        index=i+1,
                        max_length=remaining
                    )
                    context_parts.append(partial_text)
                break

            context_parts.append(chunk_text)
            current_length += chunk_length + len(self.separator)

        return self.separator.join(context_parts)

    def _format_chunk(
        self,
        chunk: Dict[str, Any],
        index: int,
        max_length: Optional[int] = None
    ) -> str:
        """
        Format a single chunk with metadata.

        Args:
            chunk: Chunk dictionary with content and metadata
            index: Index number for the chunk
            max_length: Optional maximum length for truncation

        Returns:
            Formatted chunk string
        """
        parts = []

        # Add metadata header if enabled
        if self.include_metadata:
            header = f"[Source {index}]"

            # Add chapter and section info
            if chunk.get('chapter'):
                header += f" {chunk['chapter']}"
            if chunk.get('header'):
                header += f" - {chunk['header']}"

            parts.append(header)

        # Add content
        content = chunk.get('content', '')

        # Truncate if needed
        if max_length and len(content) > max_length:
            # Try to truncate at sentence boundary
            truncated = content[:max_length]
            last_period = truncated.rfind('.')
            if last_period > max_length * 0.7:  # If we find a period in last 30%
                content = truncated[:last_period + 1] + "..."
            else:
                content = truncated + "..."

        parts.append(content)

        return "\n".join(parts)

    def build_prompt(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Build complete prompt with system message, context, and user query.

        Args:
            query: User's question
            chunks: Retrieved context chunks
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant for the Physical AI and Humanoid Robotics textbook.
Your role is to answer questions based ONLY on the provided context from the textbook.

Guidelines:
- Answer questions accurately using information from the context
- Cite specific chapters or sections when possible
- If the answer is not in the context, say "I don't have information about that in the textbook"
- Do not make up information or use knowledge outside the provided context
- Be concise but thorough in your explanations"""

        # Build context from chunks
        context = self.build_context(chunks, query=query)

        # Build user prompt
        if context:
            user_prompt = f"""Context from the textbook:

{context}

Question: {query}

Please answer based on the context above, citing relevant chapters or sections."""
        else:
            user_prompt = f"""Question: {query}

Note: No relevant context was found in the textbook for this question."""

        return {
            'system': system_prompt,
            'user': user_prompt
        }

    def get_context_stats(self, context: str) -> Dict[str, Any]:
        """
        Get statistics about the built context.

        Args:
            context: Built context string

        Returns:
            Dictionary with context statistics
        """
        return {
            'length': len(context),
            'chunks': context.count('[Source'),
            'max_length': self.max_context_length,
            'utilization': len(context) / self.max_context_length if self.max_context_length > 0 else 0
        }


def create_context_builder(
    max_context_length: int = 4000,
    include_metadata: bool = True
) -> ContextBuilder:
    """
    Factory function to create a context builder.

    Args:
        max_context_length: Maximum context length in characters
        include_metadata: Whether to include source metadata

    Returns:
        Configured ContextBuilder instance
    """
    return ContextBuilder(
        max_context_length=max_context_length,
        include_metadata=include_metadata
    )


# Example usage
if __name__ == "__main__":
    # Sample chunks (simulated search results)
    sample_chunks = [
        {
            'content': 'Physical AI refers to artificial intelligence systems that interact with and learn from the physical world through embodied agents.',
            'chapter': 'Chapter 1',
            'header': 'Defining Physical AI',
            'score': 0.85
        },
        {
            'content': 'Embodied intelligence emphasizes the importance of physical interaction and sensorimotor experience in developing intelligent behavior.',
            'chapter': 'Chapter 1',
            'header': 'Embodied Intelligence',
            'score': 0.78
        }
    ]

    # Create builder
    builder = create_context_builder(max_context_length=4000)

    # Build context
    context = builder.build_context(sample_chunks)
    print("Built Context:")
    print(context)
    print("\n" + "=" * 70 + "\n")

    # Build complete prompt
    query = "What is physical AI?"
    prompt_dict = builder.build_prompt(query, sample_chunks)

    print("System Prompt:")
    print(prompt_dict['system'])
    print("\n" + "=" * 70 + "\n")

    print("User Prompt:")
    print(prompt_dict['user'])
    print("\n" + "=" * 70 + "\n")

    # Get stats
    stats = builder.get_context_stats(context)
    print("Context Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
