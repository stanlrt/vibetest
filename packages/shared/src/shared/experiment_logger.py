import json
import os
import datetime
from pathlib import Path


def log_experiment(
    input_data: str,
    output_data: dict,
    model_name: str,
    prompt: str,
    system_instruction: str = ""
):
    """
    Logs the experiment details to a JSON file if logging is enabled.
    """
    if os.environ.get("AGENT_1_ENABLE_EXPERIMENT_LOGGING", "false").lower() != "true":
        return

    experiments_dir = Path("experiments")
    experiments_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{model_name.replace('/', '_')}.json"
    filepath = experiments_dir / filename

    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "model": model_name,
        "input": input_data,
        "prompt": prompt,
        "system_instruction": system_instruction,
        "output": output_data
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        print(f"Experiment logged to: {filepath}")
    except Exception as e:
        print(f"Failed to log experiment: {e}")
