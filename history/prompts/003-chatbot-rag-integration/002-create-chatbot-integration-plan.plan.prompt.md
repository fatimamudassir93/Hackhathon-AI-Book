---
id: 002
title: Create chatbot integration plan
stage: plan
date: 2025-12-26
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-chatbot-rag-integration
branch: 003-book-content-ingestion
user: shoai
command: sp.plan 003-chatbot-rag-integration
labels: ["planning", "rag", "chatbot", "architecture", "design"]
links:
  spec: specs/003-chatbot-rag-integration/spec.md
  ticket: null
  adr: history/adr/001-chatbot-uses-rag-ingestion.md
  pr: null
files:
  - specs/003-chatbot-rag-integration/plan.md
  - specs/003-chatbot-rag-integration/research.md
  - specs/003-chatbot-rag-integration/data-model.md
  - specs/003-chatbot-rag-integration/contracts/chat-api.yaml
  - specs/003-chatbot-rag-integration/quickstart.md
tests:
  - No automated tests created (planning phase only)
---

## Prompt

003-chatbot-rag-integration

## Response snapshot

Created comprehensive implementation plan for the chatbot RAG integration feature, documenting existing architecture and identifying remaining work.

### Key Deliverables:

**1. Implementation Plan (plan.md)**:
- Documented current implementation status (majority already complete)
- Technical context: TypeScript/React frontend, Python/FastAPI backend, Qdrant vector DB
- Architecture overview: Frontend (Chatbot.tsx) → Backend (/api/chat) → Qdrant + LLM
- Complexity tracking placeholder (constitution not yet defined)
- Phase 0: Research questions identified
- Phase 1: Design artifacts to be created
- Validation criteria with 13 functional requirements and 8 success criteria
- Risk analysis (7 risks identified with mitigation strategies)

**2. Technical Research (research.md)**:
- **Frontend-Backend Integration**: Decision to keep current fetch() implementation (simple, works well)
- **Error Handling**: Enhance with partial success support (show sources even if LLM fails)
- **Testing Strategy**: Implement testing pyramid (Unit → Integration → E2E)
- **Performance Optimization**: Add monitoring first, streaming responses if needed (target: <3s p90)
- **Session Management**: Add sessionStorage for MVP, conversation history UI later
- **Citation URL Generation**: Generate URLs in backend (centralized, testable)

**3. Data Model (data-model.md)**:
- **Frontend Entities**: ChatMessage, Source, ChapterFilter (TypeScript interfaces)
- **Backend Entities**: ChatRequest, ChatResponse, Source (Pydantic models)
- **Database Entities**: User, UserProfile, ChatHistory, PersonalizationCache (SQLAlchemy)
- **Future Entities**: UserFeedback (planned for thumbs up/down feature)
- Entity relationships diagram and data flow documentation
- Validation rules for all fields
- State transitions and lifecycle documentation
- Storage strategy: React state + sessionStorage + database

**4. API Contracts (contracts/chat-api.yaml)**:
- OpenAPI 3.0 specification for /api/chat endpoint
- Complete request/response schemas with validation rules
- Example requests: basic question, filtered question, contextual question (with selected text)
- Example responses: in-scope answer with sources, out-of-scope answer
- Error responses: 400 (bad request), 401 (unauthorized), 429 (rate limit), 500 (server error)
- Additional endpoints documented: /api/chapters, /health
- Rate limiting, caching, and performance metadata (x-* extensions)

**5. Developer Quickstart (quickstart.md)**:
- **Backend Setup**: Python venv, pip install, .env configuration, Qdrant verification
- **Frontend Setup**: npm install, Docusaurus server startup
- **Integration Testing**: 6 test scenarios (basic Q&A, filtering, text selection, out-of-scope, errors, history)
- **Development Workflow**: Running both servers simultaneously, hot reloading, debugging tips
- **Troubleshooting**: Common issues and solutions (connection errors, API keys, CORS, etc.)
- **Next Steps**: Development tasks prioritized (P1: core gaps, P2: UX improvements, P3: testing)
- Estimated setup time: 15-20 minutes

### Current Implementation Status:

**✅ COMPLETED** (Already Working):
- Backend RAG pipeline (vector search, context building, citation formatting, scope detection)
- Frontend chatbot UI (message display, sources, chapter filtering, text selection)
- Authentication and user profiles
- Rate limiting and response caching
- Performance profiling
- 246 vectors ingested in Qdrant

**🔄 IN PROGRESS / NEEDS WORK**:
- No automated tests (frontend or backend)
- User guide for chatbot
- API contract formalization (NOW COMPLETE)
- Citation URLs not populated (Source.url field empty)
- User feedback UI (thumbs up/down) not implemented
- Session storage conversation history
- Streaming response support
- Performance measurement (p90 response time)
- Accessibility audit incomplete

**Priority Recommendations**:
- **P1**: Citation URL generation, integration tests, performance monitoring, user documentation
- **P2**: User feedback UI, streaming responses, improved error messages, session storage
- **P3**: Accessibility audit, unit tests, E2E tests, developer quickstart, API formalization

### Research Decisions Summary:

| Area | Decision | Rationale |
|------|----------|-----------|
| Frontend Integration | Keep fetch() | Simple, backend handles caching |
| Error Handling | Partial success + retry | Show sources even if LLM fails |
| Testing | Pyramid (Unit → Integration → E2E) | Comprehensive coverage |
| Performance | Monitor first, stream if needed | Measure before optimizing |
| Session Management | sessionStorage for MVP | Survives refreshes, simple |
| Citation URLs | Backend generation | Centralized, testable |

## Outcome

- ✅ Impact: Created comprehensive implementation plan with 5 detailed design artifacts (plan.md, research.md, data-model.md, contracts/chat-api.yaml, quickstart.md) documenting architecture, technical decisions, data models, API contracts, and developer onboarding
- 🧪 Tests: No automated tests created (planning phase only); test strategy documented in research.md
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, chat-api.yaml, quickstart.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task list from plan, or begin P1 implementation tasks (citation URLs, tests, monitoring, docs)
- 🧠 Reflection: The plan reveals that the RAG integration is mostly complete (backend and frontend functional), with remaining work focused on testing, documentation, performance optimization, and UX enhancements (citation URLs, feedback UI, session storage). The research phase resolved all technical uncertainties with clear decisions and rationale.

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan successfully documented existing architecture and identified concrete next steps.
- Graders run and results (PASS/FAIL):
  - Architecture documentation: PASS (complete overview of frontend, backend, Qdrant, LLM providers)
  - Research completeness: PASS (all 6 research areas addressed with decisions and rationale)
  - Data model clarity: PASS (9 entities with relationships, validation rules, state transitions)
  - API contract formalization: PASS (OpenAPI 3.0 spec with examples and error codes)
  - Developer onboarding: PASS (quickstart with setup steps, testing scenarios, troubleshooting)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin P1 implementation with citation URL generation (backend citation_formatter.py) since it's a small, high-impact change that unblocks clickable source links
