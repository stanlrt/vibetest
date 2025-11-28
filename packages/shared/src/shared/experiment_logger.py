import json
import datetime
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


# Default output directory for all experiment logs
DEFAULT_OUTPUT_DIR = "./data/results"


def _sanitize_for_filename(text: str, max_length: int = 30) -> str:
    """
    Sanitize a string to be safe for use in filenames.
    
    Args:
        text: The string to sanitize
        max_length: Maximum length of the result
        
    Returns:
        A sanitized string safe for filenames
    """
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', text)
    # Replace spaces and other whitespace with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')
    return sanitized or "unknown"


def _extract_url_identifier(url: str) -> str:
    """
    Extract a short identifier from a URL for use in filenames.
    
    Args:
        url: The URL to extract identifier from
        
    Returns:
        A short identifier based on the URL's hostname/subdomain
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path
        # Remove common prefixes and port numbers
        hostname = re.sub(r'^(www\.)?', '', hostname)
        hostname = re.sub(r':\d+$', '', hostname)
        # Get the first part (subdomain or domain)
        parts = hostname.split('.')
        identifier = parts[0] if parts else hostname
        return _sanitize_for_filename(identifier, max_length=20)
    except Exception:
        return "unknown_url"


def log_experiment(
    data: dict[str, Any],
    output_dir: str = DEFAULT_OUTPUT_DIR,
    filename_prefix: str = "experiment",
    transcript_name: str | None = None,
    url: str | None = None,
    silent: bool = False
) -> Path | None:
    """
    Log experiment data to a JSON file.
    
    This is the central logging function used by all agents and pipelines.
    
    Args:
        data: Dictionary containing experiment data (will be saved as JSON)
        output_dir: Directory to save the log file (default: ./data/results)
        filename_prefix: Prefix for the filename (e.g., 'vibetester', 'agent1', 'agent2')
        transcript_name: Optional transcript name to include in filename
        url: Optional URL to include in filename (will be sanitized)
        silent: If True, don't print the log path
        
    Returns:
        Path to the created log file, or None if logging failed
        
    Examples:
        # Vibetester pipeline with transcript and URL
        log_experiment(
            data=result, 
            filename_prefix="vibetester",
            transcript_name="multiplayer_game",
            url="https://example.csb.app/"
        )
        # Output: 20251128_130649_vibetester_multiplayer_game_example.json
        
        # Agent 1 standalone
        log_experiment(data={"input": conv, "output": tasks}, filename_prefix="agent1")
        
        # Agent 2 standalone  
        log_experiment(data={"tasks": tasks, "results": results}, filename_prefix="agent2")
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build filename parts
    filename_parts = [timestamp, filename_prefix]
    
    if transcript_name:
        # Remove .json extension if present and sanitize
        clean_name = transcript_name.replace('.json', '').replace('.JSON', '')
        filename_parts.append(_sanitize_for_filename(clean_name))
    
    if url:
        filename_parts.append(_extract_url_identifier(url))
    
    filename = "_".join(filename_parts) + ".json"
    filepath = output_path / filename
    
    # Add timestamp to data if not present
    if "timestamp" not in data:
        data["timestamp"] = datetime.datetime.now().isoformat()
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        if not silent:
            print(f"📁 Results logged to: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Failed to log experiment: {e}")
        return None
