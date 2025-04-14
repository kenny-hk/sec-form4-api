# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run script: `python InsiderTrading.py`
- Install dependencies: `pip install secedgar pandas`
- Run linting: `flake8 *.py`
- Format code: `black .`
- Type checking: `mypy *.py`

## Code Style Guidelines
- Imports: Group standard library first, third-party packages second, local imports last
- Formatting: 4 spaces for indentation, 79-char line limit
- Docstrings: Use triple quotes for all functions/classes following Google style
- Variables: snake_case for variables/functions, PascalCase for classes
- Type hints: Add type annotations for function parameters and return values
- Error handling: Use specific exceptions with descriptive messages
- File paths: Store data in a 'data' subdirectory with appropriate structure
- Function design: Single responsibility principle, clear input/output interfaces