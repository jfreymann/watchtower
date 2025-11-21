# Contributing to Watchtower

Thank you for your interest in contributing to Watchtower! This document provides guidelines for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [License Agreement](#license-agreement)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Prioritize security and user privacy
- Maintain professional communication

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other conduct inappropriate for a professional setting

---

## How to Contribute

### Types of Contributions

We welcome:

- **Bug reports** - Help us identify and fix issues
- **Feature requests** - Propose new functionality
- **Code contributions** - Submit bug fixes or new features
- **Documentation** - Improve guides, examples, or API docs
- **Security reports** - Responsible disclosure of vulnerabilities
- **Testing** - Help test new features or releases

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your changes
4. **Make your changes** following our guidelines
5. **Test thoroughly** before submitting
6. **Submit a pull request** with a clear description

---

## Development Setup

### Prerequisites

- Python 3.11+ (3.12 recommended)
- Git
- Virtual environment tool (venv)
- Docker (optional, for testing containers)

### Local Setup

#### Collector

```bash
cd collector
python3 -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Set environment variables
cp .env-sample .env
# Edit .env with your test configuration

# Run locally
uvicorn main:app --reload
```

#### Agent

```bash
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
cp .env-sample .env
# Edit .env with your test configuration

# Run locally (requires root for journalctl)
sudo -E python watchtower_agent.py
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# View logs
docker-compose logs -f
```

---

## Contribution Guidelines

### Branch Naming

Use descriptive branch names:

- `feature/add-postgres-support`
- `fix/agent-crash-on-startup`
- `docs/update-installation-guide`
- `security/fix-sql-injection`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `security`: Security-related changes

**Examples:**

```
feat(collector): add PostgreSQL database support

- Implement PostgreSQL connection pooling
- Add migration scripts from SQLite
- Update configuration documentation

Closes #123
```

```
fix(agent): prevent crash when journald is unavailable

- Add graceful fallback when journalctl fails
- Log warning instead of crashing
- Implement retry with exponential backoff

Fixes #456
```

### Copyright Headers

All new Python files must include the copyright header:

```python
# Copyright © 2025 Jaye Freymann / The Watchtower Project
#
# This file is part of Watchtower, licensed under the Watchtower Community License 1.0.
# You may not use this file except in compliance with the License.
# See LICENSE.md for details.
#
# For commercial licensing: jfreymann@gmail.com
```

See `COPYRIGHT-HEADER.txt` for the template.

---

## License Agreement

### Contributor License Agreement (CLA)

By contributing to Watchtower, you agree that:

1. **Your contributions are your original work** or you have the right to submit them
2. **You grant the project perpetual rights** to use your contributions
3. **Your contributions will be licensed** under the Watchtower Community License 1.0
4. **You retain copyright** to your contributions
5. **The project may relicense** or dual-license in the future if needed
6. **You understand** that your contributions may be used in commercial versions

### Important Notes

- All contributions are subject to the [Watchtower Community License 1.0](LICENSE.md)
- Commercial use requires a separate commercial license
- Contributing does not grant you rights to use Watchtower commercially
- See [docs/licensing-guide.md](docs/licensing-guide.md) for details

---

## Pull Request Process

### Before Submitting

- [ ] Read the [Licensing Guide](docs/licensing-guide.md)
- [ ] Create an issue to discuss major changes
- [ ] Fork the repository and create a feature branch
- [ ] Follow the coding standards below
- [ ] Add tests for new functionality
- [ ] Update documentation as needed
- [ ] Add copyright headers to new files
- [ ] Run linting and tests locally
- [ ] Ensure all changes are committed

### PR Checklist

Your pull request should:

- [ ] Have a clear, descriptive title
- [ ] Reference related issues (e.g., "Fixes #123")
- [ ] Include a detailed description of changes
- [ ] Follow coding standards and conventions
- [ ] Include tests that verify the fix/feature
- [ ] Update relevant documentation
- [ ] Pass all CI/CD checks
- [ ] Maintain or improve code coverage
- [ ] Not introduce security vulnerabilities
- [ ] Include copyright headers on new files

### PR Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Security fix
- [ ] Performance improvement

## Related Issues
Fixes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass locally

## Documentation
- [ ] README updated
- [ ] API docs updated
- [ ] Comments added to complex code
- [ ] CHANGELOG updated (if applicable)

## Security Considerations
Describe any security implications or validations

## Breaking Changes
List any breaking changes and migration steps

## Screenshots (if applicable)
Add screenshots for UI changes
```

### Review Process

1. **Automated checks** run on all PRs (linting, tests)
2. **Maintainer review** - at least one approval required
3. **Security review** for security-related changes
4. **Discussion** - address feedback and questions
5. **Approval** - merge when all checks pass and approved
6. **Merge** - squash and merge with clean commit message

---

## Coding Standards

### Python Style

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length:** 88 characters (Black default)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Organized (stdlib, third-party, local)
- **Type hints:** Required for function signatures
- **Docstrings:** Google style for public functions

### Linting

Use these tools:

```bash
# Install development dependencies
pip install ruff black mypy

# Format code
black .

# Lint code
ruff check .

# Type checking
mypy collector/ agent/
```

### Code Quality

- Keep functions focused and small
- Use meaningful variable names
- Add comments for complex logic
- Avoid premature optimization
- Handle errors gracefully
- Log appropriately (not excessively)

### Security Best Practices

- **Input validation:** Validate all external input
- **No secrets in code:** Use environment variables
- **SQL injection:** Use parameterized queries (SQLAlchemy ORM)
- **Path traversal:** Validate file paths
- **XSS prevention:** Escape output (handled by FastAPI)
- **Rate limiting:** Implement for public endpoints
- **Authentication:** Always verify tokens/keys
- **Logging:** Never log secrets or sensitive data

---

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_collector.py
```

### Writing Tests

- **Unit tests:** Test individual functions/classes
- **Integration tests:** Test component interactions
- **End-to-end tests:** Test complete workflows
- **Security tests:** Test auth, validation, etc.

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    setup_data()

    # Act
    result = function_to_test()

    # Assert
    assert result == expected_value
```

### Coverage Requirements

- **Minimum coverage:** 70% overall
- **New code:** 80% coverage for new features
- **Critical paths:** 100% coverage for security/auth code

---

## Documentation

### What to Document

- **Code changes:** Update relevant docs
- **New features:** Add usage examples
- **API changes:** Update API reference
- **Breaking changes:** Add migration guide
- **Configuration:** Document new env vars
- **Architecture:** Update design docs for major changes

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex flows
- Keep README up to date
- Update CHANGELOG for releases

### Where to Add Documentation

- **README.md:** Project overview and quick start
- **docs/:** Detailed guides and architecture
- **Code comments:** Explain complex logic
- **Docstrings:** Document public APIs
- **CHANGELOG.md:** Track version changes

---

## Security Vulnerability Reporting

**DO NOT** open a public issue for security vulnerabilities.

Instead:

1. Email: **jfreymann@gmail.com**
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
3. Allow time for a fix before public disclosure
4. See [security.md](security.md) for full policy

---

## Release Process

Releases are managed by maintainers. Contributors should:

- Ensure PRs target the correct branch
- Update CHANGELOG.md with notable changes
- Follow semantic versioning for feature requests

---

## Getting Help

### Resources

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/jfreymann/watchtower/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jfreymann/watchtower/discussions)
- **Security:** [security.md](security.md)

### Questions?

- Check existing issues and discussions first
- Open a new discussion for questions
- Use issues only for bugs or feature requests

---

## Recognition

Contributors will be:

- Listed in release notes
- Credited in commit history
- Mentioned in acknowledgments (for significant contributions)

---

## Thank You!

Your contributions make Watchtower better for everyone. We appreciate your time and effort! 🛡️

---

© 2025 Jaye Freymann / The Watchtower Project
Licensed under the Watchtower Community License 1.0
