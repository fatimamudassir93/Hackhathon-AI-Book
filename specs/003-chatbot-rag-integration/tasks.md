**Source Specification**:
- Feature: Chatbot RAG Integration
- Spec File: chatbot-rag/spec.md
- Branch: 003-chatbot-rag-integration
- Generated via: sp.tasks
description: "Implementation tasks for Chatbot RAG Integration"
---

# Tasks: Chatbot RAG Integration

**Input**: Feature description - Deterministic ingestion pipeline for Docusaurus textbook content with RAG-based Q&A through chatbot

**Prerequisites**: Existing code in rag-backend/, physical-ai-book/src/components/Chatbot.tsx

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks are excluded

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `rag-backend/`
- **Frontend**: `physical-ai-book/src/`
- **Docs**: `physical-ai-book/docs/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify rag-backend dependencies in rag-backend/requirements.txt include qdrant-client, langchain, HuggingFace embeddings
- [X] T002 [P] Verify frontend dependencies in physical-ai-book/package.json include React, TypeScript
- [X] T003 [P] Create environment variable template file rag-backend/.env.example with QDRANT_HOST, QDRANT_API_KEY, GROQ_API_KEY placeholders
- [X] T004 [P] Document Qdrant Cloud setup requirements in rag-backend/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented
Note: Tasks marked [P] may be implemented in parallel, but Phase 2 as a whole must complete before any user story work begins.


**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Configure Qdrant Cloud connection and create collection "physical_ai_book" in rag-backend/qdrant_setup.py
- [X] T006 [P] Implement embeddings service wrapper in rag-backend/embeddings_service.py for OpenAI-compatible models
- [X] T007 [P] Create base document chunking utilities in rag-backend/chunking_utils.py with semantic splitting logic
- [X] T008 [P] Implement metadata extraction utilities in rag-backend/metadata_extractor.py for chapter/section/subsection parsing
- [X] T009 Configure CORS and API routing in rag-backend/main.py to allow chatbot frontend requests
- [X] T010 [P] Create logging configuration in rag-backend/logging_config.py for ingestion and query tracking

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - Initial Content Ingestion (Priority: P1) 🎯 MVP

**Goal**: Index all textbook content from physical-ai-book/docs into Qdrant Cloud with proper metadata

**Independent Test**: Run ingestion script and verify all chapters are queryable in Qdrant with chapter/section metadata

### Implementation for User Story 4

- [X] T011 [P] [US4] Implement markdown file discovery in rag-backend/file_scanner.py excluding tutorial-basics and tutorial-extras directories
- [X] T012 [P] [US4] Create chapter metadata parser in rag-backend/chapter_parser.py to extract hierarchical structure from headers
- [X] T013 [US4] Implement semantic chunking logic in rag-backend/chunker.py following header boundaries and paragraph structure
- [X] T014 [US4] Create deduplication service in rag-backend/dedup_service.py using content hashes to prevent duplicate embeddings
- [X] T015 [US4] Implement batch embedding generation in rag-backend/embedding_batch.py with rate limiting and error handling
- [X] T016 [US4] Create Qdrant uploader in rag-backend/qdrant_uploader.py to store vectors with metadata payload
- [X] T017 [US4] Implement ingestion pipeline orchestrator in rag-backend/ingest_pipeline.py coordinating scan → parse → chunk → embed → upload
- [X] T018 [US4] Add ingestion status logging and error reporting in rag-backend/ingestion_logger.py
- [X] T019 [US4] Create CLI entry point script rag-backend/run_ingestion.py for manual pipeline execution
- [X] T020 [US4] Validate ingestion by querying Qdrant for sample chapters in rag-backend/validate_ingestion.py

**Checkpoint**: At this point, all textbook content should be indexed and queryable in Qdrant Cloud

---

## Phase 4: User Story 1 - Ask Questions About Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Enable users to ask questions through chatbot and receive answers with chapter citations

**Independent Test**: Ask "What is embodied intelligence?" and verify chatbot returns answer with Chapter 1 citation

### Implementation for User Story 1

- [X] T021 [P] [US1] Implement vector search service in rag-backend/vector_search.py with similarity threshold and top-k retrieval
- [X] T022 [P] [US1] Create context builder in rag-backend/context_builder.py to format retrieved chunks for LLM prompt
- [X] T023 [P] [US1] Implement citation formatter in rag-backend/citation_formatter.py to extract and format chapter/section references
- [X] T024 [US1] Create RAG query endpoint POST /api/chat in rag-backend/main.py accepting message and returning response with sources
- [X] T025 [US1] Implement LLM response generation in rag-backend/llm_service.py using Groq API with context injection
- [X] T026 [US1] Add out-of-scope detection in rag-backend/scope_detector.py to identify questions outside textbook content
- [X] T027 [US1] Update chatbot component in physical-ai-book/src/components/Chatbot.tsx to display source citations in UI
- [X] T028 [US1] Add error handling for API failures in physical-ai-book/src/components/Chatbot.tsx
- [X] T029 [US1] Implement loading state indicators in physical-ai-book/src/components/Chatbot.tsx while waiting for responses

**Checkpoint**: At this point, users can ask questions and receive cited answers from the textbook

---

## Phase 5: User Story 2 - Context-Aware Questions on Selected Text (Priority: P2)

**Goal**: Allow users to select text and ask contextual questions about it

**Independent Test**: Select text about "ROS 2 nodes", ask "How does this relate to Nav2?", verify contextual answer with citations

### Implementation for User Story 2

- [X] T030 [P] [US2] Add selected_text parameter to /api/chat endpoint in rag-backend/main.py
- [X] T031 [P] [US2] Implement context augmentation in rag-backend/context_augmenter.py to combine selected text with retrieved chunks
- [X] T032 [US2] Update vector search to boost relevance when selected_text is provided in rag-backend/vector_search.py
- [X] T033 [US2] Enhance chatbot to send selected text with questions in physical-ai-book/src/components/Chatbot.tsx
- [X] T034 [US2] Add visual indicator in chatbot UI showing selected text context in physical-ai-book/src/components/Chatbot.tsx

**Checkpoint**: At this point, users can ask questions about highlighted text and receive contextual answers

---

## Phase 6: User Story 3 - Filter Answers by Chapter (Priority: P2)

**Goal**: Enable users to restrict chatbot answers to specific chapters

**Independent Test**: Set filter to "Chapter 2", ask "What are actuators?", verify all sources are from Chapter 2

### Implementation for User Story 3

- [X] T035 [P] [US3] Add chapter_filter parameter to /api/chat endpoint in rag-backend/main.py
- [X] T036 [P] [US3] Implement metadata filtering in rag-backend/vector_search.py using Qdrant filter conditions
- [X] T037 [P] [US3] Create chapter list endpoint GET /api/chapters in rag-backend/main.py to populate filter dropdown
- [X] T038 [US3] Add chapter filter dropdown UI component in physical-ai-book/src/components/ChatbotFilters.tsx
- [X] T039 [US3] Integrate chapter filter with chat requests in physical-ai-book/src/components/Chatbot.tsx
- [X] T040 [US3] Add visual indication of active filters in chatbot interface in physical-ai-book/src/components/Chatbot.tsx

**Checkpoint**: At this point, users can filter answers to specific chapters

---

## Phase 7: User Story 5 - Update Content Without Duplication (Priority: P3)

**Goal**: Support re-ingestion of updated chapters without creating duplicates

**Independent Test**: Modify Chapter 3, re-run ingestion, verify no duplicates and updated content is used

### Implementation for User Story 5

- [X] T041 [P] [US5] Implement content hash comparison in rag-backend/dedup_service.py to detect changed vs unchanged files
- [X] T042 [P] [US5] Create update strategy in rag-backend/update_strategy.py to delete old embeddings before inserting new ones
- [X] T043 [US5] Add incremental ingestion mode to rag-backend/ingest_pipeline.py that only processes changed files
- [X] T044 [US5] Implement orphaned embedding detection in rag-backend/orphan_detector.py for deleted source files
- [X] T045 [US5] Add dry-run mode to rag-backend/run_ingestion.py showing what would be updated without making changes
- [X] T046 [US5] Create ingestion comparison report in rag-backend/ingestion_reporter.py showing before/after stats

**Checkpoint**: At this point, content can be safely updated without duplication

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T047 [P] Add comprehensive error messages for Qdrant connection failures in rag-backend/main.py
- [X] T048 [P] Implement rate limiting on /api/chat endpoint in rag-backend/rate_limiter.py to prevent abuse
- [X] T049 [P] Add ingestion monitoring dashboard data endpoint GET /api/ingestion/status in rag-backend/main.py
- [X] T050 [P] Create ingestion documentation in rag-backend/docs/INGESTION.md with setup and usage instructions
- [X] T051 [P] Add chatbot usage documentation in physical-ai-book/docs/chatbot-guide.md for end users
- [X] T052 [P] Optimize chunk size parameters in rag-backend/chunking_utils.py based on retrieval performance testing
- [X] T053 [P] Add response caching for frequently asked questions in rag-backend/response_cache.py
- [X] T054 Code cleanup and remove unused demo files (demo_groq.py, test_groq_direct.py) from rag-backend/
- [X] T055 [P] Security review of API key handling and add key rotation documentation
- [X] T056 Performance profiling of end-to-end query latency and optimization

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 4 - Initial Ingestion (Phase 3)**: Depends on Foundational (Phase 2) - BLOCKS User Stories 1, 2, 3 (no content = no answers)
- **User Story 1 - Q&A (Phase 4)**: Depends on User Story 4 completion (needs indexed content)
- **User Story 2 - Selected Text (Phase 5)**: Depends on User Story 1 completion (extends Q&A capability)
- **User Story 3 - Chapter Filter (Phase 6)**: Depends on User Story 1 completion (extends Q&A capability)
- **User Story 5 - Updates (Phase 7)**: Depends on User Story 4 completion (extends ingestion capability)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 4 (Initial Ingestion - P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - CRITICAL BLOCKER for all Q&A features
- **User Story 1 (Q&A - P1)**: Depends on User Story 4 (needs indexed content) - Core chatbot functionality
- **User Story 2 (Selected Text - P2)**: Depends on User Story 1 (extends Q&A) - Can proceed after US1 complete
- **User Story 3 (Chapter Filter - P2)**: Depends on User Story 1 (extends Q&A) - Can proceed in parallel with US2 after US1 complete
- **User Story 5 (Updates - P3)**: Depends on User Story 4 (extends ingestion) - Can proceed in parallel with US2/US3

### Within Each User Story

- Foundational utilities before pipeline orchestration
- Pipeline orchestration before endpoint implementation
- Backend endpoints before frontend integration
- Core implementation before UI enhancements

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- User Story 4 MUST complete before User Stories 1, 2, 3 can start (no content = no answers)
- After User Story 1 completes, User Stories 2 and 3 can run in parallel
- User Story 5 can run in parallel with User Stories 2 and 3 (different subsystems)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 4 (Initial Ingestion)

```bash
# Launch parallel foundational utilities for User Story 4:
Task: "Implement markdown file discovery in rag-backend/file_scanner.py"
Task: "Create chapter metadata parser in rag-backend/chapter_parser.py"

# Then sequentially:
Task: "Implement semantic chunking logic in rag-backend/chunker.py"
→ Task: "Implement ingestion pipeline orchestrator in rag-backend/ingest_pipeline.py"
```

## Parallel Example: User Story 1 (Q&A)

```bash
# Launch parallel services for User Story 1:
Task: "Implement vector search service in rag-backend/vector_search.py"
Task: "Create context builder in rag-backend/context_builder.py"
Task: "Implement citation formatter in rag-backend/citation_formatter.py"

# Then sequentially:
Task: "Create RAG query endpoint POST /api/chat in rag-backend/main.py"
→ Task: "Update chatbot component in physical-ai-book/src/components/Chatbot.tsx"
```

## Parallel Example: After User Story 1 Complete

```bash
# These can run in parallel since they extend different aspects:
Team A: User Story 2 (Selected Text Context)
Team B: User Story 3 (Chapter Filtering)
Team C: User Story 5 (Update Without Duplication)
```

---

## Implementation Strategy

### MVP First (Ingestion + Basic Q&A)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 4 (Ingestion) - CRITICAL BLOCKER for Q&A
4. Complete Phase 4: User Story 1 (Basic Q&A with Citations)
5. **STOP and VALIDATE**: Test that users can ask questions and get cited answers
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 4 (Ingestion) → Test that content is indexed → Critical milestone!
3. Add User Story 1 (Q&A) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 2 (Selected Text) → Test independently → Deploy/Demo
5. Add User Story 3 (Chapter Filter) → Test independently → Deploy/Demo
6. Add User Story 5 (Updates) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Team completes User Story 4 (Ingestion) together - CRITICAL BLOCKER
3. Team completes User Story 1 (Q&A) together - CORE VALUE
4. Once User Story 1 is done:
   - Developer A: User Story 2 (Selected Text)
   - Developer B: User Story 3 (Chapter Filter)
   - Developer C: User Story 5 (Updates)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 4 (Ingestion) is CRITICAL and BLOCKS all Q&A features (US1, US2, US3)
- User Story 1 (Q&A) is the core value proposition and should be completed before US2/US3
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Existing code in rag-backend/data_ingestion.py and main.py can be refactored/enhanced rather than rewritten
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
