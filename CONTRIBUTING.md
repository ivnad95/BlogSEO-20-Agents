# Contributing to BlogSEO v3

Thank you for your interest in contributing to BlogSEO v3! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Review Process](#code-review-process)

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip
- virtualenv (recommended)

### Initial Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/blogseo-v3.git
   cd blogseo-v3
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the project with development dependencies**
   ```bash
   make install
   # Or manually:
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. **Set up your environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Verify the installation**
   ```bash
   make test
   make lint
   ```

## 📝 Code Style Guidelines

We use automated tools to maintain consistent code style across the project:

### Automatic Formatting

Before committing any code, run:

```bash
make format
```

This will:
- Format code with **Black** (100 character line limit)
- Sort imports with **isort**

### Linting

Check your code for style issues:

```bash
make lint
```

This runs **flake8** with our custom configuration.

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit to ensure code quality:

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run on staged files (happens automatically on commit)
git commit -m "Your message"
```

The pre-commit hooks will:
1. Format code with Black
2. Sort imports with isort
3. Run flake8 linting
4. Check for syntax errors
5. Fix common issues (trailing whitespace, file endings, etc.)
6. Run security checks with Bandit
7. Type check with mypy

### Code Style Rules

1. **Docstrings**: Use Google-style docstrings for all public functions and classes
   ```python
   def process_data(input_data: str, validate: bool = True) -> dict:
       """Process input data and return structured output.
       
       Args:
           input_data: Raw input string to process
           validate: Whether to validate the input
           
       Returns:
           Processed data as a dictionary
           
       Raises:
           ValueError: If input_data is empty or invalid
       """
   ```

2. **Type Hints**: Use type hints for function arguments and return values
   ```python
   from typing import List, Optional, Dict
   
   def get_keywords(text: str, max_count: Optional[int] = None) -> List[str]:
       ...
   ```

3. **Naming Conventions**:
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private methods/attributes: `_leading_underscore`

4. **Imports**: Organize imports in this order (handled by isort):
   - Standard library imports
   - Third-party imports
   - Local application imports

## 🔧 Making Changes

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Add docstrings and comments where necessary
   - Update tests if needed
   - Update documentation if needed

3. **Format and lint your code**
   ```bash
   make format
   make lint
   ```

4. **Run tests**
   ```bash
   make test
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature X"
   ```

### Commit Message Format

We follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Examples:
```bash
git commit -m "feat: add keyword density analyzer"
git commit -m "fix: resolve API timeout issue"
git commit -m "docs: update installation instructions"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run tests matching pattern
pytest -k "test_keyword"
```

### Writing Tests

1. Place tests in the `tests/` directory
2. Name test files with `test_` prefix
3. Use descriptive test names that explain what is being tested
4. Use fixtures for common test data
5. Aim for at least 70% code coverage

Example test:
```python
import pytest
from agents.keyword_mining import KeywordMiner

def test_keyword_extraction():
    """Test that keyword extraction returns expected results."""
    miner = KeywordMiner()
    text = "Python programming is essential for data science"
    keywords = miner.extract_keywords(text)
    
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    assert "python" in [k.lower() for k in keywords]
```

## 📤 Submitting Changes

### Pull Request Process

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Go to GitHub and create a new Pull Request
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link any related issues

3. **PR Checklist**
   - [ ] Code follows style guidelines
   - [ ] All tests pass
   - [ ] Documentation is updated
   - [ ] Commit messages follow convention
   - [ ] PR description explains the changes

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed

## Related Issues
Fixes #123
```

## 👀 Code Review Process

1. **Automated Checks**: GitHub Actions will run tests and linting
2. **Peer Review**: At least one maintainer will review the code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, the PR will be merged

### Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations

## 🤝 Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the README and docs/ folder
- **Contact**: Reach out to maintainers via GitHub

## 📜 Code of Conduct

Please note that this project has a Code of Conduct. By participating, you agree to abide by its terms.

## 🙏 Thank You!

Thank you for contributing to BlogSEO v3! Your efforts help make this project better for everyone.

---
*Happy coding! 🚀*
