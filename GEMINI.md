# Gemini Code Assist - PRO Configuration

## 1. Project Overview

This project is a Python-based web scraping application designed for modularity and easy extension. It uses asynchronous requests, parses HTML, validates data with Pydantic, and stores results in a database.

## 2. Dependencies

### Production Dependencies:
- `dataset`
- `html2text`
- `playwright`
- `readability-lxml`
- `pydantic`
- `httpx`
- `imagehash`
- `robotexclusionrulesparser`
- `playwright-stealth`
- `pydantic-settings`

To install, run: `pip install -r requirements.txt`

### Development Dependencies:
- `pre-commit`
- `black`
- `isort`
- `flake8`
- `pytest`

To install, run: `pip install -r requirements-dev.txt`

## 3. Coding Style and Conventions

The project enforces a strict coding style via `pre-commit` hooks.

- **Formatter:** `black` (line length: 88).
- **Import Sorting:** `isort` (black profile).
- **Linter:** `flake8`.

**Golden Rule:** Before committing, always run `pre-commit run --all-files`. I must adhere to these standards for any code change.

## 4. Testing

The project uses `pytest` for all testing.

- **Test Location:** `tests/` directory.
- **Execution Command:** `pytest`
- **Configuration:** `config/pytest.ini`.

**Golden Rule:** Any new feature or bug fix must be accompanied by corresponding tests in the `tests/` directory.

## 5. Instructions for Gemini

1.  **Adhere to Conventions:** Strictly follow the coding style and testing rules defined above.
2.  **Write Tests:** Always create or update tests for any code changes.
3.  **Use Dependencies:** Leverage the existing libraries. Do not add new dependencies without explicit permission.
4.  **Be Proactive:** When asked to add a feature (e.g., a new scraper), also create the corresponding test file and ensure all checks pass.
5.  **Stay Modular:** Maintain the existing modular architecture.
