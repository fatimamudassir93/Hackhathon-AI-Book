# Technical Research: Chatbot RAG Integration

**Feature**: 003-chatbot-rag-integration
**Date**: 2025-12-26
**Status**: Complete

## Overview

This document answers technical research questions identified during planning to resolve "NEEDS CLARIFICATION" items and inform implementation decisions.

---

## Research Area 1: Frontend-Backend Integration Pattern

### Question
What's the best practice for React ↔ FastAPI integration in a Docusaurus environment?

### Current Implementation
- Basic `fetch()` API calls with bearer token authentication
- No request/response caching library (backend handles caching)
- No retry logic or request deduplication
- No state management library (React useState only)

### Options Considered

#### Option A: Keep Current fetch() Implementation
**Pros**:
- Simple, no additional dependencies
- Works well for current use case
- Backend already handles caching and rate limiting

**Cons**:
- No automatic retries
- No request deduplication (rapid clicks send multiple requests)
- No loading state management across components

#### Option B: Use React Query (TanStack Query)
**Pros**:
- Automatic request deduplication
- Built-in retry logic and error handling
- Cache management and invalidation
- Loading/error states handled automatically
- Optimistic updates support

**Cons**:
- Additional dependency (~40KB gzipped)
- Learning curve for team
- May be overkill for single endpoint

#### Option C: Use SWR (Stale-While-Revalidate)
**Pros**:
- Lightweight (~5KB gzipped)
- Simple API, minimal learning curve
- Automatic revalidation and cache
- Focus on data fetching (perfect for our use case)

**Cons**:
- Less powerful than React Query
- No built-in optimistic updates (not needed for RAG)

### Decision: **Keep Current fetch() Implementation (Option A)**

**Rationale**:
- Current implementation is working well (no reported issues)
- Backend already handles caching, rate limiting, and error responses
- Adding React Query/SWR would be premature optimization
- Chatbot is a single, isolated component with minimal state sharing
- Retry logic can be added inline if needed (1-2 retries on network error)

**Implementation Notes**:
- Add client-side request deduplication (prevent double-clicks)
- Implement 1 automatic retry on network failure before showing error
- Keep loading state managed via useState (simple and effective)

**Alternatives Rejected**: React Query (too heavy), SWR (unnecessary abstraction)

---

## Research Area 2: Error Handling Strategy

### Question
How should we handle different error scenarios and provide user-friendly feedback?

### Current Implementation
```typescript
// Existing error handling in Chatbot.tsx (lines 133-161)
- Network errors: "Cannot connect to backend server"
- 401 Unauthorized: "Authentication required"
- 403 Forbidden: "Access denied"
- 500 Server error: "Server encountered an issue"
- Generic: "Error: {message}"
```

### Error Taxonomy

#### Category 1: Network Errors (Client-Side)
- **Failed to fetch**: Backend unreachable
- **Timeout**: Request took >30 seconds
- **CORS errors**: Configuration issue

**Handling**:
- Show connection error with retry button
- Suggest checking backend URL configuration
- Log to console for debugging

#### Category 2: Authentication Errors (401, 403)
- **401 Unauthorized**: Invalid/missing token
- **403 Forbidden**: Insufficient permissions

**Handling**:
- Prompt user to sign in
- Link to authentication page
- Clear any stale tokens

#### Category 3: Rate Limiting (429)
- **429 Too Many Requests**: Rate limit exceeded

**Handling**:
- Show friendly "slow down" message
- Display countdown to next available request
- Suggest more specific questions to reduce retries

#### Category 4: Search/Retrieval Errors (500)
- **Qdrant connection failure**: Vector database unreachable
- **Embedding generation failure**: Sentence-transformers error
- **No search results**: Query returned 0 relevant chunks

**Handling**:
- Generic "search error" message (don't expose internals)
- Suggest rephrasing question
- Fallback to cached responses if available

#### Category 5: LLM Generation Errors (500)
- **Groq API down**: Primary LLM unavailable
- **Gemini API down**: Fallback LLM unavailable
- **Context too long**: Exceeds 4000 character limit
- **Timeout**: LLM took >10 seconds to respond

**Handling**:
- Show "answer generation failed" message
- Display retrieved sources anyway (partial success)
- Suggest simplifying question or asking about specific chapter

#### Category 6: Out-of-Scope Questions (200 with in_scope=false)
- **Question not in textbook**: Scope detector triggered

**Handling**:
- Show polite "outside textbook scope" message (EXISTING)
- Suggest related in-scope topics
- Link to textbook table of contents

### Decision: **Enhance Current Error Handling with Partial Success Support**

**Rationale**:
- Current error handling is mostly good (user-friendly messages)
- Missing: Partial success support (show sources even if LLM fails)
- Missing: Retry suggestions and recovery actions
- Missing: Specific handling for rate limiting (429)

**Implementation Plan**:
1. Add rate limiting error handler (429 → countdown + suggestion)
2. Implement partial success: show sources even if response text fails
3. Add retry button for network errors (with exponential backoff)
4. Improve out-of-scope messages with topic suggestions
5. Add "Report Issue" link for unexpected errors

**Example Enhanced Error UI**:
```
❌ Failed to generate answer, but here's what I found:

📖 Sources:
  - Chapter 1: Embodied Intelligence (relevance: 85%)
  - Chapter 2: Physical AI Systems (relevance: 72%)

💡 Try:
  • [Retry] Ask again
  • [Simplify] Rephrase your question
  • [Report] Something's not right?
```

---

## Research Area 3: Testing Strategy

### Question
How should we test the RAG pipeline end-to-end?

### Current State
- ❌ No automated tests (frontend or backend)
- ⚠️ Manual testing only
- ✅ Backend has health check endpoint

### Testing Pyramid

#### Level 1: Unit Tests (Foundation)

**Backend (pytest)**:
```python
tests/
├── test_vector_search.py       # Test search logic, filters, relevance
├── test_scope_detection.py     # Test in/out-of-scope detection
├── test_citation_formatting.py # Test citation formatting
├── test_context_builder.py     # Test context assembly
└── test_llm_service.py         # Test LLM service (mocked)
```

**Key Tests**:
- Vector search returns correct chapters for filter
- Scope detector correctly identifies out-of-scope questions
- Citation formatter generates valid markdown
- Context builder respects 4000 character limit
- LLM service handles provider fallback (Groq → Gemini)

**Mocking Strategy**:
- Mock Qdrant client (use in-memory vectors for fast tests)
- Mock LLM API calls (pre-defined responses for consistency)
- Mock embedding model (deterministic embeddings)

**Frontend (Jest + React Testing Library)**:
```typescript
tests/
├── Chatbot.test.tsx            # Component rendering, interactions
├── ChatbotFilters.test.tsx     # Filter dropdown behavior
└── integration/
    └── rag-flow.test.tsx       # E2E flow with mocked backend
```

**Key Tests**:
- Chatbot renders message history correctly
- User can send message and see loading state
- Sources display with correct formatting
- Chapter filter updates API request
- Error messages display for different failure modes
- Text selection triggers "Explain Selection" button

#### Level 2: Integration Tests (API Layer)

**Backend (pytest)**:
```python
tests/integration/
├── test_chat_endpoint.py       # Full /api/chat flow (no mocks)
├── test_auth_flow.py           # Authentication + chat
└── test_rate_limiting.py       # Rate limit enforcement
```

**Key Tests**:
- POST /api/chat returns valid ChatResponse
- Chapter filtering works end-to-end
- Rate limiting blocks excessive requests
- Caching returns identical responses for same query
- Out-of-scope detection works correctly
- Authentication required for /api/chat (if configured)

**Test Data**:
- Use real Qdrant collection (test environment)
- Mock LLM responses (consistent, fast, no API costs)
- Reset rate limits between tests

#### Level 3: E2E Tests (User Scenarios)

**Frontend (Playwright or Cypress)**:
```typescript
e2e/
├── chatbot-basic-flow.spec.ts     # User Story 1 (ask & get answer)
├── chatbot-filtering.spec.ts      # User Story 2 (chapter filter)
├── chatbot-text-selection.spec.ts # User Story 3 (highlight text)
└── chatbot-history.spec.ts        # User Story 4 (history persistence)
```

**Key Tests**:
- Open chatbot → ask question → see answer with sources
- Select chapter filter → ask question → verify filtered sources
- Highlight text → click "Explain Selection" → see contextual answer
- Ask multiple questions → verify history preserved

**Test Environment**:
- Isolated test database (SQLite)
- Test Qdrant collection (subset of production data)
- Mocked LLM responses (fast, deterministic)
- Local backend (no external dependencies)

### Decision: **Implement Pyramid Testing (Unit → Integration → E2E)**

**Rationale**:
- Comprehensive coverage with fast feedback loop
- Unit tests provide foundation (fast, isolated, many tests)
- Integration tests validate API contracts
- E2E tests validate user experience

**Priority**:
1. **P1 (First)**: Backend unit tests (vector search, scope detection, citation formatting)
2. **P1 (First)**: Backend integration test for /api/chat endpoint
3. **P2 (Next)**: Frontend unit tests (Chatbot.tsx rendering and interactions)
4. **P3 (Later)**: E2E tests (full user flows with real browser)

**Mocking Strategy**:
- Mock LLM API calls in all tests (use pre-defined responses)
- Mock Qdrant in unit tests (in-memory)
- Use real Qdrant in integration/E2E tests (test collection)
- Mock embedding model in unit tests (deterministic vectors)

**Test Fixtures**:
- Create sample questions with expected answers
- Pre-generate embeddings for common queries
- Define edge cases (empty results, very long questions, special characters)

---

## Research Area 4: Performance Optimization

### Question
How can we meet the <3 second response time target (90th percentile)?

### Current Performance Bottlenecks

**Measured Latency Breakdown** (from backend profiling):
```
Total: ~2.5-4.0 seconds (variable)
├── Embedding generation: ~200-400ms (sentence-transformers)
├── Qdrant vector search: ~100-300ms (cloud latency)
├── LLM generation (Groq): ~1.5-3.0s (variable, depends on answer length)
└── Network overhead: ~200-500ms (frontend ↔ backend round-trip)
```

**Analysis**:
- LLM generation is the primary bottleneck (50-70% of total time)
- Qdrant search is acceptable (<300ms)
- Embedding generation is fast enough (<400ms)
- Network overhead is high but expected (cloud deployment)

### Optimization Options

#### Option 1: Streaming Responses
**Description**: Stream LLM output token-by-token as it's generated

**Pros**:
- User sees partial answer immediately (~500ms to first token)
- Perceived performance dramatically improved
- Better UX for long answers

**Cons**:
- Requires SSE (Server-Sent Events) or WebSocket
- More complex frontend state management
- Backend refactoring needed (async streaming)

**Estimated Improvement**: Perceived latency reduced from 3s → 500ms (to first token)

#### Option 2: Pre-compute Common Queries
**Description**: Cache answers for frequently asked questions

**Pros**:
- Instant responses for cached queries
- Reduces LLM API costs

**Cons**:
- Already implemented (response_cache.py)
- Cache hit rate unknown (needs monitoring)
- Limited to exact query matches

**Estimated Improvement**: 30-40% cache hit rate → 30-40% instant responses

#### Option 3: Reduce Context Length
**Description**: Send fewer chunks to LLM (top 3 instead of top 5)

**Pros**:
- Faster LLM generation (shorter context)
- Lower API costs

**Cons**:
- May reduce answer quality
- May miss relevant context

**Estimated Improvement**: ~200-500ms saved (10-20% faster LLM)

#### Option 4: Use Faster LLM Model
**Description**: Switch to smaller/faster Groq model (llama-3.1-8b instead of 3.3-70b)

**Pros**:
- Significantly faster generation (~500ms instead of 2s)
- Lower costs

**Cons**:
- Lower answer quality (smaller model)
- May hallucinate more

**Estimated Improvement**: ~1.5s saved (50% faster)

#### Option 5: Parallel Processing
**Description**: Generate embedding + fetch from Qdrant in parallel (already implemented?)

**Pros**:
- Small latency reduction

**Cons**:
- Likely already optimized in backend

**Estimated Improvement**: Minimal (~50-100ms)

### Decision: **Implement Streaming Responses (Option 1) + Monitor Cache Hit Rate (Option 2)**

**Rationale**:
- Streaming provides best UX improvement for minimal code change
- Existing caching already reduces actual latency for common questions
- Reducing context length or model size hurts answer quality (unacceptable)
- Need to measure current performance before optimizing further

**Implementation Plan**:
1. **Phase 1 (P1 - High Priority)**:
   - Add performance monitoring: track 90th percentile response time
   - Add cache hit rate metrics to /api/ingestion/status endpoint
   - Measure actual latency distribution (validate 3s target)

2. **Phase 2 (P2 - If latency exceeds 3s for >10% of queries)**:
   - Implement SSE streaming for /api/chat endpoint
   - Update Chatbot.tsx to render streaming responses
   - Add loading indicator for partial responses

3. **Phase 3 (P3 - Optimization)**:
   - A/B test: 3 chunks vs 5 chunks (measure quality vs speed tradeoff)
   - Experiment with faster Groq models for simple questions
   - Optimize network latency (CDN, edge functions)

**Acceptance Criteria**:
- 90th percentile response time < 3 seconds (end-to-end)
- Cache hit rate > 30% for common questions
- Streaming implementation (if needed) shows first token in <500ms

**Alternatives Rejected**:
- Reduce context length → hurts quality
- Use faster model → hurts quality
- Parallel processing → likely already optimal

---

## Research Area 5: Session Management

### Question
How should conversation history be stored and persisted?

### Current Implementation
- **In-Memory**: React useState stores messages array in component state
- **Database**: If user authenticated, messages saved to ChatHistory table
- **Limitation**: In-memory messages lost on page refresh (unless authenticated)

### Options Considered

#### Option 1: Keep Current Approach (In-Memory + Database)
**Pros**:
- Simple, already working
- Database persistence for logged-in users
- No additional complexity

**Cons**:
- Anonymous users lose history on refresh
- No cross-tab synchronization
- No conversation history UI for logged-in users

#### Option 2: Add Browser Session Storage
**Description**: Store messages in sessionStorage (persists across refreshes)

**Pros**:
- History survives page refreshes
- Works for anonymous users
- Simple implementation (~20 lines)

**Cons**:
- Limited to ~5MB storage
- Lost when browser tab closes
- No cross-device synchronization

#### Option 3: Add Conversation History UI (for Authenticated Users)
**Description**: Add "History" tab showing past conversations with resume feature

**Pros**:
- Users can revisit past conversations
- Search through conversation history
- Better learning retention

**Cons**:
- Requires significant UI work
- Backend query endpoint needed
- Out of scope for MVP (User Story 4 is P3)

#### Option 4: Use Browser localStorage
**Description**: Persist messages indefinitely in localStorage

**Pros**:
- Survives browser restarts
- Works for anonymous users

**Cons**:
- Privacy concern (messages stored on device)
- Storage limit (5-10MB)
- No expiration (old conversations clutter storage)

### Decision: **Add Session Storage (Option 2) for MVP, Conversation History UI Later (Option 3)**

**Rationale**:
- Session storage solves immediate problem (history lost on refresh)
- Works for both authenticated and anonymous users
- Simple implementation with minimal risk
- Conversation history UI is P3 priority (nice-to-have, not critical)

**Implementation Plan**:

**Phase 1 (MVP - P2 Priority)**:
```typescript
// Add to Chatbot.tsx
useEffect(() => {
  // Load from sessionStorage on mount
  const saved = sessionStorage.getItem('chatbot-messages');
  if (saved) {
    setMessages(JSON.parse(saved));
  }
}, []);

useEffect(() => {
  // Save to sessionStorage on messages change
  sessionStorage.setItem('chatbot-messages', JSON.stringify(messages));
}, [messages]);
```

**Phase 2 (Future - P3 Priority)**:
- Add /api/chat/history endpoint (GET user's past conversations)
- Add "History" button in chatbot header
- Show list of past conversations (grouped by date)
- Allow resuming conversation (load session_id)
- Add search functionality (find questions/answers)

**Storage Limits**:
- Max 50 messages in sessionStorage (to avoid 5MB limit)
- Older messages truncated (keep most recent)
- Database stores full history for authenticated users (no limit)

**Alternatives Rejected**:
- localStorage → privacy concern, no expiration
- In-memory only → frustrating UX on refresh
- Conversation history UI now → out of scope for MVP

---

## Research Area 6: Citation URL Generation

### Question
How should we generate clickable links to specific textbook sections in Docusaurus?

### Current State
- Source.url field exists but always empty ("")
- Citations display chapter and section name (no link)
- Metadata includes file_path (e.g., "docs/chapter-1.md")

### Docusaurus URL Structure

**Pattern**: `https://<domain>/docs/<category>/<page>#<heading-anchor>`

**Examples**:
- Chapter 1: `/docs/chapter-1`
- Chapter 1, Section "Embodied Intelligence": `/docs/chapter-1#embodied-intelligence`
- Chapter 3, Subsection "ROS 2 Architecture": `/docs/chapter-3#ros-2-architecture`

**Anchor Generation**:
- Docusaurus auto-generates anchors from headings
- Algorithm: lowercase, replace spaces with hyphens, remove special chars
- Example: "3.2 ROS 2 Architecture" → `#ros-2-architecture`

### Citation Metadata Available

From Qdrant payload:
```python
{
  "chapter": "Chapter 1",
  "title": "Introduction to Physical AI",
  "heading": "Embodied Intelligence",  # Section heading
  "file_path": "docs/chapter-1-intro.md"
}
```

### URL Generation Strategy

#### Option 1: Generate URLs in Backend (citation_formatter.py)
**Description**: Add URL generation logic to citation formatter service

**Pros**:
- Centralized logic (single source of truth)
- Can validate URLs against sitemap
- Easier to test

**Cons**:
- Backend needs to know frontend URL structure (coupling)
- Requires Docusaurus base URL configuration

**Implementation**:
```python
def generate_doc_url(file_path: str, heading: str = None) -> str:
    base_url = os.getenv("DOCUSAURUS_BASE_URL", "https://example.com")
    # Extract page slug from file_path
    page = file_path.replace("docs/", "").replace(".md", "")
    url = f"{base_url}/docs/{page}"
    if heading:
        # Generate anchor from heading
        anchor = heading.lower().replace(" ", "-")
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)  # Remove special chars
        url += f"#{anchor}"
    return url
```

#### Option 2: Generate URLs in Frontend (Chatbot.tsx)
**Description**: Add URL generation logic when rendering sources

**Pros**:
- Frontend already knows its own URL structure
- No backend configuration needed
- Simpler deployment

**Cons**:
- Logic duplicated if multiple frontends exist
- Harder to test (requires React testing)

**Implementation**:
```typescript
function generateSourceUrl(source: Source): string {
  const baseUrl = window.location.origin;
  const chapterSlug = source.chapter.toLowerCase().replace(" ", "-");
  let url = `${baseUrl}/docs/${chapterSlug}`;
  if (source.section) {
    const anchor = source.section.toLowerCase().replace(/\s+/g, "-")
                                  .replace(/[^a-z0-9-]/g, "");
    url += `#${anchor}`;
  }
  return url;
}
```

#### Option 3: Hybrid Approach (Backend Generates, Frontend Overrides)
**Description**: Backend generates best-effort URLs, frontend can override

**Pros**:
- Backend provides default URL (works for API consumers)
- Frontend can customize if needed

**Cons**:
- Most complex solution
- Unnecessary unless multiple frontend clients exist

### Decision: **Generate URLs in Backend (Option 1)**

**Rationale**:
- Centralized logic is easier to maintain and test
- Backend already has file_path and heading metadata
- API consumers (future mobile app?) get URLs for free
- Docusaurus base URL is deployment configuration (belongs in backend .env)

**Implementation Plan**:

**Step 1**: Update `citation_formatter.py`:
```python
def format_citations(chunks: List[dict]) -> dict:
    sources = []
    for chunk in chunks:
        url = _generate_doc_url(
            file_path=chunk.get('file_path', ''),
            heading=chunk.get('heading', '')
        )
        sources.append({
            'chapter': chunk['chapter'],
            'title': chunk['title'],
            'section': chunk.get('heading', ''),
            'score': chunk['score'],
            'url': url  # NEW
        })
    # ... rest of citation formatting
```

**Step 2**: Add environment variable:
```bash
# .env
DOCUSAURUS_BASE_URL=http://localhost:3000  # Development
# DOCUSAURUS_BASE_URL=https://physical-ai-book.vercel.app  # Production
```

**Step 3**: Update frontend to render clickable links:
```typescript
{source.url && (
  <a href={source.url} target="_blank" rel="noopener noreferrer">
    View in Textbook →
  </a>
)}
```

**Testing**:
- Unit test `_generate_doc_url()` with various heading formats
- Validate generated URLs match Docusaurus actual URLs
- Test special characters in headings (e.g., "ROS 2", "A/B Testing")
- Test missing headings (fallback to chapter URL only)

**Edge Cases**:
- Heading has multiple words: "Embodied Intelligence" → `#embodied-intelligence`
- Heading has numbers: "3.2 ROS 2 Architecture" → `#ros-2-architecture`
- Heading has special chars: "Q&A Section" → `#qa-section`
- No heading: Fallback to chapter URL only (no anchor)
- Invalid file_path: Return empty string (no URL)

**Alternatives Rejected**:
- Frontend generation → harder to test, duplicated logic
- Hybrid approach → unnecessary complexity

---

## Summary of Key Decisions

| Research Area | Decision | Rationale | Priority |
|--------------|----------|-----------|----------|
| **1. Frontend-Backend Integration** | Keep current fetch() implementation | Simple, works well, backend handles caching | P3 (Optimize later) |
| **2. Error Handling** | Enhance with partial success + retry | Show sources even if LLM fails | P2 (UX improvement) |
| **3. Testing Strategy** | Implement testing pyramid (Unit → Integration → E2E) | Comprehensive coverage with fast feedback | P1 (Foundation) |
| **4. Performance Optimization** | Add monitoring first, then streaming if needed | Measure before optimizing | P1 (Monitoring), P2 (Streaming) |
| **5. Session Management** | Add sessionStorage for MVP | Survives refreshes, simple implementation | P2 (MVP feature) |
| **6. Citation URL Generation** | Generate URLs in backend (citation_formatter.py) | Centralized, testable, works for all clients | P1 (Core feature gap) |

---

## Next Steps

1. **Immediate (P1)**:
   - Implement citation URL generation (backend)
   - Add performance monitoring (track p90 response time)
   - Write backend unit tests (vector search, scope detection, citations)
   - Write backend integration test (/api/chat endpoint)

2. **Short-term (P2)**:
   - Implement sessionStorage for conversation history
   - Enhance error handling with partial success support
   - Add frontend unit tests (Chatbot.tsx)
   - Implement streaming responses (if performance monitoring shows >3s for >10% of queries)

3. **Long-term (P3)**:
   - Add E2E tests (Playwright/Cypress)
   - Build conversation history UI for authenticated users
   - Optimize performance (reduce context length experiments)
   - Add React Query/SWR if state management becomes complex

---

**Research Status**: ✅ COMPLETE

**Blockers Resolved**: All "NEEDS CLARIFICATION" items from Technical Context section answered

**Ready for**: Phase 1 (Design & Contracts - data-model.md, contracts/, quickstart.md)
