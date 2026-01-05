"""
Context augmentation for selected text queries
Combines selected text with retrieved chunks for better contextual understanding
"""
from typing import List, Dict, Any, Optional


class ContextAugmenter:
    """
    Augments context by intelligently combining selected text with retrieved chunks.
    """

    def __init__(
        self,
        selected_text_weight: float = 1.5,
        max_selected_text_length: int = 500
    ):
        """
        Initialize the context augmenter.

        Args:
            selected_text_weight: Weight multiplier for selected text relevance
            max_selected_text_length: Maximum length of selected text to include
        """
        self.selected_text_weight = selected_text_weight
        self.max_selected_text_length = max_selected_text_length

    def augment_context(
        self,
        chunks: List[Dict[str, Any]],
        selected_text: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Augment retrieved chunks with selected text context.

        Args:
            chunks: Retrieved chunks from vector search
            selected_text: Text selected by user
            query: User's question

        Returns:
            Dictionary with augmented context and metadata
        """
        # Truncate selected text if too long
        truncated_text = self._truncate_selected_text(selected_text)

        # Build augmented context
        context_parts = []

        # Add selected text context header
        context_parts.append(self._build_selected_text_header(truncated_text, query))

        # Add retrieved chunks that relate to selected text
        relevant_chunks = self._filter_relevant_chunks(chunks, selected_text)

        # Combine into final context
        augmented_context = {
            'selected_text': truncated_text,
            'query': query,
            'chunks': relevant_chunks,
            'combined_chunks': chunks,  # Keep all chunks for fallback
            'has_selected_text': True,
            'context_header': context_parts[0]
        }

        return augmented_context

    def _truncate_selected_text(self, text: str) -> str:
        """
        Truncate selected text to maximum length.

        Args:
            text: Selected text

        Returns:
            Truncated text
        """
        if len(text) <= self.max_selected_text_length:
            return text

        # Truncate at sentence boundary if possible
        truncated = text[:self.max_selected_text_length]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')

        boundary = max(last_period, last_newline)
        if boundary > self.max_selected_text_length * 0.7:
            return text[:boundary + 1] + "..."

        return truncated + "..."

    def _build_selected_text_header(self, selected_text: str, query: str) -> str:
        """
        Build header section for selected text context.

        Args:
            selected_text: The selected text
            query: User's question

        Returns:
            Formatted header string
        """
        header = f"""**Selected Text Context:**

{selected_text}

**Question about the selected text:**
{query}

**Related Information from Textbook:**
"""
        return header

    def _filter_relevant_chunks(
        self,
        chunks: List[Dict[str, Any]],
        selected_text: str
    ) -> List[Dict[str, Any]]:
        """
        Filter and rank chunks by relevance to selected text.

        Args:
            chunks: Retrieved chunks
            selected_text: Selected text to compare against

        Returns:
            Filtered and ranked chunks
        """
        # Simple keyword overlap scoring
        selected_keywords = set(selected_text.lower().split())

        scored_chunks = []
        for chunk in chunks:
            content = chunk.get('content', '')
            chunk_keywords = set(content.lower().split())

            # Calculate overlap score
            overlap = len(selected_keywords & chunk_keywords)
            overlap_score = overlap / max(len(selected_keywords), 1)

            # Boost original score by overlap
            original_score = chunk.get('score', 0)
            boosted_score = original_score + (overlap_score * 0.2)

            scored_chunks.append({
                **chunk,
                'original_score': original_score,
                'boosted_score': boosted_score,
                'overlap_score': overlap_score
            })

        # Sort by boosted score
        scored_chunks.sort(key=lambda x: x['boosted_score'], reverse=True)

        return scored_chunks

    def build_augmented_prompt(
        self,
        augmented_context: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Build LLM prompt with augmented context.

        Args:
            augmented_context: Augmented context from augment_context()
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant for the Physical AI and Humanoid Robotics textbook.
The user has selected a specific piece of text and is asking a question about it.

Guidelines:
- Focus your answer on the selected text context provided
- Use additional textbook information to provide complete answers
- Reference the selected text when relevant
- Cite specific chapters or sections when appropriate
- If the selected text and question don't match well, acknowledge it"""

        # Build user prompt with augmented context
        header = augmented_context['context_header']

        # Add relevant chunks
        chunks_text = []
        for i, chunk in enumerate(augmented_context['chunks'][:5], 1):
            chunks_text.append(
                f"[Source {i}] {chunk.get('chapter', 'Unknown')}\n"
                f"{chunk.get('content', '')}"
            )

        context_str = "\n\n".join(chunks_text)

        user_prompt = f"""{header}

{context_str}

Please provide a detailed answer to the question, considering both the selected text and the related information from the textbook."""

        return {
            'system': system_prompt,
            'user': user_prompt
        }


def create_context_augmenter(
    selected_text_weight: float = 1.5,
    max_selected_text_length: int = 500
) -> ContextAugmenter:
    """
    Factory function to create a context augmenter.

    Args:
        selected_text_weight: Weight multiplier for selected text
        max_selected_text_length: Max length of selected text

    Returns:
        Configured ContextAugmenter instance
    """
    return ContextAugmenter(
        selected_text_weight=selected_text_weight,
        max_selected_text_length=max_selected_text_length
    )


# Example usage
if __name__ == "__main__":
    # Sample data
    selected_text = """
    Inverse Kinematics (IK) is crucial for humanoid robot control.
    Given a desired end-effector position, IK computes the joint angles needed to achieve that position.
    """

    query = "How does IK help with reaching tasks?"

    sample_chunks = [
        {
            'content': 'Inverse kinematics is used in robotic manipulation for precise positioning...',
            'chapter': 'Chapter 4',
            'score': 0.75
        },
        {
            'content': 'Forward kinematics computes position from joint angles...',
            'chapter': 'Chapter 4',
            'score': 0.65
        },
        {
            'content': 'End-effector control is essential for manipulation tasks...',
            'chapter': 'Chapter 5',
            'score': 0.70
        }
    ]

    # Create augmenter
    augmenter = create_context_augmenter()

    # Augment context
    augmented = augmenter.augment_context(sample_chunks, selected_text, query)

    print("Augmented Context:")
    print(f"Selected text length: {len(augmented['selected_text'])}")
    print(f"Number of chunks: {len(augmented['chunks'])}")
    print(f"\nContext Header:\n{augmented['context_header']}")

    # Build prompt
    prompt = augmenter.build_augmented_prompt(augmented)
    print(f"\n{'='*70}")
    print("User Prompt:")
    print(prompt['user'][:500] + "...")
