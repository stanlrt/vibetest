# Agent 2

Agent 2 is an E2E agent to interact like a human would with the vibecoded app, and execute the test steps provided by Agent 1.

## Usage

```bash
uv run agent2 --headless --logging
```

### Arguments

| Argument     | Required | Default | Description                                  |
| ------------ | -------- | ------- | -------------------------------------------- |
| `--headless` | ❌        | `False` | Run browser in headless mode                 |
| `--logging`  | ❌        | `False` | Enable logging (also via `LOGGING=true` env) |

### Environment Variables

| Variable  | Description                              |
| --------- | ---------------------------------------- |
| `LOGGING` | Set to `true` to enable logging globally |

## Input

A JSON-structured list of steps that must be executed in order to test the vibecoded app

## Output

A JSON-structured test report
