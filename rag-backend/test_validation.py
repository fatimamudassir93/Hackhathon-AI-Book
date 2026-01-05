"""Test script to check ChatRequest validation"""
import json
from main import ChatRequest

# Test 1: Basic valid request
test_data = {
    "message": "What is physical AI?",
    "use_history": True
}

print("Test 1: Basic request")
print("Request data:", json.dumps(test_data, indent=2))
try:
    req = ChatRequest(**test_data)
    print("✓ Valid request")
    print("Model:", req)
except Exception as e:
    print(f"✗ Validation error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Request with all fields
test_data_full = {
    "message": "What is physical AI?",
    "session_id": "test-session-123",
    "selected_text": None,
    "chapter_filter": None,
    "use_history": True
}

print("Test 2: Request with all fields (explicit None)")
print("Request data:", json.dumps(test_data_full, indent=2))
try:
    req = ChatRequest(**test_data_full)
    print("✓ Valid request")
    print("Model:", req)
except Exception as e:
    print(f"✗ Validation error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Test what the frontend is actually sending
test_data_frontend = {
    "message": "What is physical AI?",
    "selected_text": None,
    "chapter_filter": None,
    "use_history": True
}

print("Test 3: Frontend-style request")
print("Request data:", json.dumps(test_data_frontend, indent=2))
try:
    req = ChatRequest(**test_data_frontend)
    print("✓ Valid request")
    print("Model:", req)
    print("JSON representation:", req.model_dump_json())
except Exception as e:
    print(f"✗ Validation error: {e}")
