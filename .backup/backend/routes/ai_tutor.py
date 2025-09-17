"""
AI Tutor API Routes

Handles AI-powered tutoring, hints, explanations, and code review.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_database, DatabaseManager
from ..models import (
    AITutorRequest, AITutorResponse, AIInteraction, Problem,
    CodeExecutionRequest, CodeExecutionResult
)

router = APIRouter()


class AITutorService:
    """AI Tutor service using Gemini API"""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.client = None
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro')
            except ImportError:
                print("Warning: google-generativeai not installed")
                self.client = None

    async def get_hint(self, problem: Problem, user_code: Optional[str] = None) -> str:
        """Generate a helpful hint for a problem"""
        if not self.client:
            return self._get_fallback_hint(problem)

        prompt = f"""
        You are an expert DSA tutor. Provide a helpful hint for this problem without giving away the complete solution.

        Problem: {problem.title}
        Description: {problem.description or "No description provided"}
        Patterns: {", ".join(problem.patterns)}
        Difficulty: {problem.difficulty}

        {f"User's current code attempt:\n```python\n{user_code}\n```" if user_code else ""}

        Provide a single, specific hint that guides the user toward the solution without revealing the complete approach.
        Focus on the key insight or pattern they should consider.
        """

        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating hint: {e}")
            return self._get_fallback_hint(problem)

    async def explain_concept(self, concept: str, problem_context: Optional[Problem] = None) -> str:
        """Explain a DSA concept in detail"""
        if not self.client:
            return self._get_fallback_explanation(concept)

        context = ""
        if problem_context:
            context = f"\nIn the context of the problem '{problem_context.title}' which involves {', '.join(problem_context.patterns)}"

        prompt = f"""
        You are an expert DSA tutor. Explain the concept of "{concept}" in a clear, educational manner.
        {context}

        Your explanation should:
        1. Define the concept clearly
        2. Explain when and why it's used
        3. Provide a simple example
        4. Mention time/space complexity considerations
        5. Give practical tips for implementation

        Keep it concise but comprehensive.
        """

        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error explaining concept: {e}")
            return self._get_fallback_explanation(concept)

    async def review_code(self, code: str, problem: Problem) -> str:
        """Review user's code and provide feedback"""
        if not self.client:
            return self._get_fallback_code_review(code)

        prompt = f"""
        You are an expert code reviewer specializing in DSA problems. Review this Python solution:

        Problem: {problem.title}
        Expected patterns: {", ".join(problem.patterns)}
        Difficulty: {problem.difficulty}

        User's code:
        ```python
        {code}
        ```

        Provide constructive feedback focusing on:
        1. Correctness of the solution
        2. Time and space complexity
        3. Code quality and readability
        4. Potential optimizations
        5. Edge cases that might be missed

        Be encouraging while providing specific, actionable suggestions.
        """

        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error reviewing code: {e}")
            return self._get_fallback_code_review(code)

    def _get_fallback_hint(self, problem: Problem) -> str:
        """Fallback hint when AI is not available"""
        if problem.hints:
            return problem.hints[0]

        pattern_hints = {
            "Two Pointers": "Consider using two pointers - one at the start and one at the end of the array.",
            "Binary Search": "Think about how you can eliminate half of the search space in each iteration.",
            "Sliding Window": "Can you maintain a window and slide it across the data structure?",
            "Dynamic Programming": "Look for overlapping subproblems and optimal substructure.",
            "Graph": "Consider using DFS or BFS to traverse the graph.",
            "Tree": "Think about tree traversal methods - inorder, preorder, or postorder.",
            "Stack": "LIFO structure - what goes in last comes out first.",
            "Queue": "FIFO structure - first in, first out.",
        }

        for pattern in problem.patterns:
            if pattern in pattern_hints:
                return pattern_hints[pattern]

        return "Break down the problem into smaller parts and think about the most efficient approach."

    def _get_fallback_explanation(self, concept: str) -> str:
        """Fallback explanation when AI is not available"""
        explanations = {
            "Two Pointers": "Two pointers technique uses two indices to traverse a data structure, typically from opposite ends or at different speeds.",
            "Binary Search": "Binary search efficiently finds elements in sorted arrays by repeatedly dividing the search space in half.",
            "Dynamic Programming": "DP solves problems by breaking them into overlapping subproblems and storing results to avoid recomputation.",
            "DFS": "Depth-First Search explores graph nodes by going as deep as possible before backtracking.",
            "BFS": "Breadth-First Search explores graph nodes level by level, visiting all neighbors before moving to the next level.",
        }
        return explanations.get(concept, f"I don't have detailed information about {concept} available offline.")

    def _get_fallback_code_review(self, code: str) -> str:
        """Fallback code review when AI is not available"""
        return "Code review functionality requires AI connection. Please check your code for correctness, efficiency, and edge cases."


# Initialize AI tutor service
ai_tutor = AITutorService()


@router.post("/ask", response_model=AITutorResponse)
async def ask_ai_tutor(
    request: AITutorRequest,
    user_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Ask the AI tutor a question"""

    problem = None
    if request.problem_id:
        problem = db.get_problem_by_id(request.problem_id)

    # Generate response based on interaction type
    if request.interaction_type == "hint":
        if not problem:
            raise HTTPException(status_code=400, detail="Problem ID required for hints")
        response_text = await ai_tutor.get_hint(problem, request.code)

    elif request.interaction_type == "explanation":
        response_text = await ai_tutor.explain_concept(request.query, problem)

    elif request.interaction_type == "review":
        if not request.code:
            raise HTTPException(status_code=400, detail="Code required for review")
        if not problem:
            raise HTTPException(status_code=400, detail="Problem ID required for code review")
        response_text = await ai_tutor.review_code(request.code, problem)

    else:  # general
        # For general questions, use the concept explanation
        response_text = await ai_tutor.explain_concept(request.query, problem)

    # Save interaction
    interaction = AIInteraction(
        interaction_id=str(uuid.uuid4()),
        user_id=user_id,
        problem_id=request.problem_id,
        query=request.query,
        response=response_text,
        interaction_type=request.interaction_type,
        timestamp=datetime.utcnow()
    )

    db.save_ai_interaction(interaction)

    # Generate suggestions and follow-up questions
    suggestions = []
    follow_up_questions = []

    if request.interaction_type == "hint" and problem:
        suggestions = [
            "Try implementing the suggested approach",
            "Consider edge cases",
            "Think about time complexity"
        ]
        follow_up_questions = [
            "What's the time complexity of this approach?",
            "How would you handle edge cases?",
            "Can you optimize this further?"
        ]

    return AITutorResponse(
        response=response_text,
        suggestions=suggestions,
        follow_up_questions=follow_up_questions,
        helpful_resources=[]
    )


@router.get("/interactions/{user_id}")
async def get_ai_interactions(
    user_id: str,
    limit: int = 20,
    db: DatabaseManager = Depends(get_database)
):
    """Get recent AI interactions for a user"""
    interactions = db.get_ai_interactions(user_id, limit)
    return interactions


@router.post("/execute", response_model=CodeExecutionResult)
async def execute_code(request: CodeExecutionRequest):
    """Execute Python code and return results"""
    import sys
    import io
    import traceback
    import time

    # Create a string buffer to capture output
    output_buffer = io.StringIO()
    error_buffer = io.StringIO()

    # Redirect stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = output_buffer
    sys.stderr = error_buffer

    start_time = time.time()
    success = True
    error_message = None

    try:
        # Execute the code
        exec(request.code)
    except Exception as e:
        success = False
        error_message = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    finally:
        # Restore stdout and stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    execution_time = time.time() - start_time

    # Get outputs
    output = output_buffer.getvalue()
    error_output = error_buffer.getvalue()

    if error_output and success:
        error_message = error_output

    return CodeExecutionResult(
        success=success,
        output=output if output else None,
        error=error_message,
        execution_time=execution_time
    )


@router.post("/feedback")
async def submit_feedback(
    interaction_id: str,
    helpful: bool,
    user_id: str,
    additional_feedback: Optional[str] = None
):
    """Submit feedback on AI interaction"""
    # In a real application, you'd update the interaction record
    return {
        "message": "Feedback submitted successfully",
        "interaction_id": interaction_id,
        "helpful": helpful
    }