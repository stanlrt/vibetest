from .tools import register_tools
import asyncio
import time
from browser_use import Agent, Browser, Tools
from browser_use import ActionResult, Browser
from browser_use.llm import ChatBrowserUse, ChatGoogle

from .agent_prompt import AGENT_PROMPT


tools = Tools()

register_tools(tools)


async def main():
    """
    This function initializes and runs a browser-use agent
    """

    task = """
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

    browser = Browser(headless=False,
                      keep_alive=True,
                      minimum_wait_page_load_time=0.2,
                      wait_between_actions=0.2,)
    await browser.start()

    agent = Agent(
        task=task,
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


if __name__ == "__main__":
    asyncio.run(main())
