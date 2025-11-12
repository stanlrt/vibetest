import asyncio
import json
import os
from .agent1_prompt import AGENT1_PROMPT
from dotenv import load_dotenv
import google.generativeai as genai

# Environment variable is set in the .env file or in the terminal using "set GOOGLE_API_KEY=your_api_key_here"
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

async def extract_user_stories(conversation: str) -> dict:
    
    #This function takes a conversation and extracts user stories from it.
    
    model = genai.GenerativeModel('models/gemini-flash-latest')

    prompt = f"{AGENT1_PROMPT}\n\nHere is the conversation:\n{conversation}"

    response = await model.generate_content_async(prompt)

    try:
        response_text = response.text
        # Clean issues with responses wrapped in code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
        
    except (json.JSONDecodeError, AttributeError) as e:
        # Handle JSON parsing errors or missing text attribute
        return {"error": "Failed to parse LLM response as JSON", "response": response.text if hasattr(response, 'text') else str(response)}

async def main():

    #sample conversation to test the agent 1 user story extraction.

    sample_conversation = json.dumps([
        {"role": "user", "content": "Hey, can you help me build a simple to-do list app?"},
        {"role": "developer", "content": "Sure! What features are you thinking of?"},
        {"role": "user", "content": "I want to be able to add tasks to a list."},
        {"role": "developer", "content": "Okay, adding tasks. What else?"},
        {"role": "user", "content": "I also need to be able to delete them once I'm done."},
        {"role": "developer", "content": "Makes sense. Add and delete. Anything else?"},
        {"role": "user", "content": "Maybe mark them as complete?"},
        {"role": "developer", "content": "Got it. So, add, delete, and mark as complete. Let's start with that."},
    ])

    print("Input Conversation:")
    print(sample_conversation)

    user_stories = await extract_user_stories(sample_conversation)

    print("Extracted User Stories:")
    print(json.dumps(user_stories))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())