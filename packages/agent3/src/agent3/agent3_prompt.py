"""DSPy prompt and signature for Agent 3 test grouping."""

import dspy
from pydantic import BaseModel, Field
from typing import List
from .models import GroupedTest, TestResults, TestType


class TestGroupingSignature(dspy.Signature):
    """
    Analyze atomic test tasks and their execution results to group them into meaningful test scenarios.

    CRITICAL TASKS:
    1. GROUP RELATED TESTS: Combine atomic tasks that test the same SPECIFIC feature or capability
       - Keep groups focused and granular - prefer multiple small test groups over one broad group
       - Example: "Open tab", "Navigate URL", "Verify button disabled" → Group as ONE focused test
       - Example: "Type invalid code", "Verify disabled" → Separate from "Type valid code", "Verify enabled"
       - DON'T combine unrelated features just because they're sequential

    2. IDENTIFY TEST TYPES:
       - validation: Input validation, button states, error handling
       - functional: Single feature tests (create game, join game)
       - integration: Multi-user or cross-component tests
       - workflow: End-to-end sequential processes (pitching, voting phases)
       - setup: Pure navigation/initialization (usually filter these out)

    3. CREATE STANDARDIZED NAMES AND DESCRIPTIONS:
       NAMING CONVENTION (STRICT):
       - Start with: "The system must", "The user must", "The application must", or "The [role] must"
       - Be SPECIFIC about what's being tested
       - Keep it concise (under 100 characters)

       Examples:
       ✅ GOOD: "The system must disable the Join button until a valid 4-digit code is entered"
       ✅ GOOD: "The user must be able to create a game and receive a unique room code"
       ✅ GOOD: "The host must be able to start the game when minimum players are present"
       ❌ BAD: "Join Game Flow" (too vague, doesn't start with convention)
       ❌ BAD: "Multi-User Pitching Workflow" (too broad, doesn't start with convention)
       ❌ BAD: "Button Validation" (too generic, doesn't start with convention)

       DESCRIPTION RULES:
       - Explain the SPECIFIC requirement being validated
       - State WHY this test matters (user impact, system behavior)
       - Keep focused on the grouped tasks only
       - 2-3 sentences maximum

    4. FILTER NON-TESTS: Exclude pure navigation tasks (only "Open tab", "Switch tab", "Navigate URL" without verification)

    5. KEEP GROUPS GRANULAR: 
       - Prefer 2-5 atomic tasks per group
       - If a group has >6 tasks, consider if it should be split
       - Each group should test ONE specific capability or requirement

    6. AGGREGATE RESULTS: Overall pass = all atomic tasks passed, otherwise fail

    7. PROVIDE CONTEXT: In details, explain what each atomic step verified
    """

    agent1_tasks: str = dspy.InputField(
        desc="JSON array of UX tasks from Agent 1 with number, requirement, steps, acceptance_criteria"
    )

    agent2_results: str = dspy.InputField(
        desc="JSON array of task results from Agent 2 with number, requirement, passed, observations, advice"
    )

    output: TestResults = dspy.OutputField(
        desc="Grouped test results with meaningful test scenarios"
    )


class TestGrouper(dspy.Module):
    """DSPy module for grouping test results."""

    def __init__(self):
        super().__init__()
        self.generate_groups = dspy.Predict(TestGroupingSignature)

    def forward(self, agent1_tasks: str, agent2_results: str) -> dspy.Prediction:
        """
        Group atomic test tasks into meaningful scenarios.

        Args:
            agent1_tasks: JSON string of Agent 1 UX tasks
            agent2_results: JSON string of Agent 2 task results

        Returns:
            dspy.Prediction with TestResults output
        """
        return self.generate_groups(
            agent1_tasks=agent1_tasks,
            agent2_results=agent2_results
        )


if __name__ == "__main__":
    """Test the prompt structure."""
    import json

    # Sample data for testing
    sample_tasks = [
        {
            "number": 1,
            "requirement": "User 1 must verify Join button is disabled",
            "steps": ["Navigate to URL", "Verify 'Join' button is disabled"],
            "acceptance_criteria": "Button is disabled"
        },
        {
            "number": 2,
            "requirement": "User 1 must enter invalid 3-digit code",
            "steps": ["Type '123' into code field", "Verify 'Join' button is disabled"],
            "acceptance_criteria": "Button remains disabled"
        }
    ]

    sample_results = [
        {
            "number": 1,
            "requirement": "User 1 must verify Join button is disabled",
            "passed": True,
            "observations": "Button correctly disabled",
            "advice": None
        },
        {
            "number": 2,
            "requirement": "User 1 must enter invalid 3-digit code",
            "passed": True,
            "observations": "Button remains disabled with invalid input",
            "advice": None
        }
    ]

    print("Agent 3 DSPy Prompt Structure:")
    print("=" * 60)
    print("\nSample Input:")
    print(f"Tasks: {json.dumps(sample_tasks, indent=2)}")
    print(f"Results: {json.dumps(sample_results, indent=2)}")
    print("\nExpected Output: TestResults with grouped tests")
