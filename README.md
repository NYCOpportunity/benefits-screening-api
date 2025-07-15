# Benefits Screening API

WIP - refactor of the Benefits Screening API and rules code in Python

## Setup Instructions

1. **Install uv package manager:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   **Note:** Can also install it with pip: `pip install uv`

2. **Install dependencies and create virtual environment:**
   ```bash
   uv sync
   ```

3. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

4. **Run the application:**
   ```bash
   uv run python src/main.py
   ```

## Test Instructions

Run tests using uv with PyTest:
```bash
uv run pytest tests/
```

## TODO
- Add the rest of the program rules
- Add deployment information
- Thoroughly test the program rules with different JSONs and expected values 


