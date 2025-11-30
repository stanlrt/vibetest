import argparse
import asyncio
import json
import os
from .agent1_prompt import AGENT1_PROMPT
from shared.experiment_logger import log_experiment
from .sample_conversation import complex_conversation, complex_conversation_v2, pitch_hum
from shared.llm_providers import get_provider
from dotenv import load_dotenv

# Environment variable is set in the .env file
load_dotenv()


async def extract_ux_tasks(conversation: str, model_name: str, enable_logging: bool = True) -> dict:
    """
    Extract UX tasks from a conversation.
    
    Args:
        conversation: JSON string of the conversation
        model_name: LLM model to use
        enable_logging: Whether to log results (default True for standalone, 
                       set False when called from vibetester which has its own logging)
    
    Returns:
        Dict containing extracted UX tasks
    """

    try:
        provider = get_provider(model_name)
        result = await provider.generate_json(
            prompt=f"Here is the conversation:\n{conversation}",
            system_instruction=AGENT1_PROMPT,
            model_name=model_name
        )

        if enable_logging:
            log_experiment(
                data={
                    "agent": "agent1",
                    "model": model_name,
                    "input": json.loads(conversation),
                    "output": result
                },
                filename_prefix="agent1"
            )

        return result

    except Exception as e:
        # Handle exceptions from providers
        return {"error": f"Failed to process with model {model_name}: {str(e)}", "response": str(e)}


def is_logging_enabled(cli_flag: bool) -> bool:
    """Check if logging is enabled via CLI flag or LOGGING env var."""
    if cli_flag:
        return True
    env_val = os.environ.get("LOGGING", "").lower()
    return env_val in ("true", "1", "yes")


async def main():
    parser = argparse.ArgumentParser(
        description="Run Agent 1 with a specific model.")
    parser.add_argument("--model", type=str, default="models/gemini-2.0-flash",
                        help="The model to use (e.g., models/gemini-2.0-flash or gpt-4o).")
    parser.add_argument("--logging", action="store_true",
                        help="Enable logging to ./data/results/ (also enabled by LOGGING=true env var)")
    args = parser.parse_args()

    enable_logging = is_logging_enabled(args.logging)

    # sample conversation to test the agent 1 UX task extraction.

    # change this to complex_conversation to test the agent 1 UX task extraction.
    sample_conversation = json.dumps(pitch_hum)

    print("Input Conversation:")
    print(sample_conversation)

    print(f"Using model: {args.model}")
    print(f"Logging: {'enabled' if enable_logging else 'disabled'}")
    ux_tasks = await extract_ux_tasks(sample_conversation, args.model, enable_logging=enable_logging)

    print("Extracted UX Tasks:")
    print(json.dumps(ux_tasks, indent=2))


def run():
    """Entry point for the agent1 CLI command."""
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


if __name__ == "__main__":
    run()
