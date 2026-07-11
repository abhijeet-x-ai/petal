# Contributing to Petal

Thank you for your interest in contributing to Petal! We welcome contributions from everyone, regardless of experience level.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building a welcoming community.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the issue list to avoid duplicates.

When reporting a bug, include:
- A clear, descriptive title
- A detailed description of the problem
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)
- A minimal code example if possible

### Suggesting Enhancements

We love feature ideas! When suggesting an enhancement:
- Use a clear, descriptive title
- Provide a detailed description of the proposed feature
- Explain why this feature would be useful
- List examples of how it would be used

### Pull Requests

1. **Fork the repository** and create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and follow the code style guidelines:
   - Use 4-space indentation
   - Keep functions focused and readable
   - Add docstrings to complex logic
   - Follow PEP 8 conventions

3. **Test your changes**:
   ```bash
   python3 -m pytest tests/
   ```

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** with:
   - A clear description of the changes
   - Reference to any related issues
   - Explanation of why these changes are needed

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/petal.git
   cd petal
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install pytest
   ```

4. Run tests:
   ```bash
   python3 -m pytest tests/
   ```

## Code Style Guidelines

### Python Code

- Follow PEP 8
- Use meaningful variable names
- Keep functions small and focused
- Add comments for complex logic
- Use type hints where helpful

### Petal Code Examples

- Use clear, descriptive variable names
- Add comments explaining what the code does
- Keep examples focused on a single concept

## Testing

When adding features or fixing bugs, please include tests:

```bash
# Run all tests
python3 -m pytest tests/

# Run a specific test file
python3 -m pytest tests/test_lexer.py

# Run with verbose output
python3 -m pytest -v
```

## Documentation

- Update README.md if you add or change features
- Add docstrings to new functions
- Include examples for new language features
- Update CHANGELOG.md with significant changes

## Areas for Contribution

### Easy (Great for First-Time Contributors)
- [ ] Fix typos in documentation
- [ ] Add more example programs
- [ ] Improve error messages
- [ ] Add comments to complex code sections

### Medium
- [ ] Add new built-in functions
- [ ] Optimize interpreter performance
- [ ] Expand test coverage
- [ ] Improve documentation with tutorials

### Advanced
- [ ] Add exception handling
- [ ] Implement classes/objects
- [ ] Add module system
- [ ] Optimize with bytecode compilation

## Questions?

- Open an issue for discussion
- Check existing issues and discussions
- Reach out to maintainers

## License

By contributing to Petal, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Petal better! 🌸
