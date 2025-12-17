# vibetester

End-to-end UX testing pipeline that orchestrates Agent 1 and Agent 2.

## Overview

**vibetester** takes a test case (containing a chat transcript and URL) or separate transcript + URL, then:

1. **Agent 1**: Extracts UX requirements from the conversation into atomic test steps
2. **Agent 2**: Tests those requirements in a real browser and generates individual results
3. **Agent 3**: Groups related atomic tests into meaningful test scenarios with aggregated results

## Installation

This package is part of the Q-NCLC monorepo. Install from the workspace root:

```bash
uv sync
```

## Usage

### Recommended: Unified Test Case (`-tc`)

The simplest way to run tests - use a single JSON file containing both the URL and transcript:

```bash
# Just specify the test case filename - it will look in ./data/test-cases/
uv run vibetester -tc pitch-humanity-simple.json
```

### Legacy: Separate URL and Transcript (`-u` and `-t`)

For flexible testing, you can specify the URL and transcript separately:

```bash
uv run vibetester -t pitch-humanity-simple.json -u https://myapp.example.com
```

### Full Options

```bash
uv run vibetester \
  --test-case pitch-humanity-simple.json \
  --model models/gemini-3-flash-preview \
  --headless \
  --no-cache
```

### Using Full Paths

If you need to specify custom paths outside the default directories:

```bash
uv run vibetester \
  --transcript /path/to/my/transcript.json \
  --url https://myapp.example.com \
  --output /path/to/custom/output/ \
  --full-paths
```

### Environment Variables

| Variable  | Description                              |
| --------- | ---------------------------------------- |
| `LOGGING` | Set to `true` to enable logging globally |

### Arguments

| Argument             | Required | Default                         | Description                                                               |
| -------------------- | -------- | ------------------------------- | ------------------------------------------------------------------------- |
| `--test-case`, `-tc` | ✅*       | —                               | Test case JSON file with `url` and `transcript` (in `./data/test-cases/`) |
| `--transcript`, `-t` | ✅*       | —                               | [Legacy] Transcript filename (in `./data/test-cases/`) or full path       |
| `--url`, `-u`        | ✅*       | —                               | [Legacy] Web app URL to test                                              |
| `--model`, `-m`      | ❌        | `models/gemini-3-flash-preview` | LLM model for Agent 1                                                     |
| `--headless`         | ❌        | `False`                         | Run browser in headless mode                                              |
| `--output`, `-o`     | ❌        | `./data/results/`               | Output directory for logs                                                 |
| `--full-paths`       | ❌        | `False`                         | Treat `--transcript` and `--output` as full paths                         |
| `--logging`          | ❌        | `False`                         | Enable logging (also via `LOGGING=true` env)                              |
| `--no-cache`         | ❌        | `False`                         | Disable DSPy caching for agent 1                                          |

*Either `--test-case` OR both `--url` and `--transcript` are required.

## Test Case Format (Recommended)

Test cases are JSON objects with `url` and `transcript` keys:

```json
{
    "url": "https://myapp.example.com",
    "transcript": [
        {"role": "user", "content": "I want to build a habit tracker app."},
        {"role": "developer", "content": "Great idea. What features do you want?"},
        {"role": "user", "content": "I need to be able to log my habits daily."},
        {"role": "developer", "content": "Daily logging, got it. What else?"}
    ]
}
```

## Legacy Transcript Format

For backward compatibility, you can still use standalone transcript files (JSON arrays):

```json
[
    {"role": "user", "content": "I want to build a habit tracker app."},
    {"role": "developer", "content": "Great idea. What features do you want?"},
    {"role": "user", "content": "I need to be able to log my habits daily."},
    {"role": "developer", "content": "Daily logging, got it. What else?"}
]
```

### Role Values

- `user`: The person requesting features
- `developer`: The person building the application

## Output

Results are logged to the output directory as JSON files with:

- Timestamp
- Configuration (URL, model, headless mode)
- Original transcript
- Agent 1 output (extracted UX tasks)
- Agent 2 output (test results)
- Timing information for each stage
