# vibetester

End-to-end UX testing pipeline that orchestrates Agent 1 and Agent 2.

## Overview

**vibetester** takes a chat transcript (from a "vibe-coding" session) and a web app URL, then:

1. **Agent 1**: Extracts UX requirements from the conversation
2. **Agent 2**: Tests those requirements in a real browser

## Installation

This package is part of the Q-NCLC monorepo. Install from the workspace root:

```bash
uv sync
```

## Usage

### Basic Usage

```bash
# Just specify the filename - it will look in ./data/transcripts/
uv run vibetester -t sample_habit_tracker.json -u https://myapp.example.com
```

### Full Options

```bash
uv run vibetester \
  --transcript sample_habit_tracker.json \
  --url https://myapp.example.com \
  --model models/gemini-2.5-flash \
  --headless
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

| Argument             | Required | Default                   | Description                                                 |
| -------------------- | -------- | ------------------------- | ----------------------------------------------------------- |
| `--transcript`, `-t` | ✅        | —                         | Transcript filename (in `./data/transcripts/`) or full path |
| `--url`, `-u`        | ✅        | —                         | Web app URL to test                                         |
| `--model`, `-m`      | ❌        | `models/gemini-2.5-flash` | LLM model for Agent 1                                       |
| `--headless`         | ❌        | `False`                   | Run browser in headless mode                                |
| `--output`, `-o`     | ❌        | `./data/results/`         | Output directory for logs                                   |
| `--full-paths`       | ❌        | `False`                   | Treat `--transcript` and `--output` as full paths           |
| `--logging`          | ❌        | `False`                   | Enable logging (also via `LOGGING=true` env)                |

## Transcript Format

The transcript must be a JSON array of messages with `role` and `content` fields:

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
