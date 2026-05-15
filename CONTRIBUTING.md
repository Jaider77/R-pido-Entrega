# 📋 Contributing Guidelines

## Code of Conduct

All contributors must follow our Code of Conduct:

- Be respectful and inclusive
- Report inappropriate behavior to maintainers
- Focus on constructive feedback

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/rapido-entrega.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Set up development environment (see DEVELOPMENT.md)
5. Make your changes
6. Run tests and linting
7. Push to your fork
8. Create a Pull Request

## Development Workflow

### Branch Naming

```
feature/feature-name      - New features
bugfix/bug-name          - Bug fixes
docs/doc-name            - Documentation
refactor/refactor-name   - Code refactoring
test/test-name           - Test additions
```

### Commit Messages

Follow conventional commits:

```
feat: add new feature description
fix: fix specific bug description
docs: update documentation
style: format/whitespace changes
refactor: code restructuring
test: add/update tests
chore: dependencies, config updates
```

### Pre-commit Checks

All commits automatically run:

- Black formatter
- Ruff linter with auto-fix
- MyPy type checking
- Bandit security scan
- Markdownlint

If pre-commit checks fail:

```bash
# Fix issues automatically
black services/ --line-length=100
ruff check services/ --fix

# Try commit again
git commit -m "feat: description"
```

## Pull Request Process

1. **Update README.md** if you change functionality
2. **Add tests** for new features (minimum 80% coverage)
3. **Update API_DOCUMENTATION.md** if API changes
4. **Link related issues** in PR description
5. **Ensure CI passes** (all checks must be green)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
```

## Code Style

### Python

- Line length: 100 characters (Black)
- Use type hints: `def func(param: str) -> int:`
- Follow PEP 8 with Ruff
- Use meaningful variable names
- Add docstrings for functions/classes

```python
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers.

    Args:
        lat1: Starting latitude
        lon1: Starting longitude
        lat2: Ending latitude
        lon2: Ending longitude

    Returns:
        Distance in kilometers
    """
    from geopy.distance import geodesic
    return geodesic((lat1, lon1), (lat2, lon2)).km
```

### JavaScript/React

- Use ESLint configuration
- Use prettier for formatting
- Use meaningful component names
- Keep components small and focused
- Use hooks instead of class components

```javascript
// Good
function UserCard({ user, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="card">
      <h2>{user.name}</h2>
      <button onClick={() => setIsEditing(true)}>Edit</button>
    </div>
  )
}
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test
pytest services/authentication/tests/test_auth.py::test_login

# With coverage
pytest --cov=services --cov-report=html

# Minimum coverage: 80%
```

### Frontend Tests

```bash
# Run tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Documentation

- Add docstrings to all functions/classes
- Update README for feature changes
- Add examples in API_DOCUMENTATION.md
- Keep DEVELOPMENT.md up to date
- Comment complex logic

## Performance Guidelines

- Use database indexes for frequently queried columns
- Cache expensive operations with Redis
- Implement pagination for large datasets
- Use async/await in Python
- Optimize React re-renders with useMemo, useCallback

## Security

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Always validate user input
- Use parameterized queries (ORM handles this)
- Keep dependencies updated
- Run Bandit security checks regularly

```bash
# Security scan
bandit -r services/ -ll
```

## API Changes

If you modify API endpoints:

1. Update API_DOCUMENTATION.md
2. Update test files
3. Create migration if database schema changes
4. Consider backward compatibility
5. Add deprecation warnings if removing endpoints

## Release Process

1. Update version in package.json and pyproject.toml
2. Create CHANGELOG entry
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions automatically creates release

## Questions or Need Help?

- Check existing issues/PRs
- Read API_DOCUMENTATION.md
- Review DEVELOPMENT.md
- Open a discussion for questions

## Thank You

Your contributions help make Rápido-Entrega better for everyone! 🎉
