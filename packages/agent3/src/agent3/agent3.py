"""Agent 3: Groups atomic test tasks into meaningful test results using LLM."""

import dspy
import json
import os
from typing import Any
from dotenv import load_dotenv
from .models import TestResults
from .agent3_prompt import TestGrouper

# Load environment variables
load_dotenv()


def group_test_results(
    agent1_output: dict[str, Any],
    agent2_output: dict[str, Any],
    model_name: str = "models/gemini-2.5-flash",
    disable_cache: bool = False
) -> TestResults:
    """
    Group atomic test tasks into meaningful test results using LLM.

    Args:
        agent1_output: Output from Agent 1 containing ux_tasks
        agent2_output: Output from Agent 2 containing task_results
        model_name: LLM model to use for grouping
        disable_cache: Whether to disable DSPy caching

    Returns:
        TestResults model with grouped tests
    """
    # Configure DSPy LM
    dspy_model_name = model_name
    if model_name.startswith("models/"):
        short_name = model_name.replace("models/", "")
        if "gemini" in short_name:
            dspy_model_name = f"gemini/{short_name}"
    elif "gemini" in model_name and not model_name.startswith("gemini/"):
        dspy_model_name = f"gemini/{model_name}"

    try:
        lm = dspy.LM(
            model=dspy_model_name,
            api_key=os.environ.get("GOOGLE_API_KEY"),
            cache=not disable_cache
        )
        dspy.settings.configure(lm=lm)

        # Prepare data for LLM
        ux_tasks = agent1_output.get("ux_tasks", [])
        task_results_obj = agent2_output.get("task_results", {})
        task_results = task_results_obj.get("task_results", [])

        # Convert to JSON strings for the LLM
        tasks_json = json.dumps(ux_tasks, indent=2)
        results_json = json.dumps(task_results, indent=2)

        # Call LLM to group tests
        grouper = TestGrouper()
        prediction = grouper(
            agent1_tasks=tasks_json,
            agent2_results=results_json
        )

        # The output is already a TestResults Pydantic model
        test_results = prediction.output

        return test_results

    except Exception as e:
        # No fallback - raise the error
        raise RuntimeError(f"Agent 3 LLM grouping failed: {str(e)}") from e
