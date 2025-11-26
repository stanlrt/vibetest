# Q-NCLC Monorepo

This repository contains the vibetesting agents organized as a monorepo.

## Structure

```txt
Q-NCLC/
└── packages/
    ├── agent1/       # Agent 1 implementation
    ├── agent2/       # Agent 2 implementation
    └── shared/       # Shared utilities
```

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

### Agent 1

```bash
uv run agent1
```

### Agent 2

```bash
uv run agent2
```

> [!NOTE]
> Avoid interacting with the browser window spawned by Agent 2 to not disrupt the agent.

## Development

- **Add a dependency to a package**:
  
  ```bash
  uv add --package agent1 <package-name>
  ```

- **Run tests (if available)**:
  
  ```bash
  uv run pytest
  ```
