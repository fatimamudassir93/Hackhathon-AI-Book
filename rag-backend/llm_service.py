"""
LLM service for generating RAG responses
Uses Groq API with context injection from retrieved chunks
"""
import os
from typing import List, Dict, Any, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """
    Service for generating responses using LLM with RAG context.
    """

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        api_key: Optional[str] = None
    ):
        """
        Initialize the LLM service.

        Args:
            model: Groq model name
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            api_key: Optional Groq API key (defaults to env)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize Groq client
        api_key = api_key or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        self.client = Groq(api_key=api_key)

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the LLM.

        Args:
            system_prompt: System instructions
            user_prompt: User query with context
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Dictionary with response and metadata
        """
        # Use defaults if not provided
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=temp,
                max_tokens=tokens,
                top_p=1,
                stream=False
            )

            # Extract response
            response_text = chat_completion.choices[0].message.content
            finish_reason = chat_completion.choices[0].finish_reason

            # Get usage stats
            usage = chat_completion.usage

            return {
                'response': response_text,
                'finish_reason': finish_reason,
                'model': self.model,
                'usage': {
                    'prompt_tokens': usage.prompt_tokens,
                    'completion_tokens': usage.completion_tokens,
                    'total_tokens': usage.total_tokens
                },
                'success': True
            }

        except Exception as e:
            return {
                'response': '',
                'error': str(e),
                'success': False
            }

    def generate_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response with RAG context.

        Args:
            query: User's question
            context: Retrieved context from vector search
            system_prompt: Optional custom system prompt

        Returns:
            Response dictionary
        """
        # Default system prompt for textbook QA
        if system_prompt is None:
            system_prompt = """You are a helpful AI assistant for the Physical AI and Humanoid Robotics textbook.
Your role is to answer questions based ONLY on the provided context from the textbook.

Guidelines:
- Answer questions accurately using information from the context
- Cite specific chapters or sections when possible (e.g., "According to Chapter 1...")
- If the answer is not in the context, clearly state: "I don't have information about that in the textbook"
- Do not make up information or use knowledge outside the provided context
- Be concise but thorough in your explanations
- Use technical terms appropriately when they appear in the context"""

        # Build user prompt with context
        if context:
            user_prompt = f"""Context from the textbook:

{context}

Question: {query}

Please answer based on the context above. Cite relevant chapters or sections in your response."""
        else:
            user_prompt = f"""Question: {query}

Note: No relevant context was found in the textbook for this question. Please let the user know."""

        return self.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    def generate_streaming(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None
    ):
        """
        Generate a streaming response (for future use).

        Args:
            system_prompt: System instructions
            user_prompt: User query with context
            temperature: Override default temperature

        Yields:
            Response chunks as they arrive
        """
        temp = temperature if temperature is not None else self.temperature

        try:
            stream = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=temp,
                max_tokens=self.max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error: {str(e)}"

    def check_api_health(self) -> bool:
        """
        Check if Groq API is accessible.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Simple test request
            response = self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'OK' if you can hear me.",
                max_tokens=10
            )
            return response.get('success', False)
        except:
            return False

    def get_available_models(self) -> List[str]:
        """
        Get list of available Groq models.

        Returns:
            List of model names
        """
        # Common Groq models (as of current knowledge)
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]


def create_llm_service(
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> LLMService:
    """
    Factory function to create an LLM service.

    Args:
        model: Groq model name
        temperature: Sampling temperature
        max_tokens: Maximum response tokens

    Returns:
        Configured LLMService instance
    """
    return LLMService(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


# Example usage
if __name__ == "__main__":
    # Create service
    try:
        llm_service = create_llm_service()

        # Test health check
        print("Checking API health...")
        if llm_service.check_api_health():
            print("✓ Groq API is healthy\n")
        else:
            print("✗ Groq API check failed\n")
            exit(1)

        # Test simple response
        print("Testing simple query...")
        result = llm_service.generate_response(
            system_prompt="You are a helpful assistant.",
            user_prompt="Explain what physical AI is in one sentence."
        )

        if result['success']:
            print(f"Response: {result['response']}")
            print(f"Tokens used: {result['usage']['total_tokens']}\n")
        else:
            print(f"Error: {result.get('error')}\n")

        # Test with context
        print("Testing with context...")
        sample_context = """[Source 1] Chapter 1 - Defining Physical AI
Physical AI refers to artificial intelligence systems that interact with and learn from the physical world through embodied agents. Unlike purely software-based AI, Physical AI requires sensors, actuators, and a physical presence."""

        query = "What is physical AI?"
        result = llm_service.generate_with_context(
            query=query,
            context=sample_context
        )

        if result['success']:
            print(f"Query: {query}")
            print(f"Response: {result['response']}")
            print(f"Tokens used: {result['usage']['total_tokens']}")
        else:
            print(f"Error: {result.get('error')}")

    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("  Make sure GROQ_API_KEY is set in your .env file")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
