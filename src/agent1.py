import argparse
import asyncio
import json
import os
from .agent1_prompt import AGENT1_PROMPT
from .experiment_logger import log_experiment
from .sample_conversation import complex_conversation, complex_conversation_v2
from .llm_providers import get_provider
from dotenv import load_dotenv

# Environment variable is set in the .env file
load_dotenv()

async def extract_ux_tasks(conversation: str, model_name: str) -> dict:
    
    #This function takes a conversation and extracts UX tasks from it.
    
    try:
        provider = get_provider(model_name)
        result = await provider.generate_json(
            prompt=f"Here is the conversation:\n{conversation}",
            system_instruction=AGENT1_PROMPT,
            model_name=model_name
        )
        
        log_experiment(
            input_data=conversation,
            output_data=result,
            model_name=model_name,
            prompt=f"Here is the conversation:\n{conversation}",
            system_instruction=AGENT1_PROMPT
        )

        return result
        
    except Exception as e:
        # Handle exceptions from providers
        return {"error": f"Failed to process with model {model_name}: {str(e)}", "response": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Run Agent 1 with a specific model.")
    parser.add_argument("--model", type=str, default="models/gemini-2.0-flash", help="The model to use (e.g., models/gemini-2.0-flash or gpt-4o).")
    args = parser.parse_args()

    #sample conversation to test the agent 1 UX task extraction.
    
    sample_conversation = json.dumps(complex_conversation_v2) #change this to complex_conversation to test the agent 1 UX task extraction.

    print("Input Conversation:")
    print(sample_conversation)

    print(f"Using model: {args.model}")
    ux_tasks = await extract_ux_tasks(sample_conversation, args.model)

    print("Extracted UX Tasks:")
    print(json.dumps(ux_tasks, indent=2))

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())