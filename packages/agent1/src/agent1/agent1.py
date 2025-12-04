from .agent1_prompt import QAArchitect
import dspy
import argparse
import asyncio
import json
import os
from shared.experiment_logger import log_experiment
from .sample_conversation import complex_conversation, complex_conversation_v2, pitch_hum
from dotenv import load_dotenv

# Environment variable is set in the .env file
load_dotenv()


def extract_ux_tasks_dspy(conversation: str, model_name: str, enable_logging: bool = True) -> tuple[dict, dict | None]:
    """
    Extract UX tasks using the DSPy approach.

    Returns:
        Tuple of (result dict, prompt dict or None on error)
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
        lm = dspy.LM(model=dspy_model_name,
                     api_key=os.environ.get("GOOGLE_API_KEY"))
        dspy.settings.configure(lm=lm)

        architect = QAArchitect()

        # Convert conversation to string format expected by DSPy if it's not already
        if not isinstance(conversation, str):
            conversation_str = json.dumps(conversation, indent=2)
        else:
            conversation_str = conversation

        pred = architect(conversation_log=conversation_str)

        # Convert Pydantic model to dict
        result = pred.output.model_dump()

        # Extract the prompt from LM history
        dspy_prompt = None
        if lm.history:
            last_call = lm.history[-1]
            # Extract relevant prompt information
            dspy_prompt = {
                "messages": last_call.get("messages", []),
                "model": last_call.get("model", dspy_model_name),
            }

        if enable_logging:
            log_experiment(
                data={
                    "agent": "agent1_dspy",
                    "model": model_name,
                    "input": conversation,
                    "output": result,
                    "dspy_prompt": dspy_prompt
                },
                filename_prefix="agent1_dspy"
            )

        return result, dspy_prompt
    except Exception as e:
        return {"error": f"DSPy extraction failed: {str(e)}"}, None


async def extract_ux_tasks(conversation: str, model_name: str, enable_logging: bool = True) -> tuple[dict, dict | None]:
    """
    Extract UX tasks from a conversation using DSPy.

    Args:
        conversation: JSON string of the conversation
        model_name: LLM model to use
        enable_logging: Whether to log results

    Returns:
        Tuple of (Dict containing extracted UX tasks, DSPy prompt dict or None)
    """
    return extract_ux_tasks_dspy(conversation, model_name, enable_logging)


def is_logging_enabled(cli_flag: bool) -> bool:
    """Check if logging is enabled via CLI flag or LOGGING env var."""
    if cli_flag:
        return True
    env_val = os.environ.get("LOGGING", "").lower()
    return env_val in ("true", "1", "yes")


async def main():
    parser = argparse.ArgumentParser(
        description="Run Agent 1 with a specific model.")

    parser.add_argument("--model", type=str, default="models/gemini-2.5-flash",
                        help="The model to use (e.g., models/gemini-2.5-flash or gpt-4o).")
    parser.add_argument(
        "--input", type=str, help="Path to input conversation file (.json, .txt, .md)")

    parser.add_argument("--logging", action="store_true",
                        help="Enable logging to ./data/results/ (also enabled by LOGGING=true env var)")

    args = parser.parse_args()

    enable_logging = is_logging_enabled(args.logging)

    # sample conversation to test the agent 1 UX task extraction.

    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                content = f.read()

            if args.input.endswith('.json'):
                # Validate JSON if it's a JSON file
                try:
                    json_content = json.loads(content)
                    sample_conversation = json.dumps(json_content)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON in {args.input}")
                    return
            else:
                # For txt/md, pass as is
                sample_conversation = content
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}")
            return
    else:
        # change this to complex_conversation to test the agent 1 UX task extraction.
        sample_conversation = json.dumps(pitch_hum)

    print("Input Conversation:")
    print(sample_conversation)

    print(f"Using model: {args.model}")
    print(f"Logging: {'enabled' if enable_logging else 'disabled'}")

    ux_tasks, dspy_prompt = await extract_ux_tasks(
        sample_conversation,
        args.model,
        enable_logging=enable_logging
    )

    print("Extracted UX Tasks:")
    print(json.dumps(ux_tasks, indent=2))

    if dspy_prompt:
        print("\nDSPy Prompt:")
        print(json.dumps(dspy_prompt, indent=2))


def run():
    """Entry point for the agent1 CLI command."""
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


if __name__ == "__main__":
    run()
