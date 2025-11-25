import argparse
import asyncio
import json
import os
from .agent1_prompt import AGENT1_PROMPT
from .experiment_logger import log_experiment
from .sample_conversation import complex_conversation
from dotenv import load_dotenv
import google.generativeai as genai

# Environment variable is set in the .env file or in the terminal using "set GOOGLE_API_KEY=your_api_key_here"
load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

async def extract_ux_tasks(conversation: str, model_name: str) -> dict:
    
    #This function takes a conversation and extracts UX tasks from it.
    
    model = genai.GenerativeModel(model_name)

    prompt = f"{AGENT1_PROMPT}\n\nHere is the conversation:\n{conversation}"

    response = await model.generate_content_async(prompt)

    try:
        response_text = response.text
        # Clean issues with responses wrapped in code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        result = json.loads(response_text)
        
        log_experiment(
            input_data=conversation,
            output_data=result,
            model_name=model_name,
            prompt=prompt,
            system_instruction=AGENT1_PROMPT
        )

        return result
        
    except (json.JSONDecodeError, AttributeError) as e:
        # Handle JSON parsing errors or missing text attribute
        return {"error": "Failed to parse LLM response as JSON", "response": response.text if hasattr(response, 'text') else str(response)}

async def main():
    parser = argparse.ArgumentParser(description="Run Agent 1 with a specific model.")
    parser.add_argument("--model", type=str, default="models/gemini-1.5-flash", help="The model to use.")
    args = parser.parse_args()

    #sample conversation to test the agent 1 UX task extraction.
    
    sample_conversation = json.dumps(complex_conversation)

    print("Input Conversation:")
    print(sample_conversation)

    print(f"Using model: {args.model}")
    ux_tasks = await extract_ux_tasks(sample_conversation, args.model)

    print("Extracted UX Tasks:")
    print(json.dumps(ux_tasks))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())