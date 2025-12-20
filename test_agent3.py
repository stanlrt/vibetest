"""Test Agent 3 with sample data."""

from agent3 import group_test_results

# Sample Agent 1 output
agent1_output = {
    "ux_tasks": [
        {
            "number": 1,
            "requirement": "User 1 (Host) must observe the 'Join Game' button in its initial disabled state.",
            "steps": [
                "Open new tab for User 1",
                "Navigate to app URL",
                "Verify 'Join Game' button is disabled"
            ],
            "acceptance_criteria": "The 'Join Game' button is visibly disabled."
        },
        {
            "number": 2,
            "requirement": "User 1 (Host) must attempt to enter an invalid 3-digit room code.",
            "steps": [
                "Locate the 4-digit code input field",
                "Type '123' into the 4-digit code input field",
                "Verify 'Join Game' button is disabled"
            ],
            "acceptance_criteria": "The 'Join Game' button remains disabled."
        },
        {
            "number": 3,
            "requirement": "User 1 (Host) must create a new game.",
            "steps": [
                "Click 'Create Game'",
                "Locate 'Name' input field",
                "Verify 'Start Game' button is disabled"
            ],
            "acceptance_criteria": "Game creation screen appears."
        }
    ]
}

# Sample Agent 2 output
agent2_output = {
    "duration_seconds": 45.2,
    "success": False,
    "task_results": {
        "task_results": [
            {
                "number": 1,
                "requirement": "User 1 (Host) must observe the 'Join Game' button in its initial disabled state.",
                "passed": True,
                "observations": "Button correctly disabled on page load",
                "advice": None
            },
            {
                "number": 2,
                "requirement": "User 1 (Host) must attempt to enter an invalid 3-digit room code.",
                "passed": False,
                "observations": "Input limited to 4 digits, button enabled with 4 digits",
                "advice": "Clarify input constraints or update button enabling logic"
            },
            {
                "number": 3,
                "requirement": "User 1 (Host) must create a new game.",
                "passed": True,
                "observations": "Game creation successful",
                "advice": None
            }
        ]
    }
}

if __name__ == "__main__":
    print("Testing Agent 3 grouping logic...")

    try:
        results = group_test_results(agent1_output, agent2_output)

        print(f"\n✓ Agent 3 completed successfully!")
        print(f"\nResults:")
        print(f"  - Original atomic tasks: {results.original_atomic_tasks}")
        print(f"  - Grouped tests: {results.grouped_tests_count}")
        print(f"  - Overall success: {results.success}")
        print(f"  - Duration: {results.duration_seconds}s")

        print(f"\nGrouped Tests:")
        for i, test in enumerate(results.grouped_tests, 1):
            print(f"\n  {i}. {test.test_name}")
            print(f"     Passed: {test.passed}")
            print(f"     Summary: {test.summary}")

        # Convert to dict to show JSON structure
        print(f"\n\nJSON Structure Preview:")
        import json
        result_dict = results.model_dump()
        print(json.dumps(result_dict, indent=2)[:500] + "...")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
