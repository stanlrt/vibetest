# Agent 1

Agent 1 extracts formal requirements from a natural language conversation between a human user and the vibecoding agent, and translates them into a JSON-structured list of testing steps.

## Usage

```bash
uv run agent1 --model models/gemini-2.0-flash --logging
```

### Arguments

| Argument    | Required | Default                   | Description                                  |
| ----------- | -------- | ------------------------- | -------------------------------------------- |
| `--model`   | ❌        | `models/gemini-2.0-flash` | LLM model to use                             |
| `--logging` | ❌        | `False`                   | Enable logging (also via `LOGGING=true` env) |

### Environment Variables

| Variable  | Description                              |
| --------- | ---------------------------------------- |
| `LOGGING` | Set to `true` to enable logging globally |

## Input

- A natural language conversation between a human user and the vibecoding agent
- The URL of the vibecoded app to test

## Output

A JSON-structured list of steps agent 2 must execute in order to test the vibecoded app
