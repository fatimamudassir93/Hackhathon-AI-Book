"""
Out-of-scope detection for chatbot queries
Identifies questions that are outside the textbook content domain
"""
import re
from typing import List, Dict, Any, Optional, Tuple


class ScopeDetector:
    """
    Detects whether a query is within the scope of the textbook.
    """

    def __init__(
        self,
        min_search_score: float = 0.4,
        min_results_threshold: int = 1
    ):
        """
        Initialize the scope detector.

        Args:
            min_search_score: Minimum relevance score to consider in-scope
            min_results_threshold: Minimum number of relevant results needed
        """
        self.min_search_score = min_search_score
        self.min_results_threshold = min_results_threshold

        # Define in-scope keywords (textbook topics)
        self.in_scope_keywords = {
            # Core topics
            'physical ai', 'embodied intelligence', 'humanoid', 'robot', 'robotics',
            'kinematics', 'dynamics', 'control', 'actuator', 'sensor',

            # ROS and frameworks
            'ros', 'ros2', 'nav2', 'moveit', 'gazebo', 'unity',

            # AI/ML topics
            'reinforcement learning', 'neural network', 'machine learning',
            'computer vision', 'slam', 'localization', 'navigation',

            # Hardware/mechanics
            'servo', 'motor', 'joint', 'link', 'dof', 'degrees of freedom',
            'inverse kinematics', 'forward kinematics', 'trajectory',

            # Simulation
            'simulation', 'physics engine', 'urdf', 'sdf',

            # Specific chapters (from textbook)
            'affordance', 'embodiment', 'sensorimotor', 'perception',
            'manipulation', 'grasping', 'locomotion', 'balance'
        }

        # Define out-of-scope patterns
        self.out_of_scope_patterns = [
            # Unrelated domains
            r'\b(weather|stock|news|sports|entertainment|movie|music|recipe|cooking)\b',
            # General knowledge unrelated to robotics
            r'\b(history|geography|politics|celebrity|gossip)\b',
            # Personal questions
            r'\b(personal|my name|your name|who are you|what are you)\b',
            # Off-topic tech
            r'\b(javascript|python|web development|database|sql)\b'
        ]

    def is_in_scope(
        self,
        query: str,
        search_results: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[bool, str, float]:
        """
        Determine if a query is within the textbook's scope.

        Args:
            query: User's question
            search_results: Optional search results from vector search

        Returns:
            Tuple of (is_in_scope, reason, confidence)
        """
        query_lower = query.lower()

        # Check 1: Explicit out-of-scope patterns
        for pattern in self.out_of_scope_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False, "Question appears to be outside the textbook domain", 0.9

        # Check 2: Search results quality
        if search_results is not None:
            in_scope, reason, confidence = self._check_search_results(search_results)
            if not in_scope:
                return False, reason, confidence

        # Check 3: Keyword matching
        keyword_match = self._check_keywords(query_lower)
        if keyword_match['has_match']:
            return True, "Question relates to textbook topics", keyword_match['confidence']

        # Check 4: Question type analysis
        question_type = self._analyze_question_type(query_lower)
        if question_type['is_generic']:
            return False, "Question is too generic or unrelated to textbook", 0.7

        # Default: Rely on search results if available
        if search_results is not None and len(search_results) > 0:
            return True, "Relevant content found in textbook", 0.6

        # No strong signals either way
        return True, "Unable to determine scope definitively", 0.5

    def _check_search_results(
        self,
        results: List[Dict[str, Any]]
    ) -> Tuple[bool, str, float]:
        """
        Check if search results indicate in-scope query.

        Args:
            results: Vector search results

        Returns:
            Tuple of (is_in_scope, reason, confidence)
        """
        if not results:
            return False, "No relevant content found in textbook", 0.8

        # Check highest score
        max_score = max([r.get('score', 0) for r in results])

        if max_score < self.min_search_score:
            return False, f"Low relevance to textbook content (max score: {max_score:.2f})", 0.7

        # Check number of relevant results
        relevant_count = sum(1 for r in results if r.get('score', 0) >= self.min_search_score)

        if relevant_count < self.min_results_threshold:
            return False, "Insufficient relevant content found", 0.6

        return True, "Relevant content found", 0.8

    def _check_keywords(self, query: str) -> Dict[str, Any]:
        """
        Check for in-scope keywords in query.

        Args:
            query: Lowercased query string

        Returns:
            Dictionary with match status and confidence
        """
        matches = []
        for keyword in self.in_scope_keywords:
            if keyword in query:
                matches.append(keyword)

        if matches:
            # Confidence based on number of matches
            confidence = min(0.7 + (len(matches) * 0.1), 0.95)
            return {
                'has_match': True,
                'matches': matches,
                'confidence': confidence
            }

        return {'has_match': False, 'matches': [], 'confidence': 0.3}

    def _analyze_question_type(self, query: str) -> Dict[str, Any]:
        """
        Analyze the type of question.

        Args:
            query: Lowercased query string

        Returns:
            Dictionary with question type analysis
        """
        # Generic greeting patterns
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        if any(greeting in query for greeting in greetings):
            return {'is_generic': True, 'type': 'greeting'}

        # General knowledge patterns
        general_patterns = [
            r'who is \w+',
            r'what is the capital of',
            r'when did \w+ happen',
            r'how do i \w+ (outside robotics context)'
        ]

        for pattern in general_patterns:
            if re.search(pattern, query):
                return {'is_generic': True, 'type': 'general_knowledge'}

        return {'is_generic': False, 'type': 'specific'}

    def get_out_of_scope_message(self, reason: str) -> str:
        """
        Generate a friendly out-of-scope message.

        Args:
            reason: Reason for being out of scope

        Returns:
            User-friendly message
        """
        return f"""I'm specialized in answering questions about Physical AI and Humanoid Robotics based on this textbook.

{reason}

I can help you with topics like:
- Physical AI and embodied intelligence concepts
- Humanoid robotics and control systems
- ROS 2 and robot frameworks
- Kinematics, dynamics, and motion planning
- Robot simulation and Unity integration
- Computer vision and perception for robots
- Reinforcement learning for robotics

Please feel free to ask a question about these topics!"""


def create_scope_detector(
    min_search_score: float = 0.4,
    min_results_threshold: int = 1
) -> ScopeDetector:
    """
    Factory function to create a scope detector.

    Args:
        min_search_score: Minimum relevance score
        min_results_threshold: Minimum number of relevant results

    Returns:
        Configured ScopeDetector instance
    """
    return ScopeDetector(
        min_search_score=min_search_score,
        min_results_threshold=min_results_threshold
    )


# Example usage
if __name__ == "__main__":
    detector = create_scope_detector()

    # Test queries
    test_queries = [
        ("What is embodied intelligence?", None),
        ("How do I cook pasta?", None),
        ("Explain inverse kinematics for humanoid robots", None),
        ("What's the weather today?", None),
        ("How does ROS 2 navigation work?", None),
        ("Who won the Super Bowl?", None)
    ]

    print("Testing Scope Detection:\n" + "=" * 70)

    for query, _ in test_queries:
        # Simulate search results based on keywords
        simulated_results = []
        if any(kw in query.lower() for kw in ['embodied', 'kinematics', 'ros', 'robot', 'navigation']):
            simulated_results = [{'score': 0.75}]

        in_scope, reason, confidence = detector.is_in_scope(query, simulated_results)

        print(f"\nQuery: {query}")
        print(f"In Scope: {in_scope}")
        print(f"Reason: {reason}")
        print(f"Confidence: {confidence:.2f}")

        if not in_scope:
            print(f"\nMessage: {detector.get_out_of_scope_message(reason)[:100]}...")
