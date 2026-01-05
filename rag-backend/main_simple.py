from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from openai import OpenAI
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Physical AI Book RAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "physical_ai_book"
EMBEDDING_MODEL = "text-embedding-3-small"  # or text-embedding-3-large

# Request/Response models
class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]

class UpsertRequest(BaseModel):
    chunk_id: str
    text: str
    metadata: dict

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    filter_metadata: Optional[dict] = None

class QueryResult(BaseModel):
    text: str
    score: float
    metadata: dict

class QueryResponse(BaseModel):
    results: List[QueryResult]

# Endpoints
@app.get("/")
async def root():
    return {"message": "Physical AI Book RAG API", "status": "running"}

@app.post("/embed", response_model=EmbedResponse)
async def embed_text(request: EmbedRequest):
    """Generate embedding for given text using OpenAI"""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=request.text
        )
        embedding = response.data[0].embedding
        return EmbedResponse(embedding=embedding)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

@app.post("/upsert")
async def upsert_document(request: UpsertRequest):
    """Embed and upsert a document chunk to Qdrant"""
    try:
        # Generate embedding
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=request.text
        )
        embedding = response.data[0].embedding

        # Upsert to Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=request.chunk_id,
                    vector=embedding,
                    payload={
                        "text": request.text,
                        **request.metadata
                    }
                )
            ]
        )

        return {"status": "success", "chunk_id": request.chunk_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upsert error: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query similar documents from Qdrant using semantic search"""
    try:
        # Generate query embedding
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=request.query
        )
        query_embedding = response.data[0].embedding

        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=request.top_k,
            query_filter=models.Filter(**request.filter_metadata) if request.filter_metadata else None
        )

        # Format results
        results = [
            QueryResult(
                text=hit.payload.get("text", ""),
                score=hit.score,
                metadata={k: v for k, v in hit.payload.items() if k != "text"}
            )
            for hit in search_result
        ]

        return QueryResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Qdrant connection
        collections = qdrant_client.get_collections()
        collection_exists = any(c.name == COLLECTION_NAME for c in collections.collections)

        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collection_exists": collection_exists
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
