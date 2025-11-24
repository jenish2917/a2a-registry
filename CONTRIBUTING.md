# Contributing to A2A Agent Registry

Thank you for your interest in contributing to the A2A Agent Registry!

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Run tests** (`npm test`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/a2a-registry
cd a2a-registry

# Install dependencies
cd registry-server && npm install
cd ../registry-client && npm install

# Run tests
npm test
```

## Code Standards

- Use TypeScript strict mode
- Follow ESLint configuration
- Write tests for new features
- Update documentation
- Keep commits atomic and well-described

## Testing

- Write unit tests for all new features
- Ensure all tests pass before submitting PR
- Add integration tests for API endpoints

## Pull Request Process

1. Update README.md with details of changes if needed
2. Update CHANGELOG.md with your changes
3. Ensure all tests pass
4. Request review from maintainers

## Questions?

- Open an issue for bugs
- Use discussions for questions
- Join A2A community discussions

## Code of Conduct

This project follows the [A2A Code of Conduct](https://github.com/a2aproject/A2A/blob/main/CODE_OF_CONDUCT.md).
