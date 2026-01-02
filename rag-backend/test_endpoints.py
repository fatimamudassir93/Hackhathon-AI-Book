"""
Diagnostic script to test all enhanced features endpoints
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== TESTING HEALTH ENDPOINT ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        print("Backend may not be running. Start with: python main.py")
        return False

def test_chat_anonymous():
    """Test chat endpoint without authentication"""
    print("\n=== TESTING CHAT (ANONYMOUS) ===")
    try:
        payload = {
            "message": "What is Physical AI?",
            "use_history": False
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response preview: {data.get('response', '')[:100]}...")
            print(f"Sources count: {len(data.get('sources', []))}")
            print("CHAT WORKS: OK")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_signup():
    """Test user signup"""
    print("\n=== TESTING SIGNUP ===")
    try:
        payload = {
            "email": f"test_user_{os.urandom(4).hex()}@example.com",
            "password": "SecurePassword123!",
            "name": "Test User",
            "technical_level": "intermediate",
            "programming_experience": ["python", "javascript"],
            "robotics_background": "hobbyist",
            "learning_goals": "Learn Physical AI fundamentals"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"Token received: {token[:20]}...")
            print("SIGNUP WORKS: OK")
            return token
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_personalization(token):
    """Test personalization endpoint"""
    print("\n=== TESTING PERSONALIZATION ===")
    if not token:
        print("SKIPPED: No authentication token")
        return False

    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "chapter_id": "test-chapter-1",
            "chapter_content": "# Introduction to Physical AI\n\nPhysical AI involves embodied intelligence in robots."
        }
        response = requests.post(
            f"{BASE_URL}/api/personalize/test-chapter-1",
            json=payload,
            headers=headers,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Personalized content preview: {data.get('content', '')[:100]}...")
            print(f"Language: {data.get('language')}")
            print("PERSONALIZATION WORKS: OK")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_translation(token):
    """Test translation endpoint"""
    print("\n=== TESTING TRANSLATION ===")
    if not token:
        print("SKIPPED: No authentication token")
        return False

    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "chapter_id": "test-chapter-2",
            "chapter_content": "# Physical AI Basics\n\nThis chapter covers the fundamentals.",
            "target_language": "ur"
        }
        response = requests.post(
            f"{BASE_URL}/api/translate/test-chapter-2",
            json=payload,
            headers=headers,
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Translated content preview: {data.get('content', '')[:100]}...")
            print(f"Language: {data.get('language')}")
            print("TRANSLATION WORKS: OK")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED FEATURES DIAGNOSTIC TEST")
    print("=" * 60)

    # Test health
    if not test_health():
        print("\n[FATAL] Backend not running or not accessible")
        print("Start backend with: cd rag-backend && python main.py")
        exit(1)

    # Test chat
    chat_ok = test_chat_anonymous()

    # Test signup and get token
    token = test_signup()

    # Test personalization
    personalization_ok = test_personalization(token)

    # Test translation
    translation_ok = test_translation(token)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Health Check:      {'PASS' if True else 'FAIL'}")
    print(f"Chat (Anonymous):  {'PASS' if chat_ok else 'FAIL'}")
    print(f"Signup:            {'PASS' if token else 'FAIL'}")
    print(f"Personalization:   {'PASS' if personalization_ok else 'FAIL'}")
    print(f"Translation:       {'PASS' if translation_ok else 'FAIL'}")
    print("=" * 60)

    if not all([chat_ok, token, personalization_ok, translation_ok]):
        print("\nSome tests failed. Check errors above for details.")
        exit(1)
    else:
        print("\nAll tests PASSED! Features are working correctly.")
