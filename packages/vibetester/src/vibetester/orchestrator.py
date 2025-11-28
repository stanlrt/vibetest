import json
import time

from agent1.agent1 import extract_ux_tasks
from agent2.agent2 import run_browser_test
from shared.experiment_logger import log_experiment


async def run_pipeline(
    transcript: str,
    url: str,
    model_name: str,
    headless: bool = False,
    output_dir: str = "./data/results",
    enable_logging: bool = False,
    transcript_name: str | None = None
) -> dict:
    """
    Run the full vibetester pipeline.
    
    1. Agent 1: Extract UX requirements from transcript
    2. Agent 2: Run browser tests against the URL
    3. Log results (if enabled)
    
    Args:
        transcript: JSON string of chat transcript
        url: Web app URL to test
        model_name: LLM model for Agent 1
        headless: Whether to run browser in headless mode
        output_dir: Directory to save experiment logs
        enable_logging: Whether to log results (via --logging or LOGGING env var)
        
    Returns:
        Dict containing full pipeline results
    """
    total_start = time.time()
    
    # === Stage 1: Extract UX Tasks ===
    print("\n📋 Stage 1: Extracting UX requirements...")
    stage1_start = time.time()
    
    # Disable Agent 1's own logging - vibetester handles all logging
    ux_tasks = await extract_ux_tasks(transcript, model_name, enable_logging=False)
    
    stage1_duration = time.time() - stage1_start
    
    # Check for errors from Agent 1
    if "error" in ux_tasks:
        print(f"   ❌ Agent 1 failed: {ux_tasks['error']}")
        raise RuntimeError(f"Agent 1 failed: {ux_tasks['error']}")
    
    task_count = len(ux_tasks.get('ux_tasks', []))
    print(f"   ✓ Extracted {task_count} UX tasks ({stage1_duration:.1f}s)")
    
    # === Stage 2: Browser Testing ===
    print("\n🌐 Stage 2: Running browser tests...")
    stage2_start = time.time()
    
    # Prepare task list with URL injection
    browser_tasks = prepare_browser_tasks(ux_tasks, url)
    
    print(f"   Tasks prepared for browser agent:")
    print(f"   {browser_tasks[:200]}..." if len(browser_tasks) > 200 else f"   {browser_tasks}")
    
    test_results = await run_browser_test(
        tasks=browser_tasks,
        headless=headless
    )
    
    stage2_duration = time.time() - stage2_start
    print(f"   ✓ Browser tests complete ({stage2_duration:.1f}s)")
    
    # === Final Logging ===
    total_duration = time.time() - total_start
    
    result = {
        "config": {
            "url": url,
            "model": model_name,
            "headless": headless
        },
        "transcript": json.loads(transcript),
        "agent1_output": ux_tasks,
        "agent2_input": json.loads(browser_tasks),  # The actual tasks sent to Agent 2 (with URL injected)
        "agent2_output": test_results,
        "timing": {
            "stage1_extraction_seconds": round(stage1_duration, 2),
            "stage2_browser_seconds": round(stage2_duration, 2),
            "total_seconds": round(total_duration, 2)
        }
    }
    
    # Use shared logging function (only if enabled)
    if enable_logging:
        log_experiment(
            data=result,
            output_dir=output_dir,
            filename_prefix="vibetester",
            transcript_name=transcript_name,
            url=url
        )
    
    print(f"\n⏱️  Timing Summary:")
    print(f"   Stage 1 (UX Extraction): {stage1_duration:.1f}s")
    print(f"   Stage 2 (Browser Test):  {stage2_duration:.1f}s")
    print(f"   Total:                   {total_duration:.1f}s")
    
    return result


def prepare_browser_tasks(ux_tasks: dict, url: str) -> str:
    """
    Transform Agent 1 output into Agent 2's expected task format.
    Replaces the URL in the first access task with the provided URL.
    
    Args:
        ux_tasks: Output from Agent 1 containing 'ux_tasks' list
        url: The web app URL to test
        
    Returns:
        JSON string of tasks ready for Agent 2
    """
    tasks = ux_tasks.get("ux_tasks", [])
    
    if not tasks:
        # Fallback: create minimal task list
        return json.dumps([
            {
                "number": 0,
                "requirement": f"Navigate to {url}"
            },
            {
                "number": 1,
                "requirement": "End of list."
            }
        ])
    
    # Update the first task (access task) with the provided URL
    processed_tasks = []
    for task in tasks:
        task_copy = task.copy()
        
        # For the access task (number 0), update the URL
        if task_copy.get("number") == 0:
            task_copy["requirement"] = f"Navigate to {url}"
            if "steps" in task_copy:
                task_copy["steps"] = [f"Navigate to {url}"]
        
        processed_tasks.append(task_copy)
    
    return json.dumps(processed_tasks)
