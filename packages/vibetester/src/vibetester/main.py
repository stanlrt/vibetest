import argparse
import asyncio
import json
import os
from pathlib import Path
from .orchestrator import run_pipeline

# Default directories for test cases and results
DEFAULT_TEST_CASES_DIR = "./data/test-cases"
DEFAULT_RESULTS_DIR = "./data/results"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="vibetester",
        description="End-to-end UX testing: extract requirements from chat transcripts and test them in browser"
    )

    # New unified test case argument
    parser.add_argument(
        "-test-case", "-tc",
        help=f"Test case JSON filename containing 'url' and 'transcript' keys (looked up in {DEFAULT_TEST_CASES_DIR}/)"
    )

    # Legacy arguments for flexible testing
    parser.add_argument(
        "--transcript", "-t",
        help=f"[Legacy] Transcript filename (looked up in {DEFAULT_TEST_CASES_DIR}/) or full path with --full-paths"
    )
    parser.add_argument(
        "--url", "-u",
        help="[Legacy] Web app URL to test"
    )
    parser.add_argument(
        "--model", "-m",
        default="models/gemini-2.5-flash",
        help="LLM model for UX extraction (default: models/gemini-2.5-flash)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help=f"Output filename or directory (default: {DEFAULT_RESULTS_DIR}/)"
    )
    parser.add_argument(
        "--full-paths",
        action="store_true",
        help="Treat --transcript and --output as full paths instead of filenames"
    )
    parser.add_argument(
        "--logging",
        action="store_true",
        help="Enable logging to output directory (also enabled by LOGGING=true env var)"
    )
    return parser.parse_args()


def resolve_test_case_path(test_case_arg: str, use_full_path: bool) -> Path:
    """
    Resolve test case argument to a full path.

    Args:
        test_case_arg: Filename or full path
        use_full_path: If True, treat as full path; otherwise look in default dir

    Returns:
        Resolved Path object
    """
    if use_full_path:
        return Path(test_case_arg)

    # Check if it's already a path (contains separator or starts with ./)
    if os.sep in test_case_arg or test_case_arg.startswith("./") or test_case_arg.startswith(".."):
        return Path(test_case_arg)

    # Look in default test cases directory
    return Path(DEFAULT_TEST_CASES_DIR) / test_case_arg


def resolve_transcript_path(transcript_arg: str, use_full_path: bool) -> Path:
    """
    Resolve transcript argument to a full path (legacy support).

    Args:
        transcript_arg: Filename or full path
        use_full_path: If True, treat as full path; otherwise look in default dir

    Returns:
        Resolved Path object
    """
    if use_full_path:
        return Path(transcript_arg)

    # Check if it's already a path (contains separator or starts with ./)
    if os.sep in transcript_arg or transcript_arg.startswith("./") or transcript_arg.startswith(".."):
        return Path(transcript_arg)

    # Look in default test cases directory
    return Path(DEFAULT_TEST_CASES_DIR) / transcript_arg


def resolve_output_path(output_arg: str | None, use_full_path: bool) -> str:
    """
    Resolve output argument to a full path.

    Args:
        output_arg: Filename, directory, or None for default
        use_full_path: If True, treat as full path; otherwise use default dir

    Returns:
        Resolved path string
    """
    if output_arg is None:
        return DEFAULT_RESULTS_DIR

    if use_full_path:
        return output_arg

    # Check if it's already a path
    if os.sep in output_arg or output_arg.startswith("./") or output_arg.startswith(".."):
        return output_arg

    # Use default results directory
    return DEFAULT_RESULTS_DIR


def is_logging_enabled(cli_flag: bool) -> bool:
    """Check if logging is enabled via CLI flag or LOGGING env var."""
    if cli_flag:
        return True
    env_val = os.environ.get("LOGGING", "").lower()
    return env_val in ("true", "1", "yes")


def load_transcript(transcript_path: Path) -> str:
    """
    Load and validate transcript from file path.

    Args:
        transcript_path: Path to JSON transcript file

    Returns:
        JSON string of the transcript

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid JSON or wrong format
    """
    if not transcript_path.exists():
        raise FileNotFoundError(
            f"Transcript file not found: {transcript_path}")

    content = transcript_path.read_text(encoding="utf-8")

    # Validate JSON structure
    # Try to parse as JSON first
    try:
        data = json.loads(content)

        # If it parses as JSON, validate structure
        if not isinstance(data, list):
            # It's valid JSON but not a list - might be a different format or just text
            # For now, we'll treat it as raw text if it's not the expected list format
            return content

        # Validate message structure for JSON transcripts
        for i, msg in enumerate(data):
            if not isinstance(msg, dict):
                # Valid JSON list but elements aren't objects - treat as raw text
                return content
            if "role" not in msg or "content" not in msg:
                # Valid JSON list of objects but missing fields - treat as raw text
                return content

        # If we get here, it's a valid JSON transcript
        return content

    except json.JSONDecodeError:
        # Not JSON, treat as raw text (Markdown, etc.)
        return content


def load_test_case(test_case_path: Path) -> tuple[str, str, str | None]:
    """
    Load a unified test case file containing URL, transcript, and optional tool.

    Args:
        test_case_path: Path to JSON test case file

    Returns:
        Tuple of (url, transcript_json_string, tool_name or None)

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
            "Test case file must be a JSON object with 'url' and 'transcript' keys")

    if "url" not in data:
        raise ValueError("Test case file missing required 'url' key")

    if "transcript" not in data:
        raise ValueError("Test case file missing required 'transcript' key")

    url = data["url"]
    transcript = data["transcript"]
    tool = data.get("tool")  # Optional field

    # Transcript can be a list (JSON transcript) or a string (raw text)
    if isinstance(transcript, list):
        transcript_str = json.dumps(transcript)
    elif isinstance(transcript, str):
        transcript_str = transcript
    else:
        raise ValueError("'transcript' must be a list or string")

    return url, transcript_str, tool


async def main():
    args = parse_args()

    # Initialize variables
    test_case_path: Path | None = None
    transcript_path: Path | None = None
    tool_name: str | None = None

    # Validate argument combinations
    if args.test_case:
        # New unified mode: -tc provides both URL and transcript
        if args.url or args.transcript:
            print(
                "❌ Error: -test-case (-tc) cannot be combined with --url (-u) or --transcript (-t)")
            return 1

        test_case_path = resolve_test_case_path(
            args.test_case, args.full_paths)
        try:
            url, transcript, tool_name = load_test_case(test_case_path)
            transcript_name = test_case_path.stem
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Error loading test case: {e}")
            return 1
    else:
        # Legacy mode: -u and -t required separately
        if not args.url or not args.transcript:
            print(
                "❌ Error: Either -test-case (-tc) OR both --url (-u) and --transcript (-t) are required")
            return 1

        url = args.url
        transcript_path = resolve_transcript_path(
            args.transcript, args.full_paths)
        transcript_name = transcript_path.stem

        try:
            transcript = load_transcript(transcript_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Error loading transcript: {e}")
            return 1

    # Resolve output path
    output_dir = resolve_output_path(args.output, args.full_paths)
    enable_logging = is_logging_enabled(args.logging)

    # Determine source name for display
    source_path = test_case_path if args.test_case else transcript_path

    print("🚀 Starting vibetester")
    if args.test_case:
        print(f"   Test Case: {source_path}")
    else:
        print(f"   Transcript: {source_path}")
    print(f"   URL: {url}")
    if tool_name:
        print(f"   Tool: {tool_name}")
    print(f"   Model: {args.model}")
    print(f"   Headless: {args.headless}")
    print(f"   Logging: {enable_logging}")
    print(f"   Output: {output_dir}")

    try:
        result = await run_pipeline(
            transcript=transcript,
            url=url,
            model_name=args.model,
            headless=args.headless,
            output_dir=output_dir,
            enable_logging=enable_logging,
            transcript_name=transcript_name,
            tool_name=tool_name
        )

        print("\n✅ Pipeline complete!")
        return 0

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return 1


def run():
    """Entry point for the vibetester CLI command."""
    # Note: Do NOT set WindowsSelectorEventLoopPolicy on Windows
    # browser-use requires ProactorEventLoop (default) for subprocess support
    exit_code = asyncio.run(main())
    exit(exit_code)


if __name__ == "__main__":
    run()
