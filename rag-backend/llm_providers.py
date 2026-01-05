"""
Multi-LLM Provider Support with Automatic Fallback
Supports: OpenAI, Groq, Google Gemini, Ollama
"""
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

class LLMProvider:
    """Base class for LLM providers"""

    def __init__(self):
        self.provider_name = "base"

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate chat completion"""
        raise NotImplementedError

    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding"""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if provider is configured and available"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self):
        super().__init__()
        self.provider_name = "OpenAI"
        self.api_key = os.getenv("OPENAI_API_KEY")

        if self.api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def create_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


class GroqProvider(LLMProvider):
    """Groq (Fast, Free LLaMA models)"""

    def __init__(self):
        super().__init__()
        self.provider_name = "Groq"
        self.api_key = os.getenv("GROQ_API_KEY")

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Warning: groq package not installed. Run: pip install groq")
                self.client = None
        else:
            self.client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and capable (updated model)
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def create_embedding(self, text: str) -> List[float]:
        # Groq doesn't have embeddings, use OpenAI or local model
        # For now, use a simple fallback to OpenAI embeddings or sentence-transformers
        raise NotImplementedError("Groq doesn't provide embeddings. Use OpenAI or local model.")


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self):
        super().__init__()
        self.provider_name = "Google Gemini"
        self.api_key = os.getenv("GEMINI_API_KEY")

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
            except ImportError:
                print("Warning: google-generativeai package not installed. Run: pip install google-generativeai")
                self.model = None
        else:
            self.model = None

    def is_available(self) -> bool:
        return bool(self.api_key and self.model)

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        # Convert OpenAI message format to Gemini format
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")

        full_prompt = "\n\n".join(prompt_parts)

        response = self.model.generate_content(
            full_prompt,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
            }
        )
        return response.text

    def create_embedding(self, text: str) -> List[float]:
        # Gemini embeddings
        import google.generativeai as genai
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']


class OllamaProvider(LLMProvider):
    """Ollama (Local, completely free)"""

    def __init__(self):
        super().__init__()
        self.provider_name = "Ollama"
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        try:
            import requests
            # Test if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self.available = response.status_code == 200
        except:
            self.available = False

    def is_available(self) -> bool:
        return self.available

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        import requests

        # Convert messages to prompt
        prompt_parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            prompt_parts.append(f"{role.capitalize()}: {content}")

        full_prompt = "\n\n".join(prompt_parts) + "\n\nAssistant:"

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": "llama3.2",  # or llama2, mistral, etc.
                "prompt": full_prompt,
                "temperature": temperature,
                "stream": False
            },
            timeout=60
        )

        return response.json()['response']

    def create_embedding(self, text: str) -> List[float]:
        import requests

        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            },
            timeout=30
        )

        return response.json()['embedding']


class LLMManager:
    """Manages multiple LLM providers with automatic fallback"""

    def __init__(self):
        # Initialize all providers
        self.providers = {
            'openai': OpenAIProvider(),
            'groq': GroqProvider(),
            'gemini': GeminiProvider(),
            'ollama': OllamaProvider(),
        }

        # Determine priority order from env
        priority = os.getenv("LLM_PRIORITY", "groq,gemini,openai,ollama").split(",")
        self.priority_order = [p.strip() for p in priority]

        # Find first available provider
        self.current_provider = None
        for provider_name in self.priority_order:
            provider = self.providers.get(provider_name)
            if provider and provider.is_available():
                self.current_provider = provider
                print(f"[OK] Using LLM provider: {provider.provider_name}")
                break

        if not self.current_provider:
            raise RuntimeError("No LLM provider available! Configure at least one: GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, or run Ollama locally")

        # For embeddings, prefer OpenAI or Ollama (Groq/Gemini don't have good embedding APIs)
        self.embedding_provider = None
        for provider_name in ['openai', 'ollama', 'gemini']:
            provider = self.providers.get(provider_name)
            if provider and provider.is_available():
                try:
                    # Test if it supports embeddings
                    provider.create_embedding("test")
                    self.embedding_provider = provider
                    print(f"[OK] Using embedding provider: {provider.provider_name}")
                    break
                except NotImplementedError:
                    continue
                except:
                    continue

        if not self.embedding_provider:
            print("[WARN] No embedding provider available. Using sentence-transformers fallback.")
            self._init_local_embeddings()

    def _init_local_embeddings(self):
        """Initialize local sentence-transformers as fallback"""
        try:
            from sentence_transformers import SentenceTransformer
            self.local_embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[OK] Using local embeddings: sentence-transformers")
        except ImportError:
            print("[WARN] Install sentence-transformers for local embeddings: pip install sentence-transformers")
            self.local_embedding_model = None

    def chat_completion(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate chat completion with automatic fallback"""
        errors = []

        for provider_name in self.priority_order:
            provider = self.providers.get(provider_name)
            if not provider or not provider.is_available():
                continue

            try:
                result = provider.chat_completion(messages, temperature, max_tokens)
                return result
            except Exception as e:
                errors.append(f"{provider.provider_name}: {str(e)}")
                print(f"[FAIL] {provider.provider_name} failed, trying next provider...")
                continue

        raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")

    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding with fallback"""
        if self.embedding_provider:
            try:
                return self.embedding_provider.create_embedding(text)
            except:
                pass

        # Fallback to local model
        if hasattr(self, 'local_embedding_model') and self.local_embedding_model:
            return self.local_embedding_model.encode(text).tolist()

        raise RuntimeError("No embedding provider available")

    def get_current_provider_name(self) -> str:
        """Get name of current provider"""
        return self.current_provider.provider_name if self.current_provider else "None"


# Global instance
llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get or create LLM manager singleton"""
    global llm_manager
    if llm_manager is None:
        llm_manager = LLMManager()
    return llm_manager
