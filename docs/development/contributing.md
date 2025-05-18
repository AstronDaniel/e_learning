# Contributing to the E-Learning Platform

Thank you for your interest in contributing to our E-Learning Platform! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment** following our [Setup Guide](setup.md)
4. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Making Changes

### Coding Standards

- Follow our [Coding Standards](coding_standards.md)
- Write clean, readable, and maintainable code
- Include docstrings for all functions, classes, and modules
- Comment complex logic or algorithms

### Testing

- Write tests for all new features or bug fixes
- Ensure all existing tests pass before submitting your changes
- Follow our [Testing Guidelines](testing.md)

### Commit Messages

Use clear and descriptive commit messages with the following format:

```
[Category] Short summary (50 chars or less)

More detailed explanatory text, if necessary. Wrapped to about 72
characters. The blank line separating the summary from the body is
critical.

Explain the problem that this commit is solving. Focus on why you
are making this change as opposed to how.

Resolves: #123
See also: #456, #789
```

Categories include: [Feature], [Fix], [Refactor], [Docs], [Test], [Style], [Chore]

## Pull Request Process

1. **Create a pull request** from your fork to the main repository
2. **Fill out the pull request template** with all required information
3. **Link to any related issues** using the GitHub syntax (`Fixes #123`)
4. **Wait for review** by a project maintainer
5. **Address any feedback** provided by reviewers
6. **Update your branch** with the latest changes from the main branch if necessary
7. Once approved, your changes will be merged by a project maintainer

## Development Workflow

### Branch Strategy

- `main` - Latest stable release
- `develop` - Development branch for next release
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `release/*` - Release preparation
- `hotfix/*` - Urgent fixes for production

### Code Review Process

All code changes will be reviewed before merging:

1. Automated checks (linting, tests)
2. Manual code review by at least one maintainer
3. Additional review by affected module owners if necessary

## Documentation

All code contributions should include appropriate documentation:

- Update README.md if applicable
- Add or update docstrings for new or modified functions/classes
- Update API documentation for API changes
- Create or update user guides for new features

## Development Environment Tips

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test courses

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality Tools

```bash
# Run flake8
flake8 .

# Run isort
isort .

# Run black
black .
```

## Getting Help

If you need help with the contribution process:

- Open an issue with your question
- Contact one of the project maintainers
- Join our community chat channel

Thank you for contributing to the E-Learning Platform!
