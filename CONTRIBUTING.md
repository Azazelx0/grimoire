# Contributing to GRIMOIRE

Thank you for your interest in contributing! 🔮

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/grimoire.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dev dependencies: `pip install -r requirements.txt && pip install -e .`
5. Make your changes
6. Test: `python -m grimoire --help`
7. Commit: `git commit -m "feat: your feature description"`
8. Push: `git push origin feature/your-feature`
9. Open a Pull Request

## Development Setup

```bash
git clone https://github.com/Azazelx0/grimoire.git
cd grimoire
pip install -r requirements.txt
pip install -e .

# Verify
grimoire --help
grimoire --alecto "cisco"
```

## Code Style

- Follow PEP 8 conventions
- Keep functions focused and small
- Write tests for new features
- Use meaningful variable names
- Use type hints where practical
- Add docstrings to modules and public functions

## Adding New Features

1. Create a new module in `grimoire/` (e.g. `grimoire/my_feature.py`)
2. Add interactive mode in `grimoire/wizard.py` (`MODES` list + `_my_feature_wizard()`)
3. Add CLI flag in `grimoire/cli.py` (`@click.option` + handler)
4. Add REPL command in `grimoire/repl.py` if applicable
5. Update `docs/` with documentation
6. Update this README with usage examples

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests
- `refactor:` — Code refactoring

## Reporting Issues

- Use GitHub Issues
- Include: Python version, OS, steps to reproduce, expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
