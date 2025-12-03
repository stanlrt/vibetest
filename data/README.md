# Data Directory

This directory contains all input and output data for the Q-NCLC experiments.

## Structure

```text
data/
├── test-cases/     # Input: Test cases with URL and chat transcripts
├── results/        # Output: Vibetester pipeline results
└── legacy/         # Archive: Old experiment files
```

---

## Test Cases (`test-cases/`)

Test cases are the input for the vibetester pipeline. They contain both the URL to test and a chat transcript representing a "vibe-coding" conversation between a user and a developer.

### Format

Test cases are JSON objects with `url` and `transcript` keys:

```json
{
    "url": "https://myapp.example.com",
    "transcript": [
        {"role": "user", "content": "I want to build a habit tracker app."},
        {"role": "developer", "content": "Great idea. What features do you want?"},
        {"role": "user", "content": "I need to be able to log my habits daily."},
        {"role": "developer", "content": "Daily logging, got it."}
    ]
}
```

### Role Values

| Role        | Description                         |
| ----------- | ----------------------------------- |
| `user`      | The person requesting features      |
| `developer` | The person building the application |

### Naming Convention

Use descriptive names: `<app_name>_<variant>.json`

Examples:

- `habit_tracker_simple.json`
- `plant_dashboard_v2.json`

---

## Results (`results/`)

Pipeline outputs from vibetester runs. These are automatically generated and contain:

- **Timestamp**: When the test ran
- **Config**: URL, model, headless mode
- **Transcript**: Original input conversation
- **Agent 1 Output**: Extracted UX tasks
- **Agent 2 Output**: Browser test results
- **Timing**: Duration of each stage

### Naming Convention

Automatically generated: `YYYYMMDD_HHMMSS_vibetester.json`

### Example Output Structure

```json
{
  "timestamp": "2025-11-27T15:30:00",
  "config": {
    "url": "https://myapp.example.com",
    "model": "models/gemini-2.0-flash",
    "headless": false
  },
  "transcript": [...],
  "agent1_output": {
    "ux_tasks": [...]
  },
  "agent2_output": {
    "success": true,
    "duration_seconds": 45.2
  },
  "timing": {
    "stage1_extraction_seconds": 3.5,
    "stage2_browser_seconds": 45.2,
    "total_seconds": 48.7
  }
}
```

---

## Legacy (`legacy/`)

Archived experiment files from earlier development. Kept for reference.

---

## Running a Test

```bash
# Recommended: Use unified test case file
uv run vibetester -uc pitch-humanity-simple.json

# Legacy: Separate transcript and URL
uv run vibetester -t sample_habit_tracker.json -u https://your-app.com

# With all options
uv run vibetester \
  --use-case pitch-humanity-simple.json \
  --model models/gemini-2.0-flash \
  --headless

# Using full paths (for files outside default directories)
uv run vibetester \
  --transcript /custom/path/transcript.json \
  --url https://your-app.com \
  --output /custom/output/ \
  --full-paths
```

See `packages/vibetester/README.md` for full documentation.
