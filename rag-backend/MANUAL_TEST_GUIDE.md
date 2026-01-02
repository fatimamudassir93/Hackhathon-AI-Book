# Chatbot Manual Test Guide

**Date**: 2025-12-26
**Purpose**: Step-by-step manual testing checklist for frontend chatbot integration
**Prerequisites**: Backend running on http://localhost:8000, Frontend on http://localhost:3000

---

## Test Setup

1. **Start Backend** (if not running):
   ```bash
   cd rag-backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend** (if not running):
   ```bash
   cd physical-ai-book
   npm run start
   ```

3. **Verify Backend Health**:
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status":"healthy","qdrant_connected":true,...}
   ```

---

## Test Suite 1: Basic Chatbot Functionality

### Test 1.1: Open Chatbot
**Steps**:
1. Navigate to http://localhost:3000
2. Look for chatbot button/icon (usually bottom-right corner)
3. Click to open chatbot

**Expected**:
- ✅ Chatbot window opens
- ✅ Clean UI with input field visible
- ✅ No error messages

**Status**: [ ] Pass [ ] Fail

---

### Test 1.2: Simple Question
**Steps**:
1. Type: "What is embodied intelligence?"
2. Press Enter or click Send

**Expected**:
- ✅ Loading indicator appears
- ✅ Response appears within 3 seconds
- ✅ Response is relevant to embodied intelligence
- ✅ Sources section appears below response
- ✅ At least 1 source listed with chapter and relevance score

**Actual Results**:
```
Response time: _____ seconds
Response length: _____ characters
Number of sources: _____
Relevance: [ ] High [ ] Medium [ ] Low
```

**Status**: [ ] Pass [ ] Fail

---

### Test 1.3: Follow-up Question
**Steps**:
1. Type: "Can you explain that in simpler terms?"
2. Press Enter

**Expected**:
- ✅ Response references previous context
- ✅ Simpler explanation provided
- ✅ Sources still present

**Status**: [ ] Pass [ ] Fail

---

## Test Suite 2: Chapter Filtering

### Test 2.1: Filter by Chapter
**Steps**:
1. Look for chapter filter dropdown (if available)
2. Select "Chapter 3: Software Frameworks"
3. Type: "How does ROS 2 work?"
4. Press Enter

**Expected**:
- ✅ Response generated
- ✅ All sources are from Chapter 3
- ✅ Source chapter names display "Chapter 3"

**Actual Results**:
```
Sources from Chapter 3: _____ / _____
All sources match filter: [ ] Yes [ ] No
```

**Status**: [ ] Pass [ ] Fail

---

### Test 2.2: Clear Filter
**Steps**:
1. Clear/reset chapter filter
2. Type: "What is SLAM?"
3. Press Enter

**Expected**:
- ✅ Response generated
- ✅ Sources from multiple chapters (Chapter 4 likely dominant)

**Actual Results**:
```
Chapters in sources: _____________________
```

**Status**: [ ] Pass [ ] Fail

---

## Test Suite 3: Out-of-Scope Detection

### Test 3.1: Completely Unrelated Topic
**Steps**:
1. Type: "What is quantum computing?"
2. Press Enter

**Expected**:
- ✅ Response indicates topic is outside book scope
- ✅ Message suggests asking about robotics/AI topics
- ✅ No sources displayed OR low relevance scores (<40%)

**Actual Response**:
```
[Paste response here]
```

**Status**: [ ] Pass [ ] Fail

---

### Test 3.2: Another Unrelated Topic
**Steps**:
1. Type: "How do I bake a cake?"
2. Press Enter

**Expected**:
- ✅ Out-of-scope message
- ✅ Helpful redirection

**Status**: [ ] Pass [ ] Fail

---

## Test Suite 4: Selected Text Context (if implemented)

### Test 4.1: Highlight and Ask
**Steps**:
1. Navigate to any chapter page (e.g., Chapter 1)
2. Highlight/select a paragraph of text (>20 characters)
3. Open chatbot
4. Type: "Can you explain this?"
5. Press Enter

**Expected**:
- ✅ Response references the selected text
- ✅ Contextual answer provided
- ✅ Sources relevant to selected text

**Status**: [ ] Pass [ ] Fail [ ] Not Implemented

---

## Test Suite 5: Performance & UX

### Test 5.1: Response Time
**Steps**:
1. Ask 3 different questions:
   - "What is embodied intelligence?"
   - "Explain inverse kinematics"
   - "What is ROS 2?"
2. Measure response time for each

**Expected**:
- ✅ All responses < 3 seconds
- ✅ Average response time < 2 seconds

**Actual Results**:
```
Question 1: _____ seconds
Question 2: _____ seconds
Question 3: _____ seconds
Average: _____ seconds
```

**Status**: [ ] Pass [ ] Fail

---

### Test 5.2: UI Responsiveness
**Steps**:
1. Type a question
2. While waiting for response, check:
   - Can you scroll chat history?
   - Is input field disabled during loading?
   - Is loading indicator clear and visible?

**Expected**:
- ✅ Smooth scrolling
- ✅ Input disabled during loading (prevents duplicate requests)
- ✅ Clear loading state

**Status**: [ ] Pass [ ] Fail

---

### Test 5.3: Mobile Responsiveness (if applicable)
**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (responsive mode)
3. Test chatbot on mobile viewport (375x667)

**Expected**:
- ✅ Chatbot opens properly
- ✅ Input field usable
- ✅ Messages readable

**Status**: [ ] Pass [ ] Fail [ ] Not Applicable

---

## Test Suite 6: Error Handling

### Test 6.1: Empty Message
**Steps**:
1. Click Send without typing anything
2. Or type only spaces and press Enter

**Expected**:
- ✅ Validation message appears
- ✅ No request sent to backend
- ✅ User prompted to enter a message

**Status**: [ ] Pass [ ] Fail

---

### Test 6.2: Network Error Simulation
**Steps**:
1. Stop backend server (Ctrl+C in backend terminal)
2. Type a question and send
3. Wait for response

**Expected**:
- ✅ Error message displayed
- ✅ User informed of connection issue
- ✅ No crash or blank screen

**Actual Behavior**:
```
[Describe what happens]
```

**Status**: [ ] Pass [ ] Fail

---

### Test 6.3: Recovery After Error
**Steps**:
1. Restart backend server
2. Type a new question and send

**Expected**:
- ✅ Chatbot works normally again
- ✅ Previous error cleared

**Status**: [ ] Pass [ ] Fail

---

## Test Suite 7: Citations & Sources

### Test 7.1: Source Information
**Steps**:
1. Ask: "What is embodied intelligence?"
2. Examine sources section

**Expected**:
- ✅ Each source shows:
  - Chapter name
  - Relevance score (percentage or decimal)
  - Text snippet/preview
  - (Optional) Link to source location

**Actual Sources Display**:
```
Source 1: Chapter _____, Score: _____, Preview: _____
Source 2: Chapter _____, Score: _____, Preview: _____
...
```

**Status**: [ ] Pass [ ] Fail

---

### Test 7.2: Source Links (if implemented)
**Steps**:
1. Click on a source citation/link
2. Verify navigation

**Expected**:
- ✅ Navigates to chapter page
- ✅ Highlights or scrolls to relevant section

**Status**: [ ] Pass [ ] Fail [ ] Not Implemented

---

## Test Suite 8: Conversation History

### Test 8.1: Message History
**Steps**:
1. Ask 3 different questions sequentially
2. Scroll up in chat window

**Expected**:
- ✅ All messages visible
- ✅ User messages clearly distinguished from bot responses
- ✅ Sources preserved for each response

**Status**: [ ] Pass [ ] Fail

---

### Test 8.2: Session Persistence
**Steps**:
1. Ask a question and get response
2. Refresh the page (F5)
3. Reopen chatbot

**Expected**:
- ✅ Conversation history preserved (if sessionStorage implemented)
- OR
- ✅ Chat starts fresh (if session persistence not implemented)

**Status**: [ ] Pass [ ] Fail [ ] Not Implemented

---

## Summary Report

### Overall Results

**Total Tests**: _____
**Passed**: _____
**Failed**: _____
**Not Implemented/Applicable**: _____

**Pass Rate**: _____%

---

### Critical Issues Found

1. _____________________________________________________
2. _____________________________________________________
3. _____________________________________________________

---

### Nice-to-Have Improvements

1. _____________________________________________________
2. _____________________________________________________
3. _____________________________________________________

---

### Tester Notes

```
[Add any additional observations, bugs, or suggestions]
```

---

### Sign-off

**Tester**: _____________________
**Date**: _____________________
**Build Version**: _____________________
**Overall Status**: [ ] Ready for Production [ ] Needs Work [ ] Blocked

---

## Quick Test (5 minutes)

If short on time, run this minimal test:

1. **Health Check**: Open chatbot ✅
2. **Basic Q&A**: Ask "What is embodied intelligence?" ✅
3. **Chapter Filter**: Filter to Chapter 3, ask about ROS 2 ✅
4. **Out-of-Scope**: Ask "What is quantum computing?" ✅
5. **Performance**: Verify response < 3 seconds ✅

**Quick Test Result**: [ ] Pass [ ] Fail
