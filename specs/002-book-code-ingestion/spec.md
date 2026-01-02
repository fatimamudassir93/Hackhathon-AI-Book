# Feature Specification: Book Content Ingestion Pipeline

**Feature Branch**: `002-book-content-ingestion`
**Created**: 2025-12-04
**Status**: Draft
**Input**: User description: "Ingest Docusaurus-based Physical AI book content into a vector database for RAG"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Ask questions from the book (Priority: P1)

As a learner reading the Physical AI & Humanoid Robotics textbook,
I want to ask natural language questions and receive accurate answers
based strictly on the book's content.

**Why this priority**:
This is the core value of the RAG chatbot. Without ingestion, the chatbot is unusable.

**Independent Test**:
Ask a question such as "What is embodied intelligence?" and receive an answer
that cites the correct chapter and section.

**Acceptance Scenarios**:

1. **Given** book content is ingested,
   **When** a user asks "What is embodied intelligence?",
   **Then** the system returns an answer citing the specific chapter and section from the book.

2. **Given** a user asks about a technical concept covered in the book,
   **When** the RAG system processes the query,
   **Then** the response includes direct quotes or paraphrases from the relevant book sections.

3. **Given** a user asks a question not covered in the book,
   **When** the RAG system searches for relevant content,
   **Then** the system responds indicating no relevant content was found in the book.

---

### User Story 2 – Chapter-level filtering (Priority: P2)

As a learner,
I want answers to be constrained to the chapter I am currently reading,
so that I can focus on content relevant to my current learning context.

**Why this priority**:
Improves learning focus and precision by reducing noise from unrelated chapters.

**Independent Test**:
Select Chapter 3, ask a question, and verify that responses only reference content from Chapter 3.

**Acceptance Scenarios**:

1. **Given** a user is reading Chapter 3 on ROS 2,
   **When** they ask "How do I set up navigation?",
   **Then** the system returns answers only from Chapter 3 content.

2. **Given** a user selects "All Chapters" filter,
   **When** they ask a question,
   **Then** the system searches across all ingested chapters.

3. **Given** a user switches from Chapter 2 to Chapter 5,
   **When** they ask the same question,
   **Then** the system returns different results based on Chapter 5 content.

---

### User Story 3 – Re-ingestion without duplication (Priority: P3)

As a maintainer,
I want to re-ingest the book after updates without creating duplicate vectors,
so that the database remains clean and search results are not duplicated.

**Why this priority**:
The book evolves during the hackathon. Content updates should refresh vectors, not duplicate them.

**Independent Test**:
Run ingestion twice with the same content and verify vector counts remain stable.

**Acceptance Scenarios**:

1. **Given** the book has been ingested once,
   **When** the ingestion process runs again with unchanged content,
   **Then** the vector count in Qdrant remains the same.

2. **Given** a single chapter has been updated,
   **When** re-ingestion is triggered,
   **Then** only vectors for the updated chapter are replaced.

3. **Given** a new chapter is added to the book,
   **When** re-ingestion is triggered,
   **Then** new vectors are created only for the new chapter, and existing vectors remain unchanged.

---

### User Story 4 – Accurate metadata attribution (Priority: P2)

As a learner,
I want to see which chapter and section each answer comes from,
so that I can verify the information and learn more about that topic.

**Why this priority**:
Trust and traceability are essential for educational content. Users need to verify sources.

**Independent Test**:
Ask any question and verify that the response includes chapter number, chapter title, and section information.

**Acceptance Scenarios**:

1. **Given** a question about "SLAM algorithms",
   **When** the RAG system retrieves relevant content,
   **Then** each retrieved chunk includes metadata: chapter number, chapter title, section heading, and file path.

2. **Given** content spans multiple sections within a chapter,
   **When** the RAG system returns results,
   **Then** each chunk is correctly attributed to its specific section.

3. **Given** supplementary content like preface or glossary,
   **When** this content is retrieved,
   **Then** it is clearly labeled as "Preface" or "Glossary" rather than a chapter.

---

### User Story 5 – Handle malformed or edge-case content (Priority: P3)

As a system maintainer,
I want the ingestion pipeline to gracefully handle malformed Markdown files,
so that one bad file doesn't break the entire ingestion process.

**Why this priority**:
Robustness ensures the system can handle real-world content variations and author mistakes.

**Independent Test**:
Create a Markdown file with missing headers, empty content, or malformed syntax, then verify ingestion completes successfully.

**Acceptance Scenarios**:

1. **Given** a Markdown file is completely empty,
   **When** the ingestion process encounters it,
   **Then** the file is skipped with a warning logged, and ingestion continues.

2. **Given** a Markdown file has no headers,
   **When** the file is processed,
   **Then** the content is chunked using paragraph boundaries and assigned default metadata.

3. **Given** a Markdown file contains malformed syntax (e.g., unclosed code blocks),
   **When** the parser processes it,
   **Then** the content is parsed as best-effort, and any errors are logged without stopping ingestion.

---

### Edge Cases

- What happens if a Markdown file is empty?
- What happens if headers are missing or malformed?
- How does the system handle malformed Markdown (unclosed code blocks, invalid syntax)?
- What happens if the same content appears in multiple files?
- How does the system handle very long chapters (>100,000 characters)?
- What happens if chapter numbering is inconsistent (e.g., chapter1.md, chapter10.md, chapter2.md)?
- How are non-chapter files (preface, glossary, appendices) handled?
- What happens if Qdrant is unavailable during ingestion?
- How does the system handle special characters, code blocks, tables, and images in Markdown?
- What happens if embedding generation fails for specific chunks?
- How does the system handle files with duplicate filenames in different directories?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse Markdown files from `physical-ai-book/docs` directory and all subdirectories.
- **FR-002**: System MUST split content using a combination of headers (H1, H2, H3) and paragraph boundaries.
- **FR-003**: System MUST extract and attach metadata to each chunk, including:
  - Chapter number (e.g., "Chapter 1", "Preface", "Glossary")
  - Chapter title (extracted from first H1 heading)
  - Section heading (from H2 or H3 if applicable)
  - Source file path
  - Chunk position within the document
- **FR-004**: System MUST generate embeddings using a deterministic embedding model with consistent parameters.
- **FR-005**: System MUST store vectors in Qdrant Cloud with the following point structure:
  - Vector: embedding representation
  - Payload: metadata (chapter, section, source_path, text content)
  - ID: unique identifier for each chunk
- **FR-006**: System MUST support re-ingestion without creating duplicate vectors by:
  - Detecting existing content based on source file path and chunk hash
  - Updating vectors when content changes
  - Removing orphaned vectors when source files are deleted
- **FR-007**: System MUST preserve code blocks, tables, and special formatting during chunking.
- **FR-008**: System MUST handle both chapter files (e.g., `chapter1.md`, `chapter2.md`) and supplementary files (e.g., `preface.md`, `glossary.md`).
- **FR-009**: System MUST log all ingestion activities, including:
  - Files processed
  - Chunks created
  - Embeddings generated
  - Errors encountered
  - Time taken per operation
- **FR-010**: System MUST validate that all ingested vectors are retrievable through search queries.

### Non-Functional Requirements

- **NFR-001**: Ingestion SHOULD complete for 6 chapters (approximately 50,000 words) within 5 minutes.
- **NFR-002**: System SHOULD handle up to 100 Markdown files without memory overflow.
- **NFR-003**: Chunk size SHOULD be between 500-1500 characters to balance context and precision.
- **NFR-004**: Embeddings MUST be generated using the same model and parameters across all re-ingestions to ensure consistency.
- **NFR-005**: The system SHOULD provide progress feedback during ingestion (e.g., "Processing file 5 of 20").

### Key Entities

- **BookChunk**: Represents a semantic unit of text from the book
  - Text content (500-1500 characters)
  - Chapter identifier (e.g., "Chapter 1", "Preface")
  - Chapter title (e.g., "Introduction to Physical AI")
  - Section heading (e.g., "What is Embodied Intelligence?")
  - Source file path
  - Chunk position (ordinal position within the source document)
  - Content hash (for deduplication)

- **VectorEmbedding**: Represents the vector representation of a BookChunk
  - Embedding vector (dense float array, dimension determined by model)
  - Metadata (all BookChunk attributes)
  - Unique ID (UUID or hash-based identifier)
  - Created timestamp
  - Updated timestamp (for re-ingestion tracking)

- **IngestionRun**: Represents a single execution of the ingestion pipeline
  - Run ID
  - Start time
  - End time
  - Files processed
  - Chunks created
  - Vectors upserted
  - Errors encountered
  - Status (in_progress, completed, failed)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of book chapters and supplementary files are successfully ingested into Qdrant.
- **SC-002**: RAG chatbot responses cite the correct chapter and section for 95% of factual queries.
- **SC-003**: Re-ingestion with unchanged content results in zero increase in vector count.
- **SC-004**: Re-ingestion with updated content replaces only the changed vectors (measurable via ingestion logs).
- **SC-005**: Users can retrieve relevant answers within 2 seconds for 90% of queries.
- **SC-006**: Ingestion completes without errors for all well-formed Markdown files.
- **SC-007**: Malformed files are handled gracefully with warnings logged, allowing ingestion to continue for remaining files.
- **SC-008**: 100% of ingested content is retrievable through vector search queries.

---

## Assumptions

1. **Content Format**: All book content is authored in Markdown format compatible with Docusaurus 3.
2. **Embedding Model**: A HuggingFace sentence-transformers model will be used for generating embeddings (e.g., `all-MiniLM-L6-v2`).
3. **Qdrant Availability**: Qdrant Cloud or a self-hosted Qdrant instance is available and accessible.
4. **File Structure**: Chapter files follow a naming convention (e.g., `chapter1.md`, `chapter2.md`) or are organized in a `chapters/` subdirectory.
5. **Update Frequency**: Book content updates are infrequent (weekly or less) during the hackathon phase.
6. **Language**: All content is in English.
7. **Access**: The ingestion pipeline has read access to the `physical-ai-book/docs` directory.
8. **Authentication**: Qdrant API key is available via environment variable or configuration file.

---

## Dependencies

### External Systems

- **Qdrant Cloud/Server**: Vector database for storing embeddings
  - Required version: 1.7.0 or higher
  - Configuration: API key, URL, collection name

- **HuggingFace Models**: Embedding model for text vectorization
  - Model: `all-MiniLM-L6-v2` or similar sentence-transformers model
  - Requires: Internet access for initial model download

### Internal Systems

- **Physical AI Book Repository**: Source of Markdown content
  - Location: `physical-ai-book/docs`
  - Format: Docusaurus 3-compatible Markdown

- **RAG Backend API**: Consumer of ingested vectors
  - Dependency: Ingestion must complete before RAG queries can work

### Libraries and Tools

- **LangChain**: Document loading and text splitting
- **Qdrant Client**: Python client for Qdrant operations
- **Python 3.9+**: Runtime environment

---

## Out of Scope

The following are explicitly out of scope for this feature:

1. **Image Ingestion**: Images, diagrams, and figures are not indexed or searchable.
2. **Code Execution**: Code snippets are ingested as text only; no execution or validation is performed.
3. **Multi-language Support**: Only English content is supported.
4. **Real-time Ingestion**: Ingestion is batch-based; real-time updates as authors edit are not supported.
5. **Version Control Integration**: The system does not track Markdown file changes via git history.
6. **Content Generation**: The ingestion pipeline only indexes existing content; it does not generate new content.
7. **Query Processing**: This feature handles ingestion only; query processing and response generation are handled by the RAG backend (separate feature).
8. **Authentication**: User authentication for accessing the chatbot is out of scope for ingestion.
9. **PDF or DOCX Conversion**: Only Markdown files are supported; other formats require pre-conversion.

---

## Open Questions / Needs Clarification

None at this time. All critical decisions have been made based on the existing implementation and standard RAG patterns.

---

## Revision History

| Date       | Version | Changes                                      | Author  |
|------------|---------|----------------------------------------------|---------|
| 2025-12-04 | 1.0     | Initial specification created                | -       |
| 2025-12-26 | 2.0     | Expanded specification with comprehensive details | Claude  |
