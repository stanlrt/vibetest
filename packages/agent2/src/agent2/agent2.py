from .tools import register_tools
import argparse
import asyncio
import json
import os
import time
from browser_use import Agent, Browser, Tools
from browser_use import ActionResult, Browser
from browser_use.llm import ChatBrowserUse

from .agent_prompt import AGENT_PROMPT
from .models import UXTestResults
from shared.experiment_logger import log_experiment


# Exclude write_file to prevent agent from writing to local files
# Results should be returned via structured output instead
tools = Tools(exclude_actions=['write_file'])

register_tools(tools)


# Default task for standalone CLI usage
DEFAULT_TASK = """
[
    {
        "number": 0,
        "requirement": "Navigate to https://zv997r-8000.csb.app/",
    }, 
    {
        "number": 1,
        "requirement": "The user must be able to create a new game.",
        "steps": [
            "Create a new game.",
            "Enter 'Stan' as the player name in the name input field.",
            "Copy or save the generated game code for later use.",
        ],
        "acceptance_criteria": "The user is successfully added to the game lobby and can see other players if any."
    },
    {
        "number": 2,
        "requirement": "The user must be able to join an existing game using a game code.",
        "steps": [
            "Use the PIN input element to enter the game code you saved in the previous task.",
            "Enter 'John' as the player name in the name input field.",
        ],
        "acceptance_criteria": "The user is successfully added to the game lobby and can see other players if any.",
        "new_tab": True,
    },
    {
        "number": 3,
        "requirement": "End of list.",
    }

]
"""


async def run_browser_test(tasks: str, headless: bool = False, enable_logging: bool = False) -> dict:
    """
    Run browser tests with the given task list.
    
    This function can be called programmatically from other packages (e.g., vibetester).
    
    Args:
        tasks: JSON string of tasks to execute
        headless: Whether to run browser in headless mode
        enable_logging: Whether to log results (default False when called from vibetester)
        
    Returns:
        Dict with test results including success status, duration, history, and structured task_results
    """
    browser = Browser(
        headless=headless,
        keep_alive=True,
        minimum_wait_page_load_time=0.2,
        wait_between_actions=0.2,
    )
    await browser.start()

    agent = Agent(
        task=tasks,
        llm=ChatBrowserUse(temperature=0.0),
        browser_session=browser,
        tools=tools,
        flash_mode=True,
        extend_system_message=AGENT_PROMPT,
        output_model_schema=UXTestResults,  # Use structured output for task results
    )

    start_time = time.time()
    history = await agent.run()
    duration = time.time() - start_time
    
    await browser.kill()

    # Extract structured output from history
    task_results = None
    final_result = history.final_result()
    
    if final_result:
        try:
            # Parse the structured output
            parsed = UXTestResults.model_validate_json(final_result)
            task_results = parsed.model_dump()
        except Exception as e:
            # If parsing fails, include the raw result
            task_results = {"parse_error": str(e), "raw_result": final_result}

    result = {
        "success": history.is_successful() if history.is_done() else False,
        "duration_seconds": round(duration, 2),
        "task_results": task_results,  # Structured task results
        "history": str(history) if history else None
    }
    
    if enable_logging:
        log_experiment(
            data={
                "agent": "agent2",
                "input": json.loads(tasks),
                "output": result
            },
            filename_prefix="agent2"
        )
    
    return result


def is_logging_enabled(cli_flag: bool) -> bool:
    """Check if logging is enabled via CLI flag or LOGGING env var."""
    if cli_flag:
        return True
    env_val = os.environ.get("LOGGING", "").lower()
    return env_val in ("true", "1", "yes")


async def main():
    """
    This function initializes and runs a browser-use agent with default task.
    For programmatic usage, use run_browser_test() instead.
    """
    parser = argparse.ArgumentParser(
        description="Run Agent 2 browser tests with default task.")
    parser.add_argument("--headless", action="store_true",
                        help="Run browser in headless mode")
    parser.add_argument("--logging", action="store_true",
                        help="Enable logging to ./data/results/ (also enabled by LOGGING=true env var)")
    args = parser.parse_args()

    enable_logging = is_logging_enabled(args.logging)
    print(f"Logging: {'enabled' if enable_logging else 'disabled'}")

    result = await run_browser_test(
        tasks=DEFAULT_TASK,
        headless=args.headless,
        enable_logging=enable_logging
    )

    print("\n--- Timing Report ---")
    print(f"Total time: {result['duration_seconds']:.2f} seconds")


def run():
    """Entry point for the agent2 CLI command."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
