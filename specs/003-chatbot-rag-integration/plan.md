# Implementation Plan: Chatbot RAG Integration

**Branch**: `003-chatbot-rag-integration` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-chatbot-rag-integration/spec.md`

## Summary

Integrate the existing Docusaurus chatbot (Chatbot.tsx) with the RAG backend (FastAPI `/api/chat` endpoint) to enable intelligent, context-aware answers from the Physical AI textbook with source citations, chapter filtering, and text selection support. The majority of this integration is already implemented; this plan documents the architecture and identifies remaining work.

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.14 (Backend)
**Primary Dependencies**:
- Frontend: React 18+, Docusaurus, AuthContext
- Backend: FastAPI, Qdrant Client, Sentence Transformers, Groq/Gemini LLMs

**Storage**:
- Vector Database: Qdrant Cloud (`physical_ai_book` collection, 246 vectors, 384 dimensions)
- Relational Database: SQLite/PostgreSQL (user profiles, chat history, personalization cache)
- Session Storage: Browser localStorage (conversation history fallback)

**Testing**: pytest (Backend), Jest/React Testing Library (Frontend planned)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge 90+), responsive mobile support
**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- 90th percentile response time < 3 seconds (retrieval + generation)
- Support 10+ concurrent users without degradation
- Cache hit rate > 30% for common questions

**Constraints**:
- Network latency frontend ↔ backend < 500ms
- LLM context window: 4000 characters max
- Session storage limit: 50 messages max
- Rate limit: ~10 requests per minute per user

**Scale/Scope**:
- 246 textbook chunks across 6 chapters
- Expected usage: 50-100 students, 5-20 questions per session
- Conversation history: up to 50 messages per session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution file is currently a template placeholder (`.specify/memory/constitution.md`). No specific constitutional principles have been defined yet.

**Status**: ⚠️ N/A (Constitution not yet defined)

**Recommendation**: Define constitution principles for this project covering:
1. Test-First Development (TDD requirements)
2. API Contract Stability (versioning, breaking changes)
3. Error Handling Standards (user-friendly messages, logging)
4. Security Requirements (AuthN/AuthZ, data privacy)
5. Performance Budgets (response times, resource limits)

## Project Structure

### Documentation (this feature)

```text
specs/003-chatbot-rag-integration/
├── plan.md              # This file
├── spec.md              # Feature specification (✅ complete)
├── research.md          # Technical research (Phase 0)
├── data-model.md        # Data models and entities (Phase 1)
├── quickstart.md        # Developer setup guide (Phase 1)
├── contracts/           # API contracts (Phase 1)
│   └── chat-api.yaml    # OpenAPI spec for /api/chat endpoint
└── checklists/
    └── requirements.md  # Spec validation checklist (✅ complete)
```

### Source Code (repository root)

```text
# Frontend (Docusaurus site)
physical-ai-book/
├── src/
│   ├── components/
│   │   ├── Chatbot.tsx              # ✅ Main chatbot component (EXISTING)
│   │   ├── Chatbot.module.css       # ✅ Chatbot styles (EXISTING)
│   │   ├── ChatbotFilters.tsx       # ✅ Chapter filter dropdown (EXISTING)
│   │   └── ChatbotFilters.module.css # ✅ Filter styles (EXISTING)
│   ├── context/
│   │   └── AuthContext.tsx          # ✅ Authentication provider (EXISTING)
│   └── pages/
│       └── [docusaurus pages]
└── docs/
    └── chatbot-guide.md             # 🔄 User documentation (NEW - needed)

# Backend (FastAPI)
rag-backend/
├── main.py                          # ✅ FastAPI app with /api/chat (EXISTING)
├── vector_search.py                 # ✅ Qdrant search service (EXISTING)
├── context_builder.py               # ✅ Context assembly (EXISTING)
├── citation_formatter.py            # ✅ Source citation formatting (EXISTING)
├── llm_service.py                   # ✅ LLM generation service (EXISTING)
├── scope_detector.py                # ✅ In/out-of-scope detection (EXISTING)
├── rate_limiter.py                  # ✅ Rate limiting (EXISTING)
├── response_cache.py                # ✅ Response caching (EXISTING)
├── auth.py                          # ✅ User authentication (EXISTING)
├── database.py                      # ✅ Database models/sessions (EXISTING)
├── models.py                        # ✅ SQLAlchemy models (EXISTING)
└── llm_providers.py                 # ✅ Multi-provider LLM manager (EXISTING)

# Tests (to be created)
physical-ai-book/tests/              # 🔄 Frontend tests (NEW - needed)
├── Chatbot.test.tsx                 # Unit tests for Chatbot component
├── ChatbotFilters.test.tsx          # Unit tests for filters
└── integration/
    └── rag-integration.test.tsx     # E2E tests for RAG flow

rag-backend/tests/                   # 🔄 Backend tests (NEW - needed)
├── test_chat_endpoint.py            # API endpoint tests
├── test_vector_search.py            # Vector search tests
├── test_scope_detection.py          # Scope detector tests
└── test_citation_formatting.py      # Citation formatter tests
```

**Structure Decision**: Web application structure with separate frontend (React/Docusaurus) and backend (FastAPI/Python) directories. Frontend handles UI/UX, backend handles RAG logic, vector search, and LLM generation. Communication via REST API (`/api/chat` endpoint).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations to track - Constitution not yet defined.*

## Phase 0: Outline & Research

### Research Questions

Based on Technical Context analysis, the following areas need research and documentation:

1. **Frontend-Backend Integration Pattern**
   - Research: Best practices for React ↔ FastAPI integration in Docusaurus
   - Current state: Basic fetch() calls with bearer token auth
   - Questions: Should we use React Query? Streaming responses? WebSockets?

2. **Error Handling Strategy**
   - Research: User-friendly error messages for different failure modes
   - Current state: Basic try/catch with HTTP status code handling
   - Questions: How to handle partial failures (search succeeds, LLM fails)?

3. **Testing Strategy**
   - Research: E2E testing for RAG pipelines (query → search → generation → display)
   - Current state: No automated tests
   - Questions: How to mock LLM responses? How to test chat history persistence?

4. **Performance Optimization**
   - Research: Techniques to meet <3 second response time target
   - Current state: Caching implemented, profiling available
   - Questions: Should we pre-generate embeddings? Use streaming responses?

5. **Session Management**
   - Research: Best practices for conversation history storage
   - Current state: In-memory messages array, database persistence if authenticated
   - Questions: How long to retain history? How to handle page refreshes?

6. **Citation URL Generation**
   - Research: How to generate clickable links to specific textbook sections
   - Current state: URL field exists but not populated
   - Questions: Docusaurus URL structure? Anchor linking strategy?

### Research Outcomes

To be documented in `research.md` after investigation.

## Phase 1: Design & Contracts

### Data Model

Key entities and their relationships (to be detailed in `data-model.md`):

**Frontend Entities**:
1. **ChatMessage** (TypeScript interface - EXISTING in Chatbot.tsx:14-21)
   - role: 'user' | 'assistant'
   - content: string | object (for error handling)
   - sources?: Source[]
   - citations?: string
   - in_scope?: boolean
   - error?: boolean
   - timestamp?: Date (NEW - add for history sorting)
   - feedback?: {rating: 'positive' | 'negative', comment?: string} (NEW - for user feedback)

2. **Source** (TypeScript interface - EXISTING in Chatbot.tsx:6-12)
   - chapter: string
   - title: string
   - section?: string
   - score: number (0.0 to 1.0 relevance)
   - url?: string (clickable link to source location)

3. **ChapterFilter** (TypeScript type - IMPLICIT in ChatbotFilters.tsx)
   - value: string | null ('all' or chapter number)
   - label: string (display name)

**Backend Entities** (Pydantic models - EXISTING in main.py:140-178):
1. **ChatRequest**
   - message: string
   - session_id?: string (UUID)
   - selected_text?: string (for contextual queries)
   - chapter_filter?: string (chapter number or null)
   - use_history: bool (default: true)

2. **ChatResponse**
   - response: string (LLM-generated answer)
   - sources: List[Source]
   - citations: string (formatted citation text)
   - session_id: string (UUID)
   - in_scope: bool (whether question was answerable from textbook)

3. **Source** (Pydantic model - EXISTING in main.py:151-156)
   - chapter: string
   - title: string
   - section?: string
   - score: float
   - url?: string

**Database Models** (SQLAlchemy - EXISTING in models.py):
1. **User** (authentication)
2. **UserProfile** (personalization preferences)
3. **ChatHistory** (conversation persistence)
4. **PersonalizationCache** (cached LLM responses)

### API Contracts

#### POST /api/chat

**Status**: ✅ FULLY IMPLEMENTED (main.py:428-649)

**Contract Details** (to be formalized in `contracts/chat-api.yaml`):

```yaml
openapi: 3.0.0
info:
  title: Physical AI Book RAG Chat API
  version: 2.0.0

paths:
  /api/chat:
    post:
      summary: RAG-powered chat endpoint
      description: |
        Retrieves relevant textbook content via vector search and generates
        contextualized answers using LLM with source citations.

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [message]
              properties:
                message:
                  type: string
                  description: User's question
                  example: "What is embodied intelligence?"
                session_id:
                  type: string
                  format: uuid
                  description: Session identifier for conversation tracking
                selected_text:
                  type: string
                  description: Text selected by user for contextual queries
                chapter_filter:
                  type: string
                  description: Filter results to specific chapter (e.g., "Chapter 1")
                use_history:
                  type: boolean
                  default: true
                  description: Include conversation history in context

      responses:
        200:
          description: Successful response with answer and sources
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                    description: LLM-generated answer
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        chapter: {type: string}
                        title: {type: string}
                        section: {type: string}
                        score: {type: number, format: float}
                        url: {type: string}
                  citations:
                    type: string
                    description: Formatted citation text
                  session_id:
                    type: string
                    format: uuid
                  in_scope:
                    type: boolean
                    description: Whether question was in textbook scope

        401:
          description: Authentication required (if token invalid/missing)
        429:
          description: Rate limit exceeded
        500:
          description: Server error (search, LLM, or general failure)
```

#### GET /api/chapters

**Status**: ✅ IMPLEMENTED (main.py:826-858)

Returns list of available chapters for filter dropdown.

#### GET /health

**Status**: ✅ IMPLEMENTED (main.py:937-957)

Health check for Qdrant and database connectivity.

### Integration Points

1. **Frontend → Backend**
   - Authentication: Bearer token in Authorization header
   - API URL: Configurable via `apiUrl` prop (default: `http://localhost:8000`)
   - Error handling: HTTP status codes mapped to user-friendly messages

2. **Backend → Qdrant**
   - Collection: `physical_ai_book`
   - Query: Sentence-transformers embedding (all-MiniLM-L6-v2, 384 dims)
   - Filters: Metadata filter for chapter_filter parameter

3. **Backend → LLM**
   - Providers: Groq (primary), Gemini (fallback)
   - Model: llama-3.3-70b-versatile (Groq)
   - Context window: 4000 characters max
   - Temperature: 0.7 (balanced creativity/consistency)

### Developer Quickstart

To be documented in `quickstart.md`:

**Backend Setup**:
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables (.env):
   - QDRANT_HOST, QDRANT_API_KEY
   - GROQ_API_KEY (and/or GEMINI_API_KEY)
   - DATABASE_URL (optional, defaults to SQLite)
3. Run server: `uvicorn main:app --reload --port 8000`
4. Verify health: `curl http://localhost:8000/health`

**Frontend Setup**:
1. Install dependencies: `npm install`
2. Configure API URL in Chatbot component or via environment variable
3. Run Docusaurus: `npm run start`
4. Open chatbot via floating button on any page

**Testing RAG Integration**:
1. Open browser console to see API calls
2. Ask test question: "What is embodied intelligence?"
3. Verify sources appear with chapter citations
4. Test chapter filtering with dropdown

## Phase 2: Implementation Tasks

*This section is NOT filled by `/sp.plan`. Use `/sp.tasks` command to generate actionable task list.*

**Placeholder for `/sp.tasks` output**:
- Task 1: Write integration tests for chat endpoint
- Task 2: Add frontend unit tests for Chatbot component
- Task 3: Implement citation URL generation (Docusaurus anchors)
- Task 4: Add user feedback UI (thumbs up/down)
- Task 5: Create user documentation (chatbot-guide.md)
- Task 6: Performance optimization (streaming responses?)
- Task 7: Accessibility audit (keyboard navigation, screen readers)

## Current Implementation Status

### ✅ COMPLETED (Already Working)

1. **Backend RAG Pipeline** (main.py):
   - ✅ `/api/chat` endpoint with full RAG workflow
   - ✅ Vector search with Qdrant (vector_search.py)
   - ✅ Context building (context_builder.py)
   - ✅ Citation formatting (citation_formatter.py)
   - ✅ Scope detection (scope_detector.py)
   - ✅ Rate limiting (rate_limiter.py)
   - ✅ Response caching (response_cache.py)
   - ✅ User authentication and profiles (auth.py, models.py)
   - ✅ Chat history persistence (database.py)
   - ✅ Performance profiling (/api/performance/metrics)

2. **Frontend Chatbot** (Chatbot.tsx):
   - ✅ Chat UI with floating button
   - ✅ Message display with sources and citations
   - ✅ Chapter filtering (ChatbotFilters.tsx)
   - ✅ Text selection and contextual queries
   - ✅ Error handling with user-friendly messages
   - ✅ Loading states and auto-scroll
   - ✅ Keyboard navigation (Enter to send)
   - ✅ Authentication integration (AuthContext)

3. **Ingestion Pipeline** (from feature 002):
   - ✅ 246 vectors ingested and validated
   - ✅ Metadata (chapter, title, section, source path)
   - ✅ Deduplication and cleanup

### 🔄 IN PROGRESS / NEEDS WORK

1. **Testing**:
   - ❌ No automated tests (frontend or backend)
   - ❌ E2E testing strategy undefined
   - ⚠️ Manual testing only

2. **Documentation**:
   - ❌ User guide for chatbot (chatbot-guide.md)
   - ❌ API contract formalization (contracts/chat-api.yaml)
   - ⚠️ Developer quickstart incomplete

3. **Features (from spec)**:
   - ❌ Citation URLs not populated (Source.url field empty)
   - ❌ User feedback UI (thumbs up/down) not implemented
   - ⚠️ Session storage conversation history (currently in-memory only)

4. **Performance**:
   - ⚠️ No streaming response support (responses can take >3 seconds)
   - ⚠️ No measurement of 90th percentile response time
   - ✅ Caching implemented but hit rate unknown

5. **Accessibility**:
   - ⚠️ Screen reader support not validated
   - ⚠️ Keyboard navigation partial (Enter works, Esc to close missing)
   - ⚠️ ARIA labels incomplete

### ⏭️ NEXT STEPS (Recommended Priority Order)

1. **High Priority** (P1 - Core Functionality Gaps):
   - Write integration tests for `/api/chat` endpoint
   - Implement citation URL generation (link to specific sections)
   - Add performance monitoring (track 90th percentile response time)
   - Create user documentation (how to use chatbot)

2. **Medium Priority** (P2 - UX Improvements):
   - Implement user feedback UI (thumbs up/down buttons)
   - Add streaming response support for long answers
   - Improve error messages with recovery suggestions
   - Implement session storage for conversation history persistence

3. **Lower Priority** (P3 - Polish):
   - Complete accessibility audit and fixes
   - Add frontend unit tests (Chatbot.test.tsx)
   - Create developer quickstart guide
   - Formalize API contracts (OpenAPI spec)

## Risk Analysis

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| LLM API outages (Groq/Gemini down) | High (chatbot unusable) | Medium | Implement multi-provider fallback (DONE), add error message with retry suggestion |
| Slow response times (>3 sec) | Medium (poor UX) | Medium | Implement streaming responses, optimize context size, add loading indicators (DONE) |
| Qdrant connection failures | High (no search results) | Low | Health check monitoring (DONE), graceful degradation with cached responses (DONE) |
| Inaccurate or hallucinated answers | High (trust issue) | Medium | Scope detection (DONE), source citations (DONE), user feedback mechanism (TODO) |
| Rate limiting blocking legitimate users | Medium (access denial) | Low | Adjust rate limits, implement per-user quotas, clear error messages (DONE) |
| Citation URLs broken/incorrect | Low (minor inconvenience) | High | Test URL generation, fallback to chapter name only |
| Session history data loss | Low (minor annoyance) | Medium | Implement session storage backup (TODO) |

## Validation Criteria (Definition of Done)

Before marking this feature as complete, verify:

### Functional Requirements (from spec.md)

- [ ] FR-001: Chatbot accepts natural language questions ✅ DONE
- [ ] FR-002: Answers displayed with formatting (markdown) ✅ DONE
- [ ] FR-003: Source citations shown (chapter, section, score, link) ⚠️ PARTIAL (URLs missing)
- [ ] FR-004: Chapter filtering functional ✅ DONE
- [ ] FR-005: Text highlight detection ✅ DONE
- [ ] FR-006: Selected text sent as context ✅ DONE
- [ ] FR-007: Conversation history preserved ⚠️ PARTIAL (in-memory only)
- [ ] FR-008: Loading state indicator ✅ DONE
- [ ] FR-009: Error handling for all failure modes ✅ DONE
- [ ] FR-010: Feedback collection (thumbs up/down) ❌ TODO
- [ ] FR-011: Out-of-scope indicator ✅ DONE
- [ ] FR-012: Accessible from all pages (floating button) ✅ DONE
- [ ] FR-013: Keyboard navigation and screen reader support ⚠️ PARTIAL (needs audit)

### Success Criteria (from spec.md)

- [ ] SC-001: 95% question accuracy with citations → Needs user testing
- [ ] SC-002: <3 second response time for 90% of queries → Needs measurement
- [ ] SC-003: 100% chapter filtering accuracy → Manual testing confirms ✅
- [ ] SC-004: 100% text highlight feature success → Manual testing confirms ✅
- [ ] SC-005: 80% first-time user success within 30 seconds → Needs user testing
- [ ] SC-006: 100% clear error messages → Manual review confirms ✅
- [ ] SC-007: 100% conversation history preservation → Needs session storage implementation
- [ ] SC-008: 100% mobile accessibility → Needs mobile testing

### Testing Checklist

- [ ] Backend unit tests (vector search, scope detection, citation formatting)
- [ ] Backend integration tests (/api/chat end-to-end)
- [ ] Frontend unit tests (Chatbot.tsx, ChatbotFilters.tsx)
- [ ] E2E tests (user asks question → sees cited answer)
- [ ] Performance tests (measure p90 response time)
- [ ] Accessibility audit (WCAG 2.1 AA compliance)
- [ ] Mobile responsive testing (iOS Safari, Android Chrome)
- [ ] Error scenario testing (backend down, LLM failure, Qdrant timeout)

### Documentation Checklist

- [ ] User guide (chatbot-guide.md) created
- [ ] Developer quickstart (quickstart.md) created
- [ ] API contracts formalized (contracts/chat-api.yaml)
- [ ] Research document (research.md) completed
- [ ] Data model document (data-model.md) completed
- [ ] ADR-001 reviewed and updated with implementation notes

---

**Plan Status**: 📝 DRAFT - Phase 0 (Research) and Phase 1 (Design) to be completed

**Next Actions**:
1. Complete research.md with answers to research questions
2. Formalize data-model.md with detailed entity relationships
3. Create contracts/chat-api.yaml OpenAPI specification
4. Write quickstart.md developer onboarding guide
5. Run `/sp.tasks` to generate actionable implementation task list
6. Begin P1 tasks (testing, citation URLs, performance monitoring)

---

**Revision History**:

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-26 | 1.0 | Initial plan created documenting existing architecture and identifying gaps | Claude |
