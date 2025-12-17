# Q-NCLC Monorepo

This repository contains the vibetesting agents organized as a monorepo.

## Structure

```txt
Q-NCLC/
├── data/
│   ├── test-cases/    # Input test cases (URL + chat transcripts)
│   ├── results/       # Output logs from test runs
│   └── legacy/        # Old experiment files
└── packages/
    ├── agent1/        # UX task extraction from conversations
    ├── agent2/        # Browser-based UX testing
    ├── vibetester/    # Pipeline orchestrating Agent 1 + Agent 2
    └── shared/        # Shared utilities (logging, LLM providers)
```

## System Overview

The system consists of two main agents working in a pipeline:

- **Agent 1 (Requirement Extractor)**: Analyzes natural language conversations between a user and a coding assistant to extract formal testing requirements. It produces a structured list of test steps.
- **Agent 2 (Browser Tester)**: Takes the test steps from Agent 1 and executes them in a real browser environment to verify the application's behavior. It acts as an automated user and generates a test report.

Together, they form the **Vibetester** pipeline, testing the application's behavior based on the user's intent.

## Prerequisites

1. Python 3.12 or higher
2. [uv](https://github.com/astral-sh/uv)

## Setup

1. Clone the repo

2. Sync dependencies:

   ```bash
   uv sync
   ```

   > [!NOTE]
   > `uv sync` automatically creates a virtual environment in `.venv`.
   > If you use VSCode and Pylance cannot resolve packages, open the command palette, execute "Python: Select Interpreter", and choose the environment in `.venv`.

3. Duplicate `.env.example` to `.env` and add your API keys (e.g., `BROWSER_USE_API_KEY`, `OPENAI_API_KEY`, etc.).

## Running the Agents

### Vibetester (full pipeline)

The full pipeline: extracts UX requirements from a test case and tests them in a browser.

```bash
# Recommended: Use unified test case file (contains URL and transcript)
uv run vibetester -tc pitch-humanity-simple.json

# Legacy: Separate transcript and URL
uv run vibetester -t my_transcript.json -u https://myapp.example.com
```

This will:

1. Load the test case from `./data/test-cases/pitch-humanity-simple.json`
2. Extract UX requirements using Agent 1
3. Test them in a browser using Agent 2
4. Save results to `./data/results/` (when `--logging` is enabled)

Run `uv run vibetester --help` for all options, or refer to the [dedicated README](./packages/vibetester/README.md#arguments).

### Agent 1 (Standalone)

```bash
uv run agent1
```

Run `uv run agent1 --help` for all options, or refer to the [dedicated README](./packages/agent1/README.md#arguments).

### Agent 2 (Standalone)

```bash
uv run agent2
```

Run `uv run agent2 --help` for all options, or refer to the [dedicated README](./packages/agent2/README.md#arguments).

> [!NOTE]
> Avoid interacting with the browser window spawned by Agent 2 to not disrupt the agent.

## Logging

Logging is **disabled by default**. Enable it via:

- **CLI flag**: `--logging`
- **Environment variable**: `LOGGING=true`

Logs are saved to `./data/results/` as JSON files with timestamps.

## Development

- **Add a dependency to a package** (e.g. agent 1):
  
  ```bash
  uv add --package agent1 <package-name>
  ```
