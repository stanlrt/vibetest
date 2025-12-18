# Agent 3: Test Results Grouping

Agent 3 intelligently groups atomic test tasks from Agent 1 and their execution results from Agent 2 into meaningful, cohesive test reports.

## Purpose

While Agent 1 generates atomic, granular test steps (like "Open new tab", "Click button", "Verify state") and Agent 2 executes them individually, Agent 3 provides a higher-level view by:

1. **Grouping related atomic tasks** into logical test scenarios
2. **Identifying test types** (validation, functional, integration, workflow, setup)
3. **Aggregating results** for better reporting and analysis
4. **Filtering out non-test tasks** (pure navigation, tab management without verification)

## How It Works

**Agent 3 uses an LLM** (via DSPy, similar to Agent 1) to intelligently group and categorize tests:

1. **LLM Analysis**: The LLM receives atomic tasks from Agent 1 and their results from Agent 2
2. **Semantic Grouping**: Understanding context and relationships between tasks
3. **Smart Categorization**: Identifying test types based on intent, not just keywords
4. **Meaningful Naming**: Generating descriptive test names that explain what's being tested

The LLM analyzes:
- **User/Actor context**: Groups tasks by the same user (e.g., \"User 1\", \"User 2\")
- **Functional relationships**: Identifies related steps in a workflow
- **Test patterns**: Recognizes validation, integration, and workflow scenarios
- **Semantic meaning**: Understands intent beyond simple keyword matching

**Fallback**: If the LLM fails, Agent 3 automatically falls back to rule-based grouping using heuristics.

## Output Structure

Agent 3 produces a `test_results` object with Pydantic validation:

```python
class TestResults(BaseModel):
    success: bool                           # Overall pass/fail
    duration_seconds: float                 # From Agent 2
    grouped_tests: list[GroupedTest]        # Logical test groups
    original_atomic_tasks: int              # Total from Agent 1
    grouped_tests_count: int                # Number of groups created
    excluded_non_test_tasks: list[int]      # Excluded task numbers
```

Each `GroupedTest` includes:
- **test_name**: Descriptive name (e.g., "Multi-User Join Flow with Validation")
- **test_type**: One of: validation, functional, integration, workflow, setup, navigation
- **atomic_tasks**: List of Agent 1 task numbers included
- **passed**: Overall pass/fail (true only if all atomic tasks passed)
- **summary**: High-level outcome description
- **details**: Dict mapping step names to `TestDetail` objects with observations and advice

## Usage

### Standalone

```python
from agent3 import group_test_results

# After Agent 2 completes
test_results = group_test_results(
    agent1_output=agent1_output,
    agent2_output=agent2_output
)

# Access grouped tests
for test in test_results.grouped_tests:
    print(f"{test.test_name}: {'✓' if test.passed else '✗'}")
    print(f"  Type: {test.test_type}")
    print(f"  Tasks: {test.atomic_tasks}")
```

### In Vibetester Pipeline

Agent 3 is automatically integrated into the vibetester pipeline. Results are saved in the `test_results` key of the output JSON:

```bash
uv run vibetester -uc pitch-humanity-simple.json --logging
```

Output JSON structure:
```json
{
  "summary": {
    "agent3": {
      "grouped_tests": 12,
      "original_atomic_tasks": 31,
      "time_seconds": 0.02
    }
  },
  "agent1_output": { ... },
  "agent2_output": { ... },
  "test_results": {
    "success": true,
    "grouped_tests": [
      {
        "test_name": "Join Game Button - Input Validation",
        "test_type": "validation",
        "atomic_tasks": [1, 2, 3],
        "passed": false,
        "summary": "Test partially passed: 2/3 step(s) succeeded",
        "details": { ... }
      }
    ]
  }
}
```

## Test Type Classification

- **validation**: Input validation, button state checks, error handling
- **functional**: Single feature/flow tests (create game, start game)
- **integration**: Multi-user or cross-component tests (join flow, lobby sync)
- **workflow**: End-to-end sequential processes (pitching phase, voting phase)
- **setup**: Initialization and configuration tasks
- **navigation**: Pure navigation without verification (usually filtered out)

## Installation

Agent 3 is part of the Q-NCLC monorepo:

```bash
uv sync
```
