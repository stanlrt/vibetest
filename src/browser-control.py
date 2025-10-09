import asyncio
import httpx
from typing import List, Optional
from pydantic import BaseModel
import uuid


class Task(BaseModel):
    description: str


async def run_task(client: httpx.AsyncClient, task: Task, session_id: Optional[str]) -> Optional[str]:
    """Sends a single task to the browser-control-api."""
    print(f"Executing task: {task.description}")
    payload = {"command": task.description}
    if session_id:
        payload["session_id"] = session_id

    try:
        response = await client.post("http://127.0.0.1:8000/interact", json=payload, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        print(f"Task response: {result.get('message')}")
        return result.get("session_id")
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
        print("Please ensure the 'browser-control-api' server is running.")
        return session_id
    except httpx.HTTPStatusError as e:
        print(
            f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
        print(f"Response: {e.response.text}")
        return session_id


async def main():
    """
    This function initializes and runs a series of tasks
    using the browser-control-api.
    """
    tasks: List[Task] = [
        Task(description="Use Google to find the GitHub repository for 'shashank-100/browser-control-api'."),
        Task(description="Click on the link to the GitHub repository."),
        Task(description="Find the first code snippet on the page and describe what it does."),
    ]

    session_id = str(uuid.uuid4())
    print(f"Starting new session: {session_id}")

    async with httpx.AsyncClient() as client:
        for task in tasks:
            new_session_id = await run_task(client, task, session_id)
            if new_session_id:
                session_id = new_session_id
            else:
                # If a task fails to return a session_id, we should probably stop.
                break
            await asyncio.sleep(2)  # Give the browser time to react

    print("All tasks have been sent.")


if __name__ == "__main__":
    print("NOTE: This script requires the 'browser-control-api' server to be running separately.")
    print("You can typically start it with a command like 'python api_server.py'.")
    print("-" * 20)
    asyncio.run(main())
