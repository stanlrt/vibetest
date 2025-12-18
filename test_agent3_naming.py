"""Quick test of Agent 3 with standardized naming."""

from agent3 import group_test_results

agent1_output = {
    "ux_tasks": [
        {
            "number": 1,
            "requirement": "User must verify Join button is disabled initially",
            "steps": ["Navigate to URL", "Verify Join button is disabled"],
            "acceptance_criteria": "Button is disabled"
        },
        {
            "number": 2,
            "requirement": "User must enter invalid 3-digit code",
            "steps": ["Type '123'", "Verify Join button remains disabled"],
            "acceptance_criteria": "Button remains disabled"
        },
        {
            "number": 3,
            "requirement": "User must create a new game",
            "steps": ["Click 'Create Game'", "Verify room code appears"],
            "acceptance_criteria": "Game created with room code"
        }
    ]
}

agent2_output = {
    "duration_seconds": 2.5,
    "task_results": {
        "task_results": [
            {
                "number": 1,
                "requirement": "User must verify Join button is disabled initially",
                "passed": True,
                "observations": "Button correctly disabled on page load",
                "advice": None
            },
            {
                "number": 2,
                "requirement": "User must enter invalid 3-digit code",
                "passed": True,
                "observations": "Button remains disabled with invalid input",
                "advice": None
            },
            {
                "number": 3,
                "requirement": "User must create a new game",
                "passed": True,
                "observations": "Game created successfully",
                "advice": None
            }
        ]
    }
}

print("Testing Agent 3 with standardized naming conventions...")
print()

result = group_test_results(agent1_output, agent2_output)

print(f"Groups created: {result.grouped_tests_count}")
print()

for i, test in enumerate(result.grouped_tests, 1):
    print(f"{i}. Test Name: {test.test_name}")
    print(f"   Description: {test.description[:150]}...")
    print(f"   Test details: {len(test.details)} steps")
    print(f"   Passed: {test.passed}")
    print()
