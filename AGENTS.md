## AGENTS.md

This document provides guidelines for AI agents working in this repository.

### Build, Lint, and Test

- **Run the bot:** `python study_bot.py`
- **Install dependencies:** `pip install -r requirements.txt`
- **Linting:** There is no linter configured. Use `black` and `isort` for formatting.
- **Testing:** There are no automated tests. Manually test new features in a Discord server.

### Code Style

- **Imports:** Use standard imports, grouped as standard library, third-party, and then local application.
- **Formatting:** Follow PEP 8. Use `black` for code formatting.
- **Types:** Use type hints for function signatures.
- **Naming:** Use `snake_case` for variables and functions. Use `UPPER_SNAKE_CASE` for constants.
- **Error Handling:** Use `try...except` blocks for API calls and other operations that might fail. Log errors to the console.
- **Docstrings:** Use docstrings for all public modules, functions, classes, and methods.
- **Structure:** The project is a single file. New features should be added as new functions or slash commands.
- **Dependencies:** Use `discord.py`, `google-generativeai`, `python-dotenv`, and `requests`.

### Commits

- **Conventional Commits:** All commits should follow the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/).
  - **Type:** Commits must be prefixed with a type (e.g., `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`).
  - **Scope:** An optional scope can be provided in parentheses, e.g., `fix(parser):`.
  - **Breaking Changes:** Use `!` after the type/scope to indicate a breaking change, e.g., `feat(api)!:`. The footer must contain a `BREAKING CHANGE:` section.
  - **Example:** `feat(auth): add password reset functionality`
