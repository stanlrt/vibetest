import asyncio
import time
from typing import List
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from browser_use import Agent, Browser
from browser_use import ChatGoogle
from browser_use import ChatGroq

SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
- If tools specificly made for your current task exist, use them instead of performing actions manually. 
- DO NOT EVER repeat the same task/step over and over again. 

Your mission:
- You are a UX evaluator. 
- Your job is to test the Google interface and rate its usability at the end. Focus on your tasks and not the content of the page. 
- If you got stuck, report it. 
- After the final task, rate the user experience.
"""


class Task(BaseModel):
    description: str


class Config(BaseSettings):
    model_name: str
    tasks: List[Task]


async def main():
    """
    This function initializes and runs a browser-use agent
    with a Gemini model to perform a simple web task.
    """

    config = Config(
        model_name="gemini-2.5-flash",
        tasks=[
            Task(
                description="Use Google to search for Argentina."
            ),
            Task(
                description="View the news. Do not read them."
            ),
            Task(
                description="Find a way to filter the news to show only the ones from the past hour."
            ),
        ])

    browser = Browser(headless=False,
                      keep_alive=True,
                      minimum_wait_page_load_time=0.1,
                      wait_between_actions=0.1,)
    await browser.start()

    agent = Agent(
        task=config.tasks[0].description,
        llm=ChatGoogle(model=config.model_name, temperature=0.0),
        browser_session=browser,
        flash_mode=True,
        extend_system_message=SPEED_OPTIMIZATION_PROMPT
    )

    total_start_time = time.time()
    task_durations = []

    for i, task in enumerate(config.tasks):
        if i > 0:
            agent.add_new_task(task.description)

        task_start_time = time.time()
        history = await agent.run()
        task_end_time = time.time()
        task_duration = task_end_time - task_start_time
        task_durations.append(task_duration)
        print(f"Task {i+1} completed successfully: {history.is_successful()}")
        print(f"Task {i+1} took {task_duration:.2f} seconds.")
        print(f"Final result of task {i+1}: {history.final_result()}")

    total_duration = time.time() - total_start_time
    await browser.kill()

    print("\n--- Timing Report ---")
    for i, duration in enumerate(task_durations):
        print(f"Task {i+1}: {duration:.2f} seconds")
    print(f"Total time: {total_duration:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
