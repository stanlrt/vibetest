import argparse
import asyncio
import json
import os
from pathlib import Path
from .orchestrator import run_pipeline

# Default directories for transcripts and results
DEFAULT_TRANSCRIPTS_DIR = "./data/transcripts"
DEFAULT_RESULTS_DIR = "./data/results"


def parse_args():
    parser = argparse.ArgumentParser(
        prog="vibetester",
        description="End-to-end UX testing: extract requirements from chat transcripts and test them in browser"
    )
    parser.add_argument(
        "--transcript", "-t",
        required=True,
        help=f"Transcript filename (looked up in {DEFAULT_TRANSCRIPTS_DIR}/) or full path with --full-paths"
    )
    parser.add_argument(
        "--url", "-u",
        required=True,
        help="Web app URL to test"
    )
    parser.add_argument(
        "--model", "-m",
        default="models/gemini-2.0-flash",
        help="LLM model for UX extraction (default: models/gemini-2.0-flash)"
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


def resolve_transcript_path(transcript_arg: str, use_full_path: bool) -> Path:
    """
    Resolve transcript argument to a full path.
    
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
    
    # Look in default transcripts directory
    return Path(DEFAULT_TRANSCRIPTS_DIR) / transcript_arg


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
        raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
    
    content = transcript_path.read_text(encoding="utf-8")
    
    # Validate JSON structure
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in transcript file: {e}")
    
    # Validate it's an array
    if not isinstance(data, list):
        raise ValueError("Transcript must be a JSON array of messages")
    
    # Validate message structure
    for i, msg in enumerate(data):
        if not isinstance(msg, dict):
            raise ValueError(f"Message {i} must be an object, got {type(msg).__name__}")
        if "role" not in msg:
            raise ValueError(f"Message {i} missing 'role' field")
        if "content" not in msg:
            raise ValueError(f"Message {i} missing 'content' field")
    
    return content


async def main():
    args = parse_args()
    
    # Resolve paths
    transcript_path = resolve_transcript_path(args.transcript, args.full_paths)
    output_dir = resolve_output_path(args.output, args.full_paths)
    enable_logging = is_logging_enabled(args.logging)
    
    # Load and validate transcript
    try:
        transcript = load_transcript(transcript_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error loading transcript: {e}")
        return 1
    
    print("🚀 Starting vibetester")
    print(f"   Transcript: {transcript_path}")
    print(f"   URL: {args.url}")
    print(f"   Model: {args.model}")
    print(f"   Headless: {args.headless}")
    print(f"   Logging: {enable_logging}")
    print(f"   Output: {output_dir}")
    
    try:
        result = await run_pipeline(
            transcript=transcript,
            url=args.url,
            model_name=args.model,
            headless=args.headless,
            output_dir=output_dir,
            enable_logging=enable_logging,
            transcript_name=transcript_path.stem  # Pass transcript name without extension
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
