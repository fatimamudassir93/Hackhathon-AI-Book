"""
End-to-End Chatbot Integration Test
Tests the complete chatbot flow from API to user experience
"""
import requests
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

# Test configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

@dataclass
class TestResult:
    test_name: str
    passed: bool
    duration: float
    details: str
    expected: Optional[str] = None
    actual: Optional[str] = None

class ChatbotE2ETester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()

    def log_result(self, test_name: str, passed: bool, duration: float, details: str,
                   expected: Optional[str] = None, actual: Optional[str] = None):
        """Log test result"""
        self.results.append(TestResult(
            test_name=test_name,
            passed=passed,
            duration=duration,
            details=details,
            expected=expected,
            actual=actual
        ))

        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
        print(f"      {details}")
        if not passed and expected and actual:
            print(f"      Expected: {expected}")
            print(f"      Actual: {actual}")
        print(f"      Duration: {duration:.2f}s")
        print()

    def test_health_check(self) -> bool:
        """Test 1: Verify backend is healthy"""
        print("\nTest 1: Health Check")
        print("-" * 80)

        start = time.time()
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=5)
            duration = time.time() - start

            if response.status_code == 200:
                data = response.json()
                all_healthy = (
                    data.get("status") == "healthy" and
                    data.get("qdrant_connected") == True and
                    data.get("qdrant_collection_exists") == True and
                    data.get("database_connected") == True
                )

                self.log_result(
                    "Health Check",
                    all_healthy,
                    duration,
                    "All systems operational" if all_healthy else "Some systems not healthy",
                    "All systems healthy",
                    json.dumps(data)
                )
                return all_healthy
            else:
                self.log_result("Health Check", False, duration, f"HTTP {response.status_code}")
                return False

        except Exception as e:
            self.log_result("Health Check", False, time.time() - start, f"Error: {str(e)}")
            return False

    def test_basic_chat(self) -> bool:
        """Test 2: Basic chat functionality"""
        print("\nTest 2: Basic Chat Functionality")
        print("-" * 80)

        test_cases = [
            {
                "query": "What is embodied intelligence?",
                "expected_in_sources": ["embodied", "intelligence"],
                "min_sources": 1,
                "should_be_in_scope": True
            },
            {
                "query": "Explain ROS 2 architecture",
                "expected_in_sources": ["ROS", "ros"],
                "min_sources": 1,
                "should_be_in_scope": True
            },
            {
                "query": "What is inverse kinematics?",
                "expected_in_sources": ["kinematics", "inverse"],
                "min_sources": 1,
                "should_be_in_scope": True
            }
        ]

        all_passed = True

        for i, test in enumerate(test_cases, 1):
            print(f"  Test Case {i}: {test['query']}")
            start = time.time()

            try:
                response = self.session.post(
                    f"{BASE_URL}/api/chat",
                    json={
                        "message": test["query"],
                        "chapter_filter": None,
                        "use_history": False
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start

                if response.status_code == 200:
                    data = response.json()

                    # Check response exists
                    has_response = bool(data.get("response"))

                    # Check sources
                    sources = data.get("sources", [])
                    has_enough_sources = len(sources) >= test["min_sources"]

                    # Check in_scope
                    is_in_scope = data.get("in_scope", False)
                    scope_matches = is_in_scope == test["should_be_in_scope"]

                    # Check if expected terms in sources
                    sources_text = " ".join([s.get("text", "") for s in sources]).lower()
                    has_expected_terms = any(
                        term.lower() in sources_text
                        for term in test["expected_in_sources"]
                    )

                    passed = (
                        has_response and
                        has_enough_sources and
                        scope_matches and
                        has_expected_terms
                    )

                    details = (
                        f"Response: {len(data.get('response', ''))} chars, "
                        f"Sources: {len(sources)}, "
                        f"In-scope: {is_in_scope}, "
                        f"Has expected terms: {has_expected_terms}"
                    )

                    self.log_result(
                        f"Basic Chat {i}: {test['query'][:40]}...",
                        passed,
                        duration,
                        details
                    )

                    if not passed:
                        all_passed = False

                else:
                    self.log_result(
                        f"Basic Chat {i}",
                        False,
                        duration,
                        f"HTTP {response.status_code}"
                    )
                    all_passed = False

            except Exception as e:
                self.log_result(
                    f"Basic Chat {i}",
                    False,
                    time.time() - start,
                    f"Error: {str(e)}"
                )
                all_passed = False

        return all_passed

    def test_chapter_filtering(self) -> bool:
        """Test 3: Chapter filtering functionality"""
        print("\nTest 3: Chapter Filtering")
        print("-" * 80)

        test_cases = [
            {
                "query": "What is ROS 2?",
                "chapter": "Chapter 3",
                "expected_chapter": "Chapter 3"
            },
            {
                "query": "What is embodied intelligence?",
                "chapter": "Chapter 1",
                "expected_chapter": "Chapter 1"
            }
        ]

        all_passed = True

        for i, test in enumerate(test_cases, 1):
            print(f"  Test Case {i}: Filter by {test['chapter']}")
            start = time.time()

            try:
                response = self.session.post(
                    f"{BASE_URL}/api/chat",
                    json={
                        "message": test["query"],
                        "chapter_filter": test["chapter"],
                        "use_history": False
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start

                if response.status_code == 200:
                    data = response.json()
                    sources = data.get("sources", [])

                    # Check all sources are from the filtered chapter
                    all_from_chapter = all(
                        s.get("chapter") == test["expected_chapter"]
                        for s in sources
                    )

                    has_sources = len(sources) > 0

                    passed = all_from_chapter and has_sources

                    details = (
                        f"Sources: {len(sources)}, "
                        f"All from {test['expected_chapter']}: {all_from_chapter}"
                    )

                    self.log_result(
                        f"Chapter Filter {i}: {test['chapter']}",
                        passed,
                        duration,
                        details
                    )

                    if not passed:
                        all_passed = False

                else:
                    self.log_result(
                        f"Chapter Filter {i}",
                        False,
                        duration,
                        f"HTTP {response.status_code}"
                    )
                    all_passed = False

            except Exception as e:
                self.log_result(
                    f"Chapter Filter {i}",
                    False,
                    time.time() - start,
                    f"Error: {str(e)}"
                )
                all_passed = False

        return all_passed

    def test_out_of_scope(self) -> bool:
        """Test 4: Out-of-scope detection"""
        print("\nTest 4: Out-of-Scope Detection")
        print("-" * 80)

        test_cases = [
            "What is quantum computing?",
            "How do I bake a cake?",
            "Explain the theory of relativity"
        ]

        all_passed = True

        for i, query in enumerate(test_cases, 1):
            print(f"  Test Case {i}: {query}")
            start = time.time()

            try:
                response = self.session.post(
                    f"{BASE_URL}/api/chat",
                    json={
                        "message": query,
                        "chapter_filter": None,
                        "use_history": False
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start

                if response.status_code == 200:
                    data = response.json()
                    in_scope = data.get("in_scope", True)

                    # Should be detected as out-of-scope
                    passed = not in_scope

                    details = f"Detected as {'out-of-scope' if not in_scope else 'in-scope'}"

                    self.log_result(
                        f"Out-of-Scope {i}: {query[:40]}...",
                        passed,
                        duration,
                        details,
                        "out-of-scope",
                        "in-scope" if in_scope else "out-of-scope"
                    )

                    if not passed:
                        all_passed = False

                else:
                    self.log_result(
                        f"Out-of-Scope {i}",
                        False,
                        duration,
                        f"HTTP {response.status_code}"
                    )
                    all_passed = False

            except Exception as e:
                self.log_result(
                    f"Out-of-Scope {i}",
                    False,
                    time.time() - start,
                    f"Error: {str(e)}"
                )
                all_passed = False

        return all_passed

    def test_performance(self) -> bool:
        """Test 5: Performance benchmarks"""
        print("\nTest 5: Performance Benchmarks")
        print("-" * 80)

        queries = [
            "What is embodied intelligence?",
            "Explain ROS 2",
            "What is SLAM?",
            "How does inverse kinematics work?",
            "What are humanoid robots?"
        ]

        times = []

        print(f"  Running {len(queries)} queries to measure performance...")

        for query in queries:
            start = time.time()
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/chat",
                    json={
                        "message": query,
                        "chapter_filter": None,
                        "use_history": False
                    },
                    timeout=TIMEOUT
                )
                duration = time.time() - start

                if response.status_code == 200:
                    times.append(duration)

            except Exception:
                pass

            # Small delay to avoid rate limiting
            time.sleep(1)

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            # P90 calculation
            sorted_times = sorted(times)
            p90_index = int(len(sorted_times) * 0.9)
            p90_time = sorted_times[p90_index] if p90_index < len(sorted_times) else max_time

            # Target: <3s for p90
            passed = p90_time < 3.0

            details = (
                f"Avg: {avg_time:.2f}s, "
                f"Min: {min_time:.2f}s, "
                f"Max: {max_time:.2f}s, "
                f"P90: {p90_time:.2f}s (target: <3s)"
            )

            self.log_result(
                "Performance Benchmark",
                passed,
                sum(times),
                details,
                "P90 < 3.0s",
                f"P90 = {p90_time:.2f}s"
            )

            return passed
        else:
            self.log_result(
                "Performance Benchmark",
                False,
                0,
                "No successful queries"
            )
            return False

    def test_response_quality(self) -> bool:
        """Test 6: Response quality checks"""
        print("\nTest 6: Response Quality")
        print("-" * 80)

        query = "What is embodied intelligence?"

        start = time.time()
        try:
            response = self.session.post(
                f"{BASE_URL}/api/chat",
                json={
                    "message": query,
                    "chapter_filter": None,
                    "use_history": False
                },
                timeout=TIMEOUT
            )
            duration = time.time() - start

            if response.status_code == 200:
                data = response.json()

                # Quality checks
                response_text = data.get("response", "")
                sources = data.get("sources", [])

                # Check 1: Response is substantial (>50 chars)
                substantial = len(response_text) > 50

                # Check 2: Has citations
                has_citations = len(sources) > 0

                # Check 3: Sources have required fields
                sources_valid = all(
                    s.get("chapter") and s.get("text") and s.get("score") is not None
                    for s in sources
                )

                # Check 4: Response mentions key terms from query
                response_lower = response_text.lower()
                has_relevance = "embodied" in response_lower or "intelligence" in response_lower

                passed = substantial and has_citations and sources_valid and has_relevance

                details = (
                    f"Length: {len(response_text)} chars, "
                    f"Sources: {len(sources)}, "
                    f"Valid sources: {sources_valid}, "
                    f"Relevant: {has_relevance}"
                )

                self.log_result(
                    "Response Quality",
                    passed,
                    duration,
                    details
                )

                return passed

            else:
                self.log_result(
                    "Response Quality",
                    False,
                    duration,
                    f"HTTP {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_result(
                "Response Quality",
                False,
                time.time() - start,
                f"Error: {str(e)}"
            )
            return False

    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("END-TO-END CHATBOT TEST REPORT")
        print("=" * 80)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ({pass_rate:.1f}%)")
        print(f"Failed: {failed} ({100 - pass_rate:.1f}%)")
        print()

        if failed > 0:
            print("FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.details}")
            print()

        # Calculate average duration
        total_duration = sum(r.duration for r in self.results)
        avg_duration = total_duration / total if total > 0 else 0

        print(f"Total test duration: {total_duration:.2f}s")
        print(f"Average test duration: {avg_duration:.2f}s")
        print()

        # Overall status
        if pass_rate == 100:
            print("STATUS: [PASS] ALL TESTS PASSED")
        elif pass_rate >= 80:
            print("STATUS: [PASS] ACCEPTABLE (>80%)")
        elif pass_rate >= 60:
            print("STATUS: [WARNING] NEEDS ATTENTION (60-80%)")
        else:
            print("STATUS: [FAIL] CRITICAL ISSUES (<60%)")

        print("=" * 80)

        return pass_rate >= 80

    def run_all_tests(self):
        """Run complete E2E test suite"""
        print("=" * 80)
        print("CHATBOT END-TO-END TEST SUITE")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Timeout: {TIMEOUT}s")
        print("=" * 80)

        # Run all tests
        self.test_health_check()
        time.sleep(1)  # Small delay between test groups

        self.test_basic_chat()
        time.sleep(1)

        self.test_chapter_filtering()
        time.sleep(1)

        self.test_out_of_scope()
        time.sleep(1)

        self.test_performance()
        time.sleep(1)

        self.test_response_quality()

        # Generate report
        return self.generate_report()


if __name__ == "__main__":
    tester = ChatbotE2ETester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
