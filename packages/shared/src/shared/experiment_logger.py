import json
import datetime
from pathlib import Path
from typing import Any


# Default output directory for all experiment logs
DEFAULT_OUTPUT_DIR = "./data/results"


def log_experiment(
    data: dict[str, Any],
    output_dir: str = DEFAULT_OUTPUT_DIR,
    filename_prefix: str = "experiment",
    silent: bool = False
) -> Path | None:
    """
    Log experiment data to a JSON file.
    
    This is the central logging function used by all agents and pipelines.
    
    Args:
        data: Dictionary containing experiment data (will be saved as JSON)
        output_dir: Directory to save the log file (default: ./data/results)
        filename_prefix: Prefix for the filename (e.g., 'vibetester', 'agent1', 'agent2')
        silent: If True, don't print the log path
        
    Returns:
        Path to the created log file, or None if logging failed
        
    Examples:
        # Vibetester pipeline
        log_experiment(data=result, filename_prefix="vibetester")
        
        # Agent 1 standalone
        log_experiment(data={"input": conv, "output": tasks}, filename_prefix="agent1")
        
        # Agent 2 standalone  
        log_experiment(data={"tasks": tasks, "results": results}, filename_prefix="agent2")
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename_prefix}.json"
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
