# Data Model: Chatbot RAG Integration

**Feature**: 003-chatbot-rag-integration
**Date**: 2025-12-26
**Status**: Complete

## Overview

This document defines all data entities, their relationships, validation rules, and state transitions for the chatbot RAG integration feature.

---

## Entity Diagram

```
┌─────────────────┐
│     User        │
│  (auth.py)      │
└────────┬────────┘
         │
         │ 1:1
         ▼
┌─────────────────┐           ┌──────────────────┐
│  UserProfile    │           │  ChatHistory     │
│  (models.py)    │◄──────────┤  (models.py)     │
└─────────────────┘    1:N    └────────┬─────────┘
                                       │
                                       │ contains
                                       ▼
                              ┌──────────────────┐
                              │  ChatMessage     │
                              │  (Frontend TS)   │
                              └────────┬─────────┘
                                       │
                                       │ has
                                       ▼
                              ┌──────────────────┐
                              │  Source          │
                              │  (Frontend/API)  │
                              └──────────────────┘

┌─────────────────┐           ┌──────────────────┐
│  ChapterFilter  │           │  UserFeedback    │
│  (Frontend TS)  │           │  (Future)        │
└─────────────────┘           └──────────────────┘

┌─────────────────────────┐
│  PersonalizationCache   │
│  (models.py)            │
└─────────────────────────┘
```

---

## Frontend Entities (TypeScript)

### 1. ChatMessage

**Purpose**: Represents a single message in the chatbot conversation (user question or assistant answer)

**Location**: `physical-ai-book/src/components/Chatbot.tsx` (lines 14-21)

**Definition**:
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string | object;  // string for normal content, object for error content
  sources?: Source[];        // Only for assistant messages
  citations?: string;        // Only for assistant messages (formatted citations)
  in_scope?: boolean;        // Only for assistant messages (textbook scope flag)
  error?: boolean;           // True if this is an error message
  timestamp?: Date;          // NEW: For message ordering and history
  feedback?: {               // NEW: User feedback (thumbs up/down)
    rating: 'positive' | 'negative';
    comment?: string;
  };
}
```

**Fields**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `role` | `'user' \| 'assistant'` | Yes | Message sender | Must be either 'user' or 'assistant' |
| `content` | `string \| object` | Yes | Message text or error object | Min length: 1 char (if string) |
| `sources` | `Source[]` | No | Source citations (assistant only) | Max 10 sources per message |
| `citations` | `string` | No | Formatted citation text | Max length: 2000 chars |
| `in_scope` | `boolean` | No | Whether question was in textbook scope | Default: true |
| `error` | `boolean` | No | Error message flag | Default: false |
| `timestamp` | `Date` | No | When message was created | Auto-generated on creation |
| `feedback` | `object` | No | User feedback on answer | Only for assistant messages |

**State Transitions**:
```
[User types message]
  → ChatMessage created (role: 'user', content: <text>)
  → Added to messages array
  → Sent to backend

[Backend response received]
  → ChatMessage created (role: 'assistant', content: <answer>, sources: [...])
  → Added to messages array
  → Rendered in UI

[User provides feedback]
  → ChatMessage.feedback updated (rating: 'positive' | 'negative', comment: <text>)
  → Saved to database (if authenticated)
```

**Validation Rules**:
1. User messages: Must have `role='user'` and non-empty `content` string
2. Assistant messages: Must have `role='assistant'` and either `content` string or `error=true`
3. Error messages: Must have `error=true` and descriptive `content`
4. Sources: Only present for successful assistant messages (not errors)
5. Feedback: Only allowed on assistant messages, not user messages or errors

**Storage**:
- **Runtime**: React state (`useState<Message[]>`)
- **Session**: Browser sessionStorage (JSON serialized, max 50 messages)
- **Persistent**: Database ChatHistory table (if user authenticated)

---

### 2. Source

**Purpose**: Represents a single source citation from the textbook (retrieved chunk)

**Location**: `physical-ai-book/src/components/Chatbot.tsx` (lines 6-12)

**Definition**:
```typescript
interface Source {
  chapter: string;      // e.g., "Chapter 1" or "Chapter 3"
  title: string;        // Chapter title or section title
  section?: string;     // Section/subsection heading (optional)
  score: number;        // Relevance score from vector search (0.0 to 1.0)
  url?: string;         // Clickable link to textbook section (Docusaurus URL)
  snippet?: string;     // NEW: Text preview (first 200 chars of chunk)
}
```

**Fields**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `chapter` | `string` | Yes | Chapter identifier | Pattern: `^Chapter \d+$` or custom chapter name |
| `title` | `string` | Yes | Chapter or section title | Min length: 1 char, Max length: 200 chars |
| `section` | `string` | No | Subsection heading | Max length: 200 chars |
| `score` | `number` | Yes | Vector similarity score | Range: 0.0 to 1.0 (inclusive) |
| `url` | `string` | No | Docusaurus URL to source | Valid URL format, starts with http:// or https:// |
| `snippet` | `string` | No | Text preview | Max length: 200 chars |

**Validation Rules**:
1. `score` must be between 0.0 and 1.0 (cosine similarity range)
2. `chapter` should match pattern `Chapter \d+` for consistency
3. `url` must be valid HTTP/HTTPS URL if provided
4. `section` is optional but recommended for better attribution
5. At least 1 source should be returned per successful query (unless out of scope)

**Rendering**:
- Display in `<div className={styles.sources}>` element
- Show chapter and section as clickable links (if URL available)
- Format score as percentage: `(score * 100).toFixed(0)}%`
- Sort by score descending (most relevant first)

**Example**:
```json
{
  "chapter": "Chapter 1",
  "title": "Introduction to Physical AI",
  "section": "Embodied Intelligence",
  "score": 0.8523,
  "url": "http://localhost:3000/docs/chapter-1#embodied-intelligence",
  "snippet": "Embodied intelligence refers to the idea that..."
}
```

---

### 3. ChapterFilter

**Purpose**: Represents the selected chapter filter state (all chapters or specific chapter)

**Location**: `physical-ai-book/src/components/ChatbotFilters.tsx` (implicit)

**Definition**:
```typescript
type ChapterFilter = string | null;  // null = "All Chapters", string = specific chapter

// Expanded version for UI rendering:
interface ChapterFilterOption {
  value: string | null;       // null for "All Chapters", "Chapter 1" for specific
  label: string;              // Display label (e.g., "All Chapters", "Chapter 1: Intro")
  count?: number;             // Number of vectors in this chapter (optional)
}
```

**Fields**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `value` | `string \| null` | Yes | Chapter identifier or null | null or matches chapter naming pattern |
| `label` | `string` | Yes | Display name | Min length: 1 char |
| `count` | `number` | No | Number of chunks in chapter | Min: 0 |

**State Management**:
```typescript
const [chapterFilter, setChapterFilter] = useState<string | null>(null);

// When user selects filter:
setChapterFilter("Chapter 1");  // Filter to Chapter 1
setChapterFilter(null);         // Reset to "All Chapters"
```

**API Integration**:
```typescript
// Sent to backend in ChatRequest:
{
  message: "What is embodied intelligence?",
  chapter_filter: chapterFilter,  // null or "Chapter 1"
  // ...
}
```

**Validation Rules**:
1. `null` means no filter (search all chapters)
2. Non-null values must match available chapters from `/api/chapters` endpoint
3. Invalid chapter names should fallback to `null` (all chapters)
4. Filter persists within session (sessionStorage)

**Example Usage**:
```typescript
// Dropdown options fetched from /api/chapters:
const options: ChapterFilterOption[] = [
  { value: null, label: "All Chapters", count: 246 },
  { value: "Chapter 1", label: "Chapter 1: Introduction", count: 42 },
  { value: "Chapter 2", label: "Chapter 2: Physical AI Systems", count: 38 },
  // ...
];
```

---

## Backend Entities (Python/Pydantic)

### 4. ChatRequest

**Purpose**: Request payload for `/api/chat` endpoint

**Location**: `rag-backend/main.py` (lines 144-149)

**Definition**:
```python
class ChatRequest(BaseModel):
    message: str                        # User's question
    session_id: Optional[str] = None    # UUID for conversation tracking
    selected_text: Optional[str] = None # Highlighted text for context
    chapter_filter: Optional[str] = None  # Filter by chapter (e.g., "Chapter 1")
    use_history: bool = True            # Include conversation history in context
```

**Fields**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `message` | `str` | Yes | User's question | Min length: 1 char, Max length: 1000 chars |
| `session_id` | `Optional[str]` | No | Conversation session UUID | Valid UUID v4 format if provided |
| `selected_text` | `Optional[str]` | No | Text selected by user | Max length: 5000 chars |
| `chapter_filter` | `Optional[str]` | No | Chapter to filter results | Must match available chapter names |
| `use_history` | `bool` | No | Include conversation context | Default: True |

**Validation Rules**:
1. `message` cannot be empty or whitespace-only
2. `message` length limited to prevent abuse (1000 chars = ~200 words)
3. `selected_text` limited to 5000 chars (reasonable paragraph size)
4. `session_id` validated as UUID v4 if provided, otherwise auto-generated
5. `chapter_filter` validated against available chapters (from `/api/chapters`)

**Example**:
```json
{
  "message": "How does ROS 2 work?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_text": null,
  "chapter_filter": "Chapter 3",
  "use_history": true
}
```

---

### 5. ChatResponse

**Purpose**: Response payload from `/api/chat` endpoint

**Location**: `rag-backend/main.py` (lines 158-163)

**Definition**:
```python
class ChatResponse(BaseModel):
    response: str              # LLM-generated answer
    sources: List[Source]      # Retrieved source citations
    citations: str             # Formatted citation text (markdown/footnote style)
    session_id: str            # UUID for conversation tracking
    in_scope: bool             # Whether question was in textbook scope
```

**Fields**:

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `response` | `str` | Yes | LLM-generated answer | Min length: 1 char, Max length: 4000 chars |
| `sources` | `List[Source]` | Yes | Retrieved citations | Min: 0 (if out of scope), Max: 10 |
| `citations` | `str` | Yes | Formatted citations | Max length: 2000 chars |
| `session_id` | `str` | Yes | Conversation UUID | Valid UUID v4 format |
| `in_scope` | `bool` | Yes | Textbook scope flag | True if answerable from textbook |

**Validation Rules**:
1. `response` cannot be empty unless `in_scope=false`
2. If `in_scope=true`, `sources` must have at least 1 entry
3. If `in_scope=false`, `sources` is empty and `response` contains out-of-scope message
4. `citations` format must match configured style (footnote/inline/apa)
5. `session_id` must match request session_id or be newly generated

**Example (In-Scope)**:
```json
{
  "response": "ROS 2 is a flexible framework...",
  "sources": [
    {
      "chapter": "Chapter 3",
      "title": "Robot Operating System (ROS 2)",
      "section": "ROS 2 Architecture",
      "score": 0.8523,
      "url": "http://localhost:3000/docs/chapter-3#ros-2-architecture"
    }
  ],
  "citations": "[1] Chapter 3: Robot Operating System (ROS 2) - ROS 2 Architecture",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "in_scope": true
}
```

**Example (Out-of-Scope)**:
```json
{
  "response": "I'm sorry, but your question about quantum computing doesn't appear to be covered in this textbook...",
  "sources": [],
  "citations": "",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "in_scope": false
}
```

---

### 6. Source (Backend)

**Purpose**: Source citation metadata (Pydantic model for API responses)

**Location**: `rag-backend/main.py` (lines 151-156)

**Definition**:
```python
class Source(BaseModel):
    chapter: str                 # Chapter identifier
    title: str                   # Chapter/section title
    section: Optional[str] = ""  # Subsection heading
    score: float                 # Vector similarity score (0.0 to 1.0)
    url: Optional[str] = ""      # Docusaurus URL to source
```

**Fields**: Same as Frontend Source entity (see above)

**Transformation**:
```python
# From Qdrant search result to Source:
def transform_search_result(hit: ScoredPoint) -> Source:
    url = generate_doc_url(
        file_path=hit.payload.get('file_path', ''),
        heading=hit.payload.get('heading', '')
    )
    return Source(
        chapter=hit.payload.get('chapter', 'Unknown'),
        title=hit.payload.get('title', ''),
        section=hit.payload.get('heading', ''),
        score=hit.score,
        url=url
    )
```

---

## Database Entities (SQLAlchemy)

### 7. User

**Purpose**: User account for authentication

**Location**: `rag-backend/models.py`

**Schema**:
```python
class User(Base):
    __tablename__ = "users"

    id: UUID (Primary Key)
    email: str (Unique, Index)
    password_hash: str
    name: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    # Relationships
    profile: UserProfile (1:1)
    chat_history: List[ChatHistory] (1:N)
```

**Validation Rules**:
1. Email must be valid format and unique
2. Password hashed with bcrypt (min 8 characters before hashing)
3. Name required (min 1 char)
4. UUID auto-generated on creation

---

### 8. UserProfile

**Purpose**: User personalization preferences (technical level, learning goals)

**Location**: `rag-backend/models.py`

**Schema**:
```python
class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: UUID (Primary Key)
    user_id: UUID (Foreign Key → users.id, Unique)
    technical_level: str  # "beginner", "intermediate", "advanced"
    programming_experience: List[str]  # ["Python", "C++", "ROS"]
    robotics_background: str  # Free text
    learning_goals: str  # Free text
    preferred_language: str = "en"  # "en", "ur", etc.
    created_at: datetime
    updated_at: datetime
```

**Validation Rules**:
1. `technical_level` must be one of: "beginner", "intermediate", "advanced"
2. `programming_experience` is JSON array of strings
3. `preferred_language` is ISO 639-1 language code

---

### 9. ChatHistory

**Purpose**: Persistent storage of conversation messages

**Location**: `rag-backend/models.py`

**Schema**:
```python
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id: UUID (Primary Key)
    user_id: UUID (Foreign Key → users.id)
    session_id: UUID (Index)
    role: str  # "user" or "assistant"
    content: str  # Message text
    sources: JSON  # List of Source objects (for assistant messages)
    timestamp: datetime

    # Indexes
    Index(user_id, session_id)
    Index(user_id, timestamp)
```

**Validation Rules**:
1. `role` must be "user" or "assistant"
2. `sources` is JSON-serialized list (empty for user messages)
3. Messages ordered by `timestamp` within each `session_id`

**Query Patterns**:
```python
# Get conversation by session_id:
messages = session.query(ChatHistory)\
    .filter_by(user_id=user.id, session_id=session_uuid)\
    .order_by(ChatHistory.timestamp.asc())\
    .all()

# Get user's recent sessions:
sessions = session.query(ChatHistory.session_id, func.max(ChatHistory.timestamp))\
    .filter_by(user_id=user.id)\
    .group_by(ChatHistory.session_id)\
    .order_by(func.max(ChatHistory.timestamp).desc())\
    .limit(10)\
    .all()
```

---

### 10. PersonalizationCache

**Purpose**: Cache LLM-generated personalized/translated content

**Location**: `rag-backend/models.py`

**Schema**:
```python
class PersonalizationCache(Base):
    __tablename__ = "personalization_cache"

    id: UUID (Primary Key)
    user_id: UUID (Foreign Key → users.id)
    chapter_id: str
    personalized_content: str  # LLM-generated content
    language: str = "en"
    created_at: datetime

    # Indexes
    Index(user_id, chapter_id, language) - Unique
```

**Validation Rules**:
1. `chapter_id` matches textbook chapter identifiers
2. `language` is ISO 639-1 language code
3. Unique constraint on (user_id, chapter_id, language) prevents duplicates

---

## Future Entities (Planned)

### 11. UserFeedback

**Purpose**: Track user feedback on chatbot answers (thumbs up/down)

**Location**: `rag-backend/models.py` (TO BE CREATED)

**Schema**:
```python
class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id: UUID (Primary Key)
    user_id: UUID (Foreign Key → users.id, Optional)
    chat_history_id: UUID (Foreign Key → chat_history.id)
    rating: str  # "positive" or "negative"
    comment: str (Optional)  # Free text feedback
    timestamp: datetime

    # Indexes
    Index(user_id, timestamp)
    Index(chat_history_id)
    Index(rating, timestamp)
```

**Validation Rules**:
1. `rating` must be "positive" or "negative"
2. `comment` max length: 1000 chars
3. `user_id` can be null for anonymous feedback

**Analytics Queries**:
```python
# Get feedback rate:
total_messages = session.query(func.count(ChatHistory.id)).filter_by(role='assistant').scalar()
total_feedback = session.query(func.count(UserFeedback.id)).scalar()
feedback_rate = total_feedback / total_messages

# Get negative feedback rate:
negative_count = session.query(func.count(UserFeedback.id)).filter_by(rating='negative').scalar()
negative_rate = negative_count / total_feedback
```

---

## Data Flow

### Chat Request Flow

```
[User types message in Chatbot.tsx]
  ↓
[ChatMessage created (role: 'user')]
  ↓
[Added to messages state array]
  ↓
[Saved to sessionStorage]
  ↓
[POST /api/chat (ChatRequest)]
  ↓
[Backend: Vector search → LLM generation → Citation formatting]
  ↓
[Backend: ChatResponse returned]
  ↓
[Frontend: ChatMessage created (role: 'assistant', sources: [...])]
  ↓
[Added to messages state array]
  ↓
[Saved to sessionStorage]
  ↓
[If authenticated: Saved to ChatHistory database]
  ↓
[Rendered in chat UI with sources and citations]
```

### Session Storage Format

```typescript
// sessionStorage.getItem('chatbot-messages')
{
  "messages": [
    {
      "role": "user",
      "content": "What is embodied intelligence?",
      "timestamp": "2025-12-26T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Embodied intelligence refers to...",
      "sources": [
        {
          "chapter": "Chapter 1",
          "title": "Introduction",
          "section": "Embodied Intelligence",
          "score": 0.85,
          "url": "http://localhost:3000/docs/chapter-1#embodied-intelligence"
        }
      ],
      "citations": "[1] Chapter 1: Introduction - Embodied Intelligence",
      "in_scope": true,
      "timestamp": "2025-12-26T10:30:03Z"
    }
  ],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filter": null  // or "Chapter 1"
}
```

---

## Validation Summary

### Frontend Validation (TypeScript)

1. **Before sending to backend**:
   - Message non-empty: `message.trim().length > 0`
   - Message max length: `message.length <= 1000`
   - Session ID valid UUID: `/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i`

2. **When rendering messages**:
   - Sources sorted by score descending
   - Scores displayed as percentages (0-100%)
   - URLs validated before rendering links

### Backend Validation (Pydantic)

1. **ChatRequest**:
   - Message required and non-empty
   - Selected text max 5000 chars
   - Chapter filter matches available chapters
   - Session ID valid UUID v4

2. **ChatResponse**:
   - Response non-empty if in_scope=true
   - Sources present if in_scope=true
   - Session ID matches request

3. **Source**:
   - Score between 0.0 and 1.0
   - URL valid HTTP/HTTPS format
   - Chapter matches naming pattern

### Database Validation (SQLAlchemy)

1. **User**:
   - Email unique and valid format
   - Password hash min length (bcrypt output)

2. **ChatHistory**:
   - Role must be 'user' or 'assistant'
   - Sources valid JSON format

3. **PersonalizationCache**:
   - Unique constraint on (user_id, chapter_id, language)

---

## State Transitions

### Message Lifecycle

```
[Draft] → [Sending] → [Sent] → [Delivered] → [Answered] → [Rated]
   ↓         ↓          ↓          ↓            ↓            ↓
 User      Frontend   Backend   Frontend    Frontend    Frontend
 types     sends      receives  displays    displays    user
 message   request    request   loading     response    rates
```

### Conversation Session States

```
[New Session] → [Active] → [Idle] → [Expired]
       ↓           ↓          ↓          ↓
   UUID gen    Messages   15min      Delete
   created     exchanged  timeout    from memory
                          (remains   (remains in
                           in DB)     DB)
```

### Cache States (PersonalizationCache)

```
[Miss] → [Generating] → [Cached] → [Stale] → [Invalidated]
   ↓          ↓            ↓          ↓           ↓
 First     LLM call    Served     24hrs       Chapter
 request   in prog     from DB    passed      updated
```

---

## Relationships

### User ↔ ChatHistory (1:N)
- One user can have many conversation messages
- ChatHistory references user via `user_id` foreign key
- Cascade delete: Delete user → delete all their chat history

### User ↔ UserProfile (1:1)
- One user has exactly one profile
- UserProfile references user via `user_id` foreign key (unique)
- Cascade delete: Delete user → delete their profile

### ChatHistory ↔ UserFeedback (1:1)
- Each assistant message can have one feedback entry
- UserFeedback references message via `chat_history_id`
- Cascade delete: Delete message → delete its feedback

### User ↔ PersonalizationCache (1:N)
- One user can have many cached personalizations (one per chapter per language)
- PersonalizationCache references user via `user_id`
- Cascade delete: Delete user → delete their cache entries

---

## Indexes

### Performance Optimization

**ChatHistory**:
- `(user_id, session_id)` - Fast session message retrieval
- `(user_id, timestamp)` - Recent conversations query
- `session_id` - Group messages by session

**UserFeedback** (future):
- `(user_id, timestamp)` - User feedback history
- `chat_history_id` - Feedback for specific message
- `(rating, timestamp)` - Aggregate feedback stats

**PersonalizationCache**:
- `(user_id, chapter_id, language)` - UNIQUE - Fast cache lookup

---

## Migrations

### Initial Schema (Existing)
- ✅ Users, UserProfiles, ChatHistory, PersonalizationCache already defined in `models.py`

### Pending Migrations
1. **Add `timestamp` field to ChatHistory** (if missing)
2. **Add `snippet` field to Source metadata** (Qdrant payload)
3. **Create UserFeedback table** (future)
4. **Add indexes for performance** (if not already created)

---

**Data Model Status**: ✅ COMPLETE

**Ready for**: API contract definition (contracts/chat-api.yaml)
