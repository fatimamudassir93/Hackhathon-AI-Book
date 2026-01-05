"""
Comprehensive test suite for /api/chat endpoint
Tests the full RAG pipeline: query -> retrieval -> LLM generation -> response
"""
import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_TIMEOUT = 30  # seconds

print("Chatbot API Test Suite")
print("=" * 80)
print(f"Testing endpoint: {BASE_URL}/api/chat")
print(f"Timeout: {TEST_TIMEOUT}s")
print("=" * 80)
print()


class ChatbotTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, name: str, passed: bool, message: str, duration: float = 0):
        """Log test result"""
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if message:
            print(f"     {message}")
        if duration > 0:
            print(f"     Duration: {duration:.2f}s")

        self.test_results.append({
            "name": name,
            "passed": passed,
            "message": message,
            "duration": duration
        })
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def test_health_check(self):
        """Test 1: Health check endpoint"""
        print("\nTest 1: Health Check")
        print("-" * 80)

        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                all_healthy = (
                    data.get("status") == "healthy" and
                    data.get("qdrant_connected") == True and
                    data.get("qdrant_collection_exists") == True and
                    data.get("database_connected") == True
                )

                if all_healthy:
                    self.log_test("Health check", True, "All systems operational")
                else:
                    issues = []
                    if not data.get("qdrant_connected"):
                        issues.append("Qdrant disconnected")
                    if not data.get("qdrant_collection_exists"):
                        issues.append("Collection missing")
                    if not data.get("database_connected"):
                        issues.append("Database disconnected")
                    self.log_test("Health check", False, f"Issues: {', '.join(issues)}")
            else:
                self.log_test("Health check", False, f"HTTP {response.status_code}")

        except Exception as e:
            self.log_test("Health check", False, f"Error: {e}")

    def test_basic_question(self):
        """Test 2: Basic question-answer"""
        print("\nTest 2: Basic Question-Answer")
        print("-" * 80)

        test_questions = [
            {
                "query": "What is embodied intelligence?",
                "expected_chapter": "Chapter 1",
                "min_score": 0.5
            },
            {
                "query": "How does ROS 2 work?",
                "expected_chapter": "Chapter 3",
                "min_score": 0.6
            },
            {
                "query": "What is inverse kinematics?",
                "expected_chapter": "Chapter 2",
                "min_score": 0.5
            }
        ]

        for test in test_questions:
            try:
                start_time = time.time()

                response = self.session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": test["query"],
                        "chapter_filter": None,
                        "use_history": True
                    },
                    timeout=TEST_TIMEOUT
                )

                duration = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()

                    # Validate response structure
                    has_response = bool(data.get("response"))
                    has_sources = len(data.get("sources", [])) > 0
                    in_scope = data.get("in_scope", False)

                    # Check if expected chapter is in sources
                    chapters = [s.get("chapter") for s in data.get("sources", [])]
                    has_expected_chapter = test["expected_chapter"] in chapters

                    # Check relevance scores
                    scores = [s.get("score", 0) for s in data.get("sources", [])]
                    max_score = max(scores) if scores else 0

                    if has_response and has_sources and in_scope and max_score >= test["min_score"]:
                        self.log_test(
                            f"Basic Q&A: {test['query'][:40]}...",
                            True,
                            f"Found {len(data['sources'])} sources, max score: {max_score:.2f}, expected chapter: {has_expected_chapter}",
                            duration
                        )
                    else:
                        issues = []
                        if not has_response:
                            issues.append("No response text")
                        if not has_sources:
                            issues.append("No sources")
                        if not in_scope:
                            issues.append("Marked out-of-scope")
                        if max_score < test["min_score"]:
                            issues.append(f"Low score ({max_score:.2f})")

                        self.log_test(
                            f"Basic Q&A: {test['query'][:40]}...",
                            False,
                            f"Issues: {', '.join(issues)}",
                            duration
                        )
                else:
                    self.log_test(
                        f"Basic Q&A: {test['query'][:40]}...",
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )

            except Exception as e:
                self.log_test(
                    f"Basic Q&A: {test['query'][:40]}...",
                    False,
                    f"Error: {e}"
                )

    def test_chapter_filtering(self):
        """Test 3: Chapter-filtered queries"""
        print("\nTest 3: Chapter Filtering")
        print("-" * 80)

        test_cases = [
            {
                "query": "What is ROS 2?",
                "chapter": "Chapter 3",
                "min_results": 1
            },
            {
                "query": "Explain embodied intelligence",
                "chapter": "Chapter 1",
                "min_results": 1
            }
        ]

        for test in test_cases:
            try:
                start_time = time.time()

                response = self.session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": test["query"],
                        "chapter_filter": test["chapter"],
                        "use_history": True
                    },
                    timeout=TEST_TIMEOUT
                )

                duration = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    sources = data.get("sources", [])

                    # Verify all sources are from the filtered chapter
                    all_from_chapter = all(
                        s.get("chapter") == test["chapter"] for s in sources
                    )

                    has_min_results = len(sources) >= test["min_results"]

                    if all_from_chapter and has_min_results:
                        self.log_test(
                            f"Chapter filter: {test['chapter']}",
                            True,
                            f"All {len(sources)} sources from {test['chapter']}",
                            duration
                        )
                    else:
                        issues = []
                        if not all_from_chapter:
                            chapters = [s.get("chapter") for s in sources]
                            issues.append(f"Mixed chapters: {set(chapters)}")
                        if not has_min_results:
                            issues.append(f"Only {len(sources)} results")

                        self.log_test(
                            f"Chapter filter: {test['chapter']}",
                            False,
                            f"Issues: {', '.join(issues)}",
                            duration
                        )
                else:
                    self.log_test(
                        f"Chapter filter: {test['chapter']}",
                        False,
                        f"HTTP {response.status_code}"
                    )

            except Exception as e:
                self.log_test(
                    f"Chapter filter: {test['chapter']}",
                    False,
                    f"Error: {e}"
                )

    def test_out_of_scope(self):
        """Test 4: Out-of-scope detection"""
        print("\nTest 4: Out-of-Scope Detection")
        print("-" * 80)

        out_of_scope_questions = [
            "What is quantum computing?",
            "How do I cook pasta?",
            "Explain general relativity"
        ]

        for query in out_of_scope_questions:
            try:
                start_time = time.time()

                response = self.session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": query,
                        "chapter_filter": None,
                        "use_history": True
                    },
                    timeout=TEST_TIMEOUT
                )

                duration = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    in_scope = data.get("in_scope", True)
                    has_response = bool(data.get("response"))
                    sources_count = len(data.get("sources", []))

                    # Out-of-scope should have: in_scope=False, response explaining, no/few sources
                    correctly_detected = (
                        not in_scope and
                        has_response and
                        sources_count == 0
                    )

                    if correctly_detected:
                        self.log_test(
                            f"Out-of-scope: {query[:40]}...",
                            True,
                            "Correctly detected as out-of-scope",
                            duration
                        )
                    else:
                        self.log_test(
                            f"Out-of-scope: {query[:40]}...",
                            False,
                            f"in_scope={in_scope}, sources={sources_count}",
                            duration
                        )
                else:
                    self.log_test(
                        f"Out-of-scope: {query[:40]}...",
                        False,
                        f"HTTP {response.status_code}"
                    )

            except Exception as e:
                self.log_test(
                    f"Out-of-scope: {query[:40]}...",
                    False,
                    f"Error: {e}"
                )

    def test_selected_text_context(self):
        """Test 5: Contextual queries with selected text"""
        print("\nTest 5: Selected Text Context")
        print("-" * 80)

        selected_text = "SLAM (Simultaneous Localization and Mapping) is a technique used by robots to build a map of an unknown environment."

        try:
            start_time = time.time()

            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "Can you explain this in simpler terms?",
                    "selected_text": selected_text,
                    "chapter_filter": None,
                    "use_history": True
                },
                timeout=TEST_TIMEOUT
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                has_response = bool(data.get("response"))
                has_sources = len(data.get("sources", [])) > 0
                in_scope = data.get("in_scope", False)

                if has_response and has_sources and in_scope:
                    self.log_test(
                        "Contextual query with selected text",
                        True,
                        f"Generated contextual response with {len(data['sources'])} sources",
                        duration
                    )
                else:
                    self.log_test(
                        "Contextual query with selected text",
                        False,
                        f"response={has_response}, sources={has_sources}, in_scope={in_scope}"
                    )
            else:
                self.log_test(
                    "Contextual query with selected text",
                    False,
                    f"HTTP {response.status_code}"
                )

        except Exception as e:
            self.log_test(
                "Contextual query with selected text",
                False,
                f"Error: {e}"
            )

    def test_response_time(self):
        """Test 6: Response time performance"""
        print("\nTest 6: Response Time Performance")
        print("-" * 80)

        query = "What is embodied intelligence?"
        num_runs = 5
        response_times = []

        for i in range(num_runs):
            try:
                start_time = time.time()

                response = self.session.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "message": query,
                        "chapter_filter": None,
                        "use_history": True
                    },
                    timeout=TEST_TIMEOUT
                )

                duration = time.time() - start_time

                if response.status_code == 200:
                    response_times.append(duration)

            except Exception as e:
                print(f"     Run {i+1} failed: {e}")

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            # Target: 90th percentile < 3 seconds
            sorted_times = sorted(response_times)
            p90_index = int(0.9 * len(sorted_times))
            p90_time = sorted_times[p90_index] if p90_index < len(sorted_times) else sorted_times[-1]

            meets_target = p90_time < 3.0

            self.log_test(
                "Response time performance",
                meets_target,
                f"Avg: {avg_time:.2f}s, Min: {min_time:.2f}s, Max: {max_time:.2f}s, P90: {p90_time:.2f}s (target: <3s)"
            )
        else:
            self.log_test(
                "Response time performance",
                False,
                "No successful requests"
            )

    def test_error_handling(self):
        """Test 7: Error handling"""
        print("\nTest 7: Error Handling")
        print("-" * 80)

        # Test empty message
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "",
                    "chapter_filter": None,
                    "use_history": True
                },
                timeout=10
            )

            if response.status_code == 400 or response.status_code == 422:
                self.log_test(
                    "Error handling: Empty message",
                    True,
                    f"Correctly rejected with HTTP {response.status_code}"
                )
            else:
                self.log_test(
                    "Error handling: Empty message",
                    False,
                    f"Expected 400/422, got {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error handling: Empty message",
                False,
                f"Error: {e}"
            )

        # Test invalid chapter filter
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={
                    "message": "What is ROS 2?",
                    "chapter_filter": "Chapter 999",  # Invalid chapter
                    "use_history": True
                },
                timeout=TEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                # Should handle gracefully (no results or all chapters)
                self.log_test(
                    "Error handling: Invalid chapter",
                    True,
                    "Handled gracefully (no crash)"
                )
            else:
                self.log_test(
                    "Error handling: Invalid chapter",
                    True if response.status_code == 400 else False,
                    f"HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Error handling: Invalid chapter",
                False,
                f"Error: {e}"
            )

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("CHATBOT API TEST REPORT")
        print("=" * 80)

        print(f"\nTotal tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"Failed: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")

        if self.failed_tests > 0:
            print("\n[FAILED TESTS]")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['name']}: {result['message']}")

        # Calculate average response time
        durations = [r["duration"] for r in self.test_results if r["duration"] > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"\nAverage response time: {avg_duration:.2f}s")

        print("\n" + "=" * 80)

        if self.failed_tests == 0:
            print("STATUS: [OK] ALL TESTS PASSED")
        else:
            print(f"STATUS: [WARNING] {self.failed_tests} TESTS FAILED")

        print("=" * 80)


def main():
    # Check if backend is running
    print("Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"[OK] Backend is running at {BASE_URL}")
        print()
    except Exception as e:
        print(f"[ERROR] Backend not reachable at {BASE_URL}")
        print(f"        Error: {e}")
        print()
        print("Please start the backend server:")
        print("  cd rag-backend")
        print("  uvicorn main:app --reload --port 8000")
        sys.exit(1)

    # Run tests
    tester = ChatbotTester(BASE_URL)

    try:
        tester.test_health_check()
        tester.test_basic_question()
        tester.test_chapter_filtering()
        tester.test_out_of_scope()
        tester.test_selected_text_context()
        tester.test_response_time()
        tester.test_error_handling()

        tester.generate_report()

        # Exit with appropriate code
        sys.exit(0 if tester.failed_tests == 0 else 1)

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
