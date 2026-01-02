# ADR-001: Chatbot Uses RAG with Vector Database Ingestion

> **Scope**: This ADR documents the decision cluster for how the chatbot provides answers to user questions, including the retrieval mechanism, knowledge source, and integration architecture.

- **Status:** Accepted
- **Date:** 2025-12-26
- **Feature:** 003-chatbot-rag-integration
- **Context:** The Physical AI textbook needs an intelligent chatbot that can answer student questions accurately, cite sources, and stay current with book updates. Traditional approaches (hardcoded Q&A, fine-tuned models) have limitations in accuracy, maintenance, and cost.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: YES - Long-term consequence for how chatbot provides answers, affects accuracy, freshness, and maintenance
     2) Alternatives: YES - Multiple viable options (fine-tuning, hardcoded, semantic search without LLM)
     3) Scope: YES - Cross-cutting concern affecting chatbot UI (003), ingestion pipeline (002), and backend architecture
-->

## Decision

**We will use Retrieval-Augmented Generation (RAG) architecture with vector database ingestion to power the chatbot:**

- **Knowledge Source**: Qdrant vector database containing 246 embedded chunks from the Physical AI textbook
- **Retrieval Mechanism**: Semantic search using sentence-transformers (all-MiniLM-L6-v2) for query embeddings + cosine similarity search
- **Generation**: LLM (Groq or Gemini) generates answers using retrieved context as grounding
- **Ingestion Pipeline**: Automated chunking (500-1500 chars) → embedding → Qdrant upload with metadata (chapter, section, source)
- **Integration**: FastAPI backend exposes `/api/chat` endpoint; React chatbot calls endpoint with user query + optional filters

## Consequences

### Positive

- **Accuracy with Citations**: RAG grounds answers in actual textbook content, with automatic source citations (chapter, section, relevance score)
- **Freshness**: Content updates require only re-ingestion (minutes), not model retraining (hours/days)
- **Cost-Effective**: No expensive fine-tuning; uses smaller embedding models + prompt-based LLM calls
- **Transparency**: Users see exactly which textbook sections informed the answer, building trust
- **Filtering Capability**: Chapter-based filtering is straightforward with metadata-tagged vectors
- **Scalability**: Qdrant can handle millions of vectors; easy to add more content sources
- **Quality Control**: Can validate ingestion quality (246/246 vectors verified) and search effectiveness independently

### Negative

- **Complexity**: Requires maintaining 3 components: ingestion pipeline, Qdrant database, and RAG backend
- **Latency**: Two-step process (retrieval + generation) adds ~1-3 seconds vs. instant hardcoded responses
- **Infrastructure**: Qdrant Cloud dependency introduces additional service to monitor and maintain
- **Embedding Model Lock-In**: Changing embedding models requires full re-ingestion of all content
- **Context Window Limits**: Can only retrieve limited chunks (typically 3-5) due to LLM context limits
- **Retrieval Failures**: Semantic search may miss relevant content if query phrasing differs significantly from source text
- **Cost Scaling**: LLM API calls cost money; high usage could become expensive (mitigated by using Groq free tier)

## Alternatives Considered

### Alternative A: Fine-Tuned LLM
**Approach**: Fine-tune Llama or similar open-source model on the entire textbook

**Pros**:
- Single model, simpler architecture
- No dependency on external vector database
- Potentially faster inference (no retrieval step)

**Cons**:
- Expensive and time-consuming to retrain on content updates
- No built-in source citations (hallucination risk)
- Requires significant GPU resources for training
- Hard to validate what the model "knows" vs. hallucinates

**Why Rejected**: Cost, maintenance burden, and lack of citations make this unsuitable for educational content that changes frequently

### Alternative B: Hardcoded Q&A Database
**Approach**: Manually curate question-answer pairs; use keyword/fuzzy matching

**Pros**:
- Fully controlled, predictable responses
- Instant response time
- No LLM costs
- Easy to debug

**Cons**:
- Requires manual creation of hundreds of Q&A pairs
- Cannot handle novel or rephrased questions
- High maintenance burden as textbook evolves
- Poor user experience for unexpected questions

**Why Rejected**: Does not scale with textbook size (6 chapters, 246 chunks); inflexible to natural language variation

### Alternative C: Semantic Search Only (No LLM Generation)
**Approach**: Return raw textbook chunks matching the query; no answer synthesis

**Pros**:
- Simpler architecture (no LLM integration)
- Faster response time
- Lower cost (no LLM API calls)

**Cons**:
- Poor user experience: users must read raw chunks themselves
- No synthesis of information from multiple sources
- Cannot answer questions requiring reasoning or comparison

**Why Rejected**: Degrades to "fancy search" rather than conversational assistant; does not meet user expectation of direct answers

## References

- Feature Spec: [003-chatbot-rag-integration/spec.md](../../specs/003-chatbot-rag-integration/spec.md)
- Implementation: Chatbot.tsx (frontend) + RAG Backend (FastAPI) + Qdrant Vector DB
- Related Features:
  - [002-book-code-ingestion](../../specs/002-book-code-ingestion/spec.md) - Ingestion pipeline that populates Qdrant
- Validation Results:
  - Ingestion: 246/246 vectors successfully uploaded
  - Retrieval: Test query "What is embodied intelligence?" returns relevant Chapter 1 content (score: 0.6065)
  - Integration: Existing Chatbot.tsx already calls `/api/chat` endpoint

## Implementation Notes

**Current Status** (as of 2025-12-26):
- ✅ Qdrant collection created: `physical_ai_book` (246 vectors, 384 dimensions, cosine similarity)
- ✅ Ingestion pipeline operational: 10 files → 246 chunks → embeddings → Qdrant
- ✅ Embedding model: all-MiniLM-L6-v2 (sentence-transformers)
- ✅ Backend API: FastAPI with `/api/chat` endpoint (existing)
- ✅ Frontend: Chatbot.tsx with chapter filtering, text selection, conversation history
- ⏳ RAG integration: Pending (spec complete, implementation needed)

**Success Metrics** (from spec 003):
- SC-001: 95% of questions receive answers with citations
- SC-002: Responses within 3 seconds (90th percentile)
- SC-005: 80% first-time user success within 30 seconds

**Risk Mitigation**:
- **Latency**: Use streaming responses if generation exceeds 3 seconds
- **Cost**: Start with Groq free tier; implement caching for common questions
- **Retrieval Quality**: Monitor feedback (thumbs up/down) to identify poor retrievals
- **Embedding Lock-In**: Document re-ingestion process; keep it fast (17 seconds for full re-index)
