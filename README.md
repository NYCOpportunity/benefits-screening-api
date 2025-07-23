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

## Deployment

Automated deployment via branch merges:

- **Staging:** Merge to `stg` → deploys to staging Lambda
- **Production:** Merge to `prod` → deploys to production Lambda

**Workflow:** Feature branch → PR → `stg` → test → `prod`

> ⚠️ Always test in staging before production deployment

## How to add a rule
1. Create a new file under [`program_rules`](src/rules/program_rules) titled as the program code, and modify the program and description to match the new rule. I recommend just duplicating an existing file and renaming it. 
2. Write the rule logic `evaluate` method. This method will take in an `AggregateEligibilityRequest` under the `request` parameter, use this to write the rule logic. Feel free to create helper functions within the class to compute values, but `evaluate` must return true or false
3. Your new rule will be auto-registered under the registry system, allowing it to be iterated through when checking all rules. It will also be auto-registered in the unit test, make sure to update the data for expected values on different test requests. 


## TODO
- Thoroughly test the program rules with different JSONs and expected values 
