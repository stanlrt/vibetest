from .tools import register_tools
import asyncio
import time
from browser_use import Agent, Browser, Tools
from browser_use import ActionResult, Browser
from browser_use.llm import ChatBrowserUse, ChatGoogle

from .agent_prompt import AGENT_PROMPT


tools = Tools()

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


async def run_browser_test(tasks: str, headless: bool = False) -> dict:
    """
    Run browser tests with the given task list.
    
    This function can be called programmatically from other packages (e.g., vibetester).
    
    Args:
        tasks: JSON string of tasks to execute
        headless: Whether to run browser in headless mode
        
    Returns:
        Dict with test results including success status, duration, and history
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
    )

    start_time = time.time()
    history = await agent.run()
    duration = time.time() - start_time
    
    await browser.kill()

    return {
        "success": True,
        "duration_seconds": round(duration, 2),
        "history": str(history) if history else None
    }


async def main():
    """
    This function initializes and runs a browser-use agent with default task.
    For programmatic usage, use run_browser_test() instead.
    """
    browser = Browser(headless=False,
                      keep_alive=True,
                      minimum_wait_page_load_time=0.2,
                      wait_between_actions=0.2,)
    await browser.start()

    agent = Agent(
        task=DEFAULT_TASK,
        llm=ChatBrowserUse(temperature=0.0),
        browser_session=browser,
        tools=tools,
        flash_mode=True,
        extend_system_message=AGENT_PROMPT,
    )

    total_start_time = time.time()
    await agent.run()

    total_duration = time.time() - total_start_time
    await browser.kill()

    print("\n--- Timing Report ---")
    print(f"Total time: {total_duration:.2f} seconds")


def run():
    """Entry point for the agent2 CLI command."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
