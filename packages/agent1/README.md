# Agent 1

Agent 1 extracts formal requirements from a natural language conversation between a human user and the vibecoding agent, and translates them into a JSON-structured list of testing steps.

## Example usage

```bash
uv run agent1 --model models/gemini-3-flash-preview --logging --no-cache
```

### Arguments

| Argument     | Required | Default                         | Description                                  |
| ------------ | -------- | ------------------------------- | -------------------------------------------- |
| `--model`    | ❌        | `models/gemini-3-flash-preview` | LLM model to use                             |
| `--logging`  | ❌        | `False`                         | Enable logging (also via `LOGGING=true` env) |
| `--no-cache` | ❌        | `False`                         | Disable DSPy caching for fresh LLM responses |

### Environment Variables

| Variable  | Description                              |
| --------- | ---------------------------------------- |
| `LOGGING` | Set to `true` to enable logging globally |

## Input

- A natural language conversation between a human user and the vibecoding agent
- The URL of the vibecoded app to test

## Output

A JSON-structured list of steps agent 2 must execute in order to test the vibecoded app
