# vibetest

## Prerequisites

1. Python 3.13 or higher

2. uv

## Setup

1. Clone the repo

2. Create and activate a virtual environment

   ```bash
   uv venv
   ```

   Then follow the activation instruction (usually `source .venv/bin/activate` on Unix or `.venv\Scripts\activate` on Windows)

3. Install the deps

    ```bash
    uv pip install -e .
    ```

    > [!NOTE]  
    > If you use VSCode and Pylance cannot resolve packages, open the command palette and execute "Python: Select Interpreter". Then choos the venv.

4. Duplicate `.env.example` and add your Gemini key ([create one here](https://aistudio.google.com/app/apikey))

5. Run the script:

    ```bash
    uv run python src/main.py
    ```
