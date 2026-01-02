"""
Enhanced FastAPI backend for Physical AI Book
Features: RAG Chat, Authentication, Personalization, Translation
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import json
import uuid
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

# Import our modules
from database import get_db, engine
from models import User, UserProfile, ChatHistory, PersonalizationCache, Base
from auth import (
    UserCreate, UserLogin, UserResponse, Token,
    create_user, authenticate_user, create_access_token,
    get_current_user, get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from llm_providers import get_llm_manager

load_dotenv()

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Physical AI Book Enhanced API",
    description="RAG Chat, Auth, Personalization & Translation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
llm_manager = get_llm_manager()
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "physical_ai_book"


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    selected_text: Optional[str] = None
    use_history: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    session_id: str

class PersonalizeRequest(BaseModel):
    chapter_id: str
    chapter_content: str

class TranslateRequest(BaseModel):
    chapter_id: str
    chapter_content: str
    target_language: str = "ur"  # Urdu

class PersonalizationResponse(BaseModel):
    chapter_id: str
    content: str
    language: str


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with technical background
    """
    try:
        user = create_user(db, user_data)

        # Create access token
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return Token(access_token=access_token)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup error: {str(e)}")


@app.post("/api/auth/signin", response_model=Token)
async def signin(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(access_token=access_token)


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user profile
    """
    profile_data = None
    if current_user.profile:
        profile_data = {
            "technical_level": current_user.profile.technical_level,
            "programming_experience": current_user.profile.programming_experience,
            "robotics_background": current_user.profile.robotics_background,
            "learning_goals": current_user.profile.learning_goals,
            "preferred_language": current_user.profile.preferred_language
        }

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        profile=profile_data
    )


# ============================================================================
# ENHANCED RAG CHAT ENDPOINTS
# ============================================================================

def get_relevant_context(query: str, top_k: int = 5, selected_text: Optional[str] = None) -> List[dict]:
    """
    Get relevant context from Qdrant with better source attribution
    """
    # If selected text is provided, use it as additional context
    search_query = query
    if selected_text:
        search_query = f"Context: {selected_text}\n\nQuestion: {query}"

    # Generate embedding using LLM manager
    query_embedding = llm_manager.create_embedding(search_query)

    # Search in Qdrant
    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k
    )

    # Format results with better attribution
    sources = []
    for hit in search_result:
        sources.append({
            "text": hit.payload.get("text", ""),
            "score": hit.score,
            "chapter": hit.payload.get("chapter", "Unknown"),
            "title": hit.payload.get("title", ""),
            "heading": hit.payload.get("heading", ""),
            "file_path": hit.payload.get("file_path", "")
        })

    return sources


def generate_rag_response(query: str, sources: List[dict], user_profile: Optional[UserProfile] = None) -> str:
    """
    Generate response using OpenAI with RAG context and user personalization
    """
    # Build context from sources
    context_parts = []
    for i, source in enumerate(sources, 1):
        context_parts.append(
            f"[Source {i}] Chapter: {source['chapter']}\n"
            f"Section: {source['heading']}\n"
            f"Content: {source['text']}\n"
        )

    context = "\n\n".join(context_parts)

    # Build system prompt with personalization
    system_prompt = "You are an expert AI assistant for the Physical AI & Humanoid Robotics textbook."

    if user_profile:
        system_prompt += f"""

User Profile:
- Technical Level: {user_profile.technical_level}
- Programming Experience: {', '.join(user_profile.programming_experience) if user_profile.programming_experience else 'Not specified'}
- Robotics Background: {user_profile.robotics_background}
- Learning Goals: {user_profile.learning_goals or 'Not specified'}

Please tailor your response to match the user's technical level and background.
"""

    system_prompt += """

Instructions:
1. Answer the question using ONLY the provided textbook sources
2. Be clear and concise
3. Reference specific chapters/sections when relevant
4. If the sources don't contain enough information, say so
5. Format your response in markdown for readability
"""

    # Call LLM manager (supports multiple providers)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context from textbook:\n\n{context}\n\nQuestion: {query}"}
    ]

    return llm_manager.chat_completion(messages, temperature=0.7, max_tokens=1000)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Enhanced RAG chat endpoint with:
    - Better source attribution
    - User profile awareness
    - Optional text selection context
    - Chat history tracking
    """
    try:
        # Get or create session ID
        session_id = request.session_id or str(uuid.uuid4())

        # Get relevant sources
        sources = get_relevant_context(
            query=request.message,
            top_k=5,
            selected_text=request.selected_text
        )

        # Get user profile for personalization
        user_profile = current_user.profile if current_user else None

        # Generate response
        response_text = generate_rag_response(
            query=request.message,
            sources=sources,
            user_profile=user_profile
        )

        # Save to chat history if user is logged in
        if current_user:
            # Save user message
            user_message = ChatHistory(
                user_id=current_user.id,
                session_id=uuid.UUID(session_id),
                role="user",
                content=request.message
            )
            db.add(user_message)

            # Save assistant response
            assistant_message = ChatHistory(
                user_id=current_user.id,
                session_id=uuid.UUID(session_id),
                role="assistant",
                content=response_text,
                sources=[{
                    "chapter": s["chapter"],
                    "heading": s["heading"],
                    "score": s["score"]
                } for s in sources[:3]]  # Save top 3 sources
            )
            db.add(assistant_message)
            db.commit()

        return ChatResponse(
            response=response_text,
            sources=sources,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ============================================================================
# PERSONALIZATION ENDPOINT
# ============================================================================

@app.post("/api/personalize/{chapter_id}", response_model=PersonalizationResponse)
async def personalize_chapter(
    chapter_id: str,
    request: PersonalizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Personalize chapter content based on user's technical background
    Caches the result for faster subsequent loads
    """
    try:
        # Check cache first
        cached = db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == current_user.id,
            PersonalizationCache.chapter_id == chapter_id,
            PersonalizationCache.language == 'en'
        ).first()

        if cached:
            return PersonalizationResponse(
                chapter_id=chapter_id,
                content=cached.personalized_content,
                language='en'
            )

        # Get user profile
        profile = current_user.profile
        if not profile:
            raise HTTPException(status_code=400, detail="User profile not found")

        # Build personalization prompt
        system_prompt = f"""You are an expert educational content adapter. Personalize the following chapter content for this user:

Technical Level: {profile.technical_level}
Programming Experience: {', '.join(profile.programming_experience) if profile.programming_experience else 'None specified'}
Robotics Background: {profile.robotics_background}
Learning Goals: {profile.learning_goals or 'Not specified'}

Personalization Instructions:
1. Adjust complexity: {'Simplify concepts' if profile.technical_level == 'beginner' else 'Add advanced details' if profile.technical_level == 'advanced' else 'Maintain moderate complexity'}
2. Add relevant examples: {'More basic examples and explanations' if profile.technical_level == 'beginner' else 'Advanced use cases and edge cases' if profile.technical_level == 'advanced' else 'Practical examples'}
3. Adapt format: Present information in a way that matches their learning style and background
4. Keep all original chapter structure (headings, code blocks, etc.) but enhance the content
5. Output in markdown format

Original chapter content follows:
"""

        # Call LLM manager to personalize
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.chapter_content}
        ]

        personalized_content = llm_manager.chat_completion(messages, temperature=0.7, max_tokens=4000)

        # Cache the result
        cache_entry = PersonalizationCache(
            user_id=current_user.id,
            chapter_id=chapter_id,
            personalized_content=personalized_content,
            language='en'
        )
        db.add(cache_entry)
        db.commit()

        return PersonalizationResponse(
            chapter_id=chapter_id,
            content=personalized_content,
            language='en'
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalization error: {str(e)}")


# ============================================================================
# TRANSLATION ENDPOINT
# ============================================================================

@app.post("/api/translate/{chapter_id}", response_model=PersonalizationResponse)
async def translate_chapter(
    chapter_id: str,
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Translate chapter content to Urdu
    Caches the result for faster subsequent loads
    """
    try:
        target_lang = request.target_language

        # Check cache first
        cached = db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == current_user.id,
            PersonalizationCache.chapter_id == chapter_id,
            PersonalizationCache.language == target_lang
        ).first()

        if cached:
            return PersonalizationResponse(
                chapter_id=chapter_id,
                content=cached.personalized_content,
                language=target_lang
            )

        # Build translation prompt
        system_prompt = f"""You are an expert translator specializing in technical and educational content.

Task: Translate the following chapter from the Physical AI & Humanoid Robotics textbook into Urdu.

Instructions:
1. Maintain all markdown formatting (headings, code blocks, lists, etc.)
2. Keep code blocks and technical terms in English where appropriate
3. Translate explanations and descriptions into clear, natural Urdu
4. Preserve the structure and organization of the content
5. Use appropriate technical terminology in Urdu when available
6. Keep the same level of technical depth

Original chapter content follows:
"""

        # Call LLM manager to translate
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.chapter_content}
        ]

        translated_content = llm_manager.chat_completion(messages, temperature=0.3, max_tokens=4000)

        # Cache the result
        cache_entry = PersonalizationCache(
            user_id=current_user.id,
            chapter_id=chapter_id,
            personalized_content=translated_content,
            language=target_lang
        )
        db.add(cache_entry)
        db.commit()

        return PersonalizationResponse(
            chapter_id=chapter_id,
            content=translated_content,
            language=target_lang
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Physical AI Book Enhanced API",
        "version": "2.0.0",
        "features": [
            "RAG Chat with source attribution",
            "User authentication",
            "Content personalization",
            "Urdu translation",
            "Chat history tracking"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Qdrant connection
        collections = qdrant_client.get_collections()
        collection_exists = any(c.name == COLLECTION_NAME for c in collections.collections)

        # Check database connection
        from database import engine
        with engine.connect() as conn:
            db_connected = True

        return {
            "status": "healthy",
            "qdrant_connected": True,
            "qdrant_collection_exists": collection_exists,
            "database_connected": db_connected
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
