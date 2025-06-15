# Contributing to GoHex

Thank you for your interest in contributing to the GoHex project! This document provides guidelines and instructions for contributing to both the template and the boilerplate generator system.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an open and welcoming environment.

## How to Contribute

There are many ways to contribute to GoHex:

1. **Report bugs**: If you find a bug, please create an issue with a detailed description.
2. **Suggest features**: Have an idea for a new feature? Open an issue to discuss it.
3. **Improve documentation**: Help us improve our documentation by fixing errors or adding examples.
4. **Submit code changes**: Implement new features or fix bugs by submitting pull requests.

## Development Workflow

### Setting Up Your Development Environment

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/gohex.git`
3. Add the upstream repository: `git remote add upstream https://github.com/gohex/gohex.git`
4. Create a new branch for your changes: `git checkout -b feature/your-feature-name`

### Making Changes

When making changes to the template or generator:

1. Follow the existing code style and architecture patterns
2. Add or update tests for your changes
3. Ensure all tests pass: `go test ./...`
4. Update documentation as needed

### Template Modifications

When modifying template files:

1. Ensure template variables are properly used and documented
2. Test template generation with various inputs
3. Verify that generated code follows best practices
4. Check that code preservation markers work correctly

### Submitting a Pull Request

1. Push your changes to your fork: `git push origin feature/your-feature-name`
2. Open a pull request against the main repository
3. Describe your changes in detail
4. Reference any related issues

## Pull Request Review Process

All pull requests will be reviewed by maintainers. The review process includes:

1. Code review for quality and adherence to standards
2. Verification that tests pass
3. Documentation review
4. Compatibility checks with existing features

## Style Guidelines

### Go Code Style

- Follow the [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- Use `gofmt` to format your code
- Follow the [Effective Go](https://golang.org/doc/effective_go) guidelines
- Run `golangci-lint run` before submitting changes

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

### Documentation Style

- Use Markdown for documentation
- Include code examples where appropriate
- Keep language clear and concise
- Update diagrams when architecture changes

## Template Design Principles

When contributing to the template design:

1. **Separation of Concerns**: Maintain clear boundaries between layers
2. **Dependency Inversion**: Dependencies should point inward
3. **Testability**: All components should be easily testable
4. **Configurability**: Components should be configurable without code changes
5. **Consistency**: Follow consistent naming and structural patterns

## License

By contributing to GoHex, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions about contributing, please open an issue or contact the maintainers directly.

Thank you for contributing to GoHex!
