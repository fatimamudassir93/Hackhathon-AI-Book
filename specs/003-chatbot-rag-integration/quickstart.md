# Developer Quickstart: Chatbot RAG Integration

**Feature**: 003-chatbot-rag-integration
**Date**: 2025-12-26
**Status**: Complete

## Overview

This guide helps developers quickly set up and test the chatbot RAG integration locally. Follow these steps to run the full stack (backend + frontend) and verify the integration works.

**Prerequisites**:
- Python 3.10+ installed
- Node.js 18+ and npm installed
- Git installed
- Code editor (VS Code recommended)
- ~500MB disk space for dependencies

**Estimated Setup Time**: 15-20 minutes (first time)

---

## Architecture Overview

```
┌─────────────────────┐
│  Frontend           │
│  (Docusaurus)       │
│  Port: 3000         │
│                     │
│  Chatbot.tsx        │
│  ChatbotFilters.tsx │
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌─────────────────────┐
│  Backend            │
│  (FastAPI)          │
│  Port: 8000         │
│                     │
│  /api/chat endpoint │
└──────────┬──────────┘
           │
           ├─────────────┐
           │             │
           ▼             ▼
┌──────────────┐  ┌──────────────┐
│  Qdrant      │  │  LLM APIs    │
│  (Cloud)     │  │  (Groq/      │
│              │  │   Gemini)    │
│  246 vectors │  │              │
└──────────────┘  └──────────────┘
```

---

## Part 1: Backend Setup (RAG API)

### Step 1: Navigate to Backend Directory

```bash
cd rag-backend
```

### Step 2: Create Python Virtual Environment

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify**:
```bash
python --version  # Should show Python 3.10+
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected packages** (main dependencies):
- fastapi
- uvicorn
- qdrant-client
- sentence-transformers
- groq (or google-generativeai)
- python-dotenv
- sqlalchemy
- pydantic

**Installation time**: ~2-3 minutes (downloading models)

### Step 4: Configure Environment Variables

Create `.env` file in `rag-backend/` directory:

```bash
# .env (rag-backend/.env)

# Qdrant Vector Database (REQUIRED)
QDRANT_HOST=https://your-qdrant-instance.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=physical_ai_book

# LLM Provider (REQUIRED - choose ONE or both)
# Option 1: Groq (Primary - Free tier available)
GROQ_API_KEY=your_groq_api_key_here

# Option 2: Google Gemini (Fallback)
GEMINI_API_KEY=your_gemini_api_key_here

# Embedding Model (OPTIONAL - uses local model by default)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Docusaurus Base URL (REQUIRED for citation links)
DOCUSAURUS_BASE_URL=http://localhost:3000

# Database (OPTIONAL - defaults to SQLite)
DATABASE_URL=sqlite:///./chatbot.db

# Rate Limiting (OPTIONAL)
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
```

**How to get API keys**:

**Qdrant**:
1. Go to https://cloud.qdrant.io
2. Sign up for free account
3. Create a cluster (free tier available)
4. Copy cluster URL and API key from dashboard
5. Note: The collection `physical_ai_book` should already exist with 246 vectors

**Groq** (Recommended - Fast and Free):
1. Go to https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key
5. Free tier: ~30 requests/minute

**Gemini** (Optional Fallback):
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Free tier: 60 requests/minute

### Step 5: Verify Database and Vector Store

**Check Qdrant connection**:
```bash
python -c "from qdrant_client import QdrantClient; import os; from dotenv import load_dotenv; load_dotenv(); client = QdrantClient(url=os.getenv('QDRANT_HOST'), api_key=os.getenv('QDRANT_API_KEY')); print('Collections:', [c.name for c in client.get_collections().collections])"
```

**Expected output**:
```
Collections: ['physical_ai_book']
```

**Check vector count**:
```bash
python -c "from qdrant_client import QdrantClient; import os; from dotenv import load_dotenv; load_dotenv(); client = QdrantClient(url=os.getenv('QDRANT_HOST'), api_key=os.getenv('QDRANT_API_KEY')); info = client.get_collection('physical_ai_book'); print(f'Vectors: {info.points_count}')"
```

**Expected output**:
```
Vectors: 246
```

### Step 6: Run Backend Server

```bash
uvicorn main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 7: Test Backend API

**Open new terminal** (keep backend running) and test health check:

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "qdrant_collection_exists": true,
  "database_connected": true
}
```

**Test chat endpoint**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is embodied intelligence?",
    "chapter_filter": null,
    "use_history": true
  }'
```

**Expected response** (truncated):
```json
{
  "response": "Embodied intelligence refers to...",
  "sources": [
    {
      "chapter": "Chapter 1",
      "title": "Introduction to Physical AI",
      "section": "Embodied Intelligence",
      "score": 0.85,
      "url": "http://localhost:3000/docs/chapter-1#embodied-intelligence"
    }
  ],
  "citations": "[1] Chapter 1: Introduction...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "in_scope": true
}
```

**Test chapter filtering**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does ROS 2 work?",
    "chapter_filter": "Chapter 3",
    "use_history": true
  }'
```

**Get available chapters**:
```bash
curl http://localhost:8000/api/chapters
```

**Expected response**:
```json
{
  "chapters": ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4", "Chapter 5", "Chapter 6"],
  "count": 6
}
```

---

## Part 2: Frontend Setup (Docusaurus Chatbot)

### Step 1: Navigate to Frontend Directory

```bash
cd ../physical-ai-book
```

### Step 2: Install Dependencies

```bash
npm install
```

**Installation time**: ~3-5 minutes

### Step 3: Configure API URL (Optional)

The chatbot automatically uses `http://localhost:8000` for local development. To override, edit `src/components/Chatbot.tsx`:

```typescript
// Line 27
const Chatbot: React.FC<ChatbotProps> = ({ apiUrl = 'http://localhost:8000' }) => {
```

Or pass as prop in the parent component.

### Step 4: Run Frontend Server

```bash
npm run start
```

**Expected output**:
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

**Build time**: ~30 seconds (first time)

### Step 5: Test Chatbot UI

1. **Open browser**: Navigate to http://localhost:3000
2. **Open chatbot**: Click floating chat button (💬) in bottom-right corner
3. **Ask question**: Type "What is embodied intelligence?" and press Enter
4. **Verify response**:
   - Loading indicator appears
   - Answer displays with markdown formatting
   - Sources section shows chapter citations with relevance scores
   - Citations are clickable (if URL generation is implemented)

**Expected UI**:
```
┌─────────────────────────────────┐
│ 📚 Ask about the Book          │
│ [Filter: All Chapters ▼]  [✕]  │
├─────────────────────────────────┤
│ User                            │
│ What is embodied intelligence? │
├─────────────────────────────────┤
│ Assistant                       │
│ Embodied intelligence refers   │
│ to the concept that...          │
│                                 │
│ 📖 Sources:                     │
│ • Chapter 1 - Embodied          │
│   Intelligence (85%)            │
│ • Chapter 1 - Physical AI       │
│   Paradigm (72%)                │
└─────────────────────────────────┘
```

---

## Part 3: Testing Integration

### Test Scenario 1: Basic Question-Answer

**Steps**:
1. Open chatbot
2. Ask: "What is SLAM?"
3. Verify response mentions "Simultaneous Localization and Mapping"
4. Check sources include Chapter 4 or Chapter 5

**Expected behavior**:
- Response time: <3 seconds
- At least 1 source citation
- Relevance score > 50%

### Test Scenario 2: Chapter Filtering

**Steps**:
1. Open chatbot
2. Select "Chapter 3" from filter dropdown
3. Ask: "How does ROS 2 work?"
4. Verify ALL sources are from Chapter 3

**Expected behavior**:
- Sources filtered correctly
- Answer still relevant and complete
- If no results in Chapter 3, shows "no relevant content" message

### Test Scenario 3: Text Selection Context

**Steps**:
1. Navigate to any chapter page (e.g., http://localhost:3000/docs/chapter-1)
2. Highlight text (e.g., select a paragraph about "embodied intelligence")
3. Open chatbot
4. Notice "Text selected" badge appears
5. Ask: "Can you explain this in simpler terms?"
6. Click "Ask Selection" button

**Expected behavior**:
- Chatbot sends selected_text in API request
- Response is contextually relevant to selected text
- Sources may include the current chapter

### Test Scenario 4: Out-of-Scope Question

**Steps**:
1. Open chatbot
2. Ask: "What is quantum computing?"
3. Verify response indicates question is out of scope

**Expected behavior**:
- Response explains question is not covered in textbook
- No sources listed
- Suggests related in-scope topics (optional)
- `in_scope: false` in API response

### Test Scenario 5: Error Handling

**Steps**:
1. **Stop backend server** (Ctrl+C in backend terminal)
2. Open chatbot
3. Ask any question
4. Verify error message appears

**Expected behavior**:
- Error message: "🔌 Cannot connect to the backend server..."
- Suggests checking backend is running
- No crash or blank screen

### Test Scenario 6: Conversation History

**Steps**:
1. Open chatbot
2. Ask 3 different questions
3. Refresh page
4. Reopen chatbot

**Expected behavior** (with sessionStorage):
- All 3 questions and answers still visible
- Scroll position maintained
- Session ID preserved

**Expected behavior** (without sessionStorage - current):
- Messages lost on refresh
- Fresh start

---

## Part 4: Development Workflow

### Running Both Servers Simultaneously

**Terminal 1** (Backend):
```bash
cd rag-backend
venv\Scripts\activate  # or source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2** (Frontend):
```bash
cd physical-ai-book
npm run start
```

**Terminal 3** (Testing):
```bash
# Run tests, make API calls, etc.
curl http://localhost:8000/health
```

### Hot Reloading

**Backend**:
- Changes to `.py` files auto-reload (via `--reload` flag)
- Changes to `.env` require manual restart

**Frontend**:
- Changes to `.tsx` files auto-reload
- Browser refreshes automatically

### Debugging

**Backend Debugging**:
```python
# Add breakpoints with:
import pdb; pdb.set_trace()

# Or use VS Code debugger:
# 1. Create .vscode/launch.json
# 2. Add FastAPI configuration
# 3. Set breakpoints in VS Code
# 4. Press F5 to start debugging
```

**Frontend Debugging**:
- Open browser DevTools (F12)
- Check Console for errors
- Check Network tab for API requests
- Use React DevTools extension

**API Request Logging**:
```typescript
// In Chatbot.tsx, add console.log:
console.log('Sending request:', {
  message: input,
  chapter_filter: chapterFilter,
  selected_text: selectedText
});

const ragResults = await queryRAG(input, useSelectedText);
console.log('Received response:', ragResults);
```

---

## Part 5: Common Issues and Troubleshooting

### Issue 1: Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: Qdrant connection failed

**Error**: `RuntimeError: Failed to connect to Qdrant`

**Solution**:
1. Check `.env` has correct `QDRANT_HOST` and `QDRANT_API_KEY`
2. Verify Qdrant Cloud cluster is running (check dashboard)
3. Test connection manually:
   ```bash
   curl https://your-cluster.qdrant.io/collections \
     -H "api-key: your_api_key"
   ```

### Issue 3: LLM generation fails

**Error**: `Response generation error: Failed to generate a response`

**Solution**:
1. Check API keys in `.env` (GROQ_API_KEY or GEMINI_API_KEY)
2. Verify API key is valid (test in provider console)
3. Check rate limits (Groq free tier: ~30 req/min)
4. Try fallback provider

### Issue 4: No sources returned

**Error**: Empty `sources` array in response

**Solution**:
1. Verify Qdrant collection has 246 vectors:
   ```bash
   curl http://localhost:8000/api/ingestion/status
   ```
2. Check chapter_filter is valid (matches available chapters)
3. Try broader question (e.g., "What is physical AI?")

### Issue 5: Frontend can't connect to backend

**Error**: "🔌 Cannot connect to the backend server"

**Solution**:
1. Verify backend is running on port 8000:
   ```bash
   curl http://localhost:8000/health
   ```
2. Check CORS settings in `main.py` (should allow `http://localhost:3000`)
3. Check browser console for CORS errors
4. Try disabling browser extensions (ad blockers)

### Issue 6: Citation URLs don't work

**Error**: Clicking source links gives 404

**Solution**:
1. Check `DOCUSAURUS_BASE_URL` in backend `.env` (should be `http://localhost:3000`)
2. Verify Docusaurus chapter URLs match generated URLs
3. Check anchor generation logic in `citation_formatter.py`

---

## Part 6: Next Steps After Setup

### Development Tasks

**Priority 1** (Core Functionality Gaps):
- [ ] Implement citation URL generation (backend `citation_formatter.py`)
- [ ] Add sessionStorage for conversation history (frontend)
- [ ] Write integration tests for `/api/chat` endpoint
- [ ] Add performance monitoring (track response times)

**Priority 2** (UX Improvements):
- [ ] Implement user feedback UI (thumbs up/down)
- [ ] Add retry button for failed requests
- [ ] Improve out-of-scope messages with suggestions
- [ ] Add streaming response support (SSE)

**Priority 3** (Testing & Documentation):
- [ ] Write unit tests for frontend components
- [ ] Write E2E tests (Playwright/Cypress)
- [ ] Create user documentation (how to use chatbot)
- [ ] Performance benchmarking (measure p90 response time)

### Testing Commands

**Backend Tests** (to be written):
```bash
cd rag-backend
pytest tests/
```

**Frontend Tests** (to be written):
```bash
cd physical-ai-book
npm run test
```

**E2E Tests** (to be written):
```bash
npx playwright test
```

### Performance Profiling

**Backend Metrics**:
```bash
curl http://localhost:8000/api/performance/metrics
```

**Expected output**:
```json
{
  "timestamp": "2025-12-26T10:30:00Z",
  "metrics": {
    "chat": {
      "count": 42,
      "avg_duration": 2.3,
      "min_duration": 1.2,
      "max_duration": 4.5,
      "p95_duration": 3.2
    }
  }
}
```

---

## Part 7: Environment Cheat Sheet

### Backend (.env)

```bash
# Minimum required for local development
QDRANT_HOST=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
DOCUSAURUS_BASE_URL=http://localhost:3000
```

### Frontend (No .env needed for local dev)

API URL is hardcoded in `Chatbot.tsx` as `http://localhost:8000`

---

## Part 8: Production Deployment (Future)

### Backend Deployment (e.g., Render, Railway, Fly.io)

**Environment Variables**:
```bash
QDRANT_HOST=https://prod-cluster.qdrant.io
QDRANT_API_KEY=prod_api_key
GROQ_API_KEY=prod_groq_key
DOCUSAURUS_BASE_URL=https://physical-ai-book.vercel.app
DATABASE_URL=postgresql://user:pass@host/db
```

**Dockerfile** (if needed):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment (Vercel/Netlify)

**Build Command**: `npm run build`
**Output Directory**: `build`
**Environment Variables**:
```bash
REACT_APP_API_URL=https://api.physical-ai-book.com
```

---

## Summary

**What We Set Up**:
- ✅ Backend RAG API (FastAPI, Qdrant, LLM)
- ✅ Frontend chatbot UI (React, Docusaurus)
- ✅ Integration testing (manual verification)
- ✅ Development workflow (hot reloading, debugging)

**What Works**:
- Natural language Q&A with source citations
- Chapter filtering
- Text selection context
- Error handling
- Conversation history (in-memory)

**What's Next**:
- Implement remaining features (citation URLs, feedback UI, session storage)
- Write automated tests (unit, integration, E2E)
- Performance optimization (streaming, caching)
- Production deployment

**Estimated Development Time**:
- P1 tasks (core gaps): ~2-3 days
- P2 tasks (UX improvements): ~2-3 days
- P3 tasks (testing & docs): ~3-4 days
- **Total**: ~1-2 weeks for full feature completion

---

**Questions? Issues?**
- Check [plan.md](./plan.md) for architecture details
- Check [research.md](./research.md) for technical decisions
- Check [data-model.md](./data-model.md) for entity definitions
- Check [contracts/chat-api.yaml](./contracts/chat-api.yaml) for API spec

**Last Updated**: 2025-12-26
