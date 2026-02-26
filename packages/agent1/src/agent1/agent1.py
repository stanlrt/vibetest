import argparse
import asyncio
import json
import os
from pathlib import Path

import dspy
from dotenv import load_dotenv
from shared.experiment_logger import log_experiment

from .agent1_prompt import QAArchitect
from .sample_conversation import pitch_hum

# Environment variable is set in the .env file
load_dotenv()

# Default directories for test cases
DEFAULT_TEST_CASES_DIR = "./data/test-cases"


def extract_ux_tasks_dspy(conversation: str, model_name: str, enable_logging: bool = True, disable_cache: bool = False) -> tuple[dict, dict | None]:
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
                     api_key=os.environ.get("GOOGLE_API_KEY"),
                     cache=not disable_cache)

        # INSTRUCTION 3: Ensure dspy.settings.configure(lm=lm) is called before the architect is invoked
        dspy.settings.configure(lm=lm)

        # INSTRUCTION 2: Refactor to use cached/loaded version
        architect = get_architect()

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


# INSTRUCTION 1: Implement Singleton/Caching Pattern
_CACHED_ARCHITECT = None


def get_architect() -> QAArchitect:
    """
    Returns a cached instance of QAArchitect.
    Loads 'qa_architect_compiled.json' if it exists.
    """
    global _CACHED_ARCHITECT
    if _CACHED_ARCHITECT is None:
        print("Initializing QAArchitect...")
        architect = QAArchitect()

        # INSTRUCTION 5: Robustness - Load if exists, graceful fallback
        compiled_path = os.path.join(os.path.dirname(
            __file__), "qa_architect_compiled.json")
        if os.path.exists(compiled_path):
            try:
                architect.load(compiled_path)
                print(f"✅ Loaded compiled QAArchitect from {compiled_path}")
            except Exception as e:
                print(
                    f"⚠️ Failed to load compiled QAArchitect: {e}. Using fresh instance.")
        else:
            print("ℹ️ No compiled QAArchitect found. Using fresh instance.")

        _CACHED_ARCHITECT = architect

    return _CACHED_ARCHITECT


async def extract_ux_tasks(conversation: str, model_name: str, enable_logging: bool = True, disable_cache: bool = False) -> tuple[dict, dict | None]:
    """
    Extract UX tasks from a conversation using DSPy.

    Args:
        conversation: JSON string of the conversation
        model_name: LLM model to use
        enable_logging: Whether to log results
        disable_cache: Whether to disable DSPy caching

    Returns:
        Tuple of (Dict containing extracted UX tasks, DSPy prompt dict or None)
    """
    return extract_ux_tasks_dspy(conversation, model_name, enable_logging, disable_cache)


def is_logging_enabled(cli_flag: bool) -> bool:
    """Check if logging is enabled via CLI flag or LOGGING env var."""
    if cli_flag:
        return True
    env_val = os.environ.get("LOGGING", "").lower()
    return env_val in ("true", "1", "yes")


def resolve_test_case_path(test_case_arg: str) -> Path:
    """
    Resolve test case argument to a full path.

    Args:
        test_case_arg: Filename or full path

    Returns:
        Resolved Path object
    """
    # Check if it's already a path (contains separator or starts with ./)
    if os.sep in test_case_arg or test_case_arg.startswith("./") or test_case_arg.startswith(".."):
        return Path(test_case_arg)

    # Look in default test cases directory
    return Path(DEFAULT_TEST_CASES_DIR) / test_case_arg


def load_test_case(test_case_path: Path) -> str:
    """
    Load a test case file containing transcript.

    Args:
        test_case_path: Path to JSON test case file

    Returns:
        Transcript string (JSON or raw text)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid JSON or missing required keys
    """
    if not test_case_path.exists():
        raise FileNotFoundError(
            f"Test case file not found: {test_case_path}")

    content = test_case_path.read_text(encoding="utf-8")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in test case file: {e}")

    if not isinstance(data, dict):
        raise ValueError(
            "Test case file must be a JSON object with 'transcript' key")

    if "transcript" not in data:
        raise ValueError("Test case file missing required 'transcript' key")

    transcript = data["transcript"]

    # Transcript can be a list (JSON transcript) or a string (raw text)
    if isinstance(transcript, list):
        return json.dumps(transcript)
    elif isinstance(transcript, str):
        return transcript
    else:
        raise ValueError("'transcript' must be a list or string")


async def main():
    parser = argparse.ArgumentParser(
        description="Run Agent 1 with a specific model.")

    parser.add_argument("--model", type=str, default="models/gemini-3-flash-preview",
                        help="The model to use (e.g., models/gemini-3-flash-preview or gpt-4o).")
    parser.add_argument(
        "--test-case", "-tc",
        help=f"Test case JSON filename containing 'transcript' key (looked up in {DEFAULT_TEST_CASES_DIR}/)")
    parser.add_argument(
        "--input", type=str, help="[Legacy] Path to input conversation file (.json, .txt, .md)")

    parser.add_argument("--logging", action="store_true",
                        help="Enable logging to ./data/results/ (also enabled by LOGGING=true env var)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Disable DSPy caching for fresh LLM responses")

    args = parser.parse_args()

    enable_logging = is_logging_enabled(args.logging)

    # sample conversation to test the agent 1 UX task extraction.

    if args.test_case:
        # New test case mode
        if args.input:
            print("❌ Error: --test-case (-tc) cannot be combined with --input")
            return

        test_case_path = resolve_test_case_path(args.test_case)
        try:
            sample_conversation = load_test_case(test_case_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Error loading test case: {e}")
            return
    elif args.input:
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
        enable_logging=enable_logging,
        disable_cache=args.no_cache
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
