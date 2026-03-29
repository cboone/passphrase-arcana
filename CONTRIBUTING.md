# Contributing to passphrase-arcana

Thank you for your interest in contributing to passphrase-arcana.

Please note that this project has a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold it.

## Reporting Issues

- **Bug reports and feature requests:** Use the [issue tracker](https://github.com/cboone/passphrase-arcana/issues/new/choose)
- **Questions and ideas:** Use [GitHub Discussions](https://github.com/cboone/passphrase-arcana/discussions)
- **Security vulnerabilities:** See [SECURITY.md](.github/SECURITY.md)

## Development Setup

### Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [phraze](https://github.com/sts10/phraze) (for running `bin/arcana`)

### Getting Started

```bash
# Clone the repository
git clone https://github.com/cboone/passphrase-arcana.git
cd passphrase-arcana

# Install dependencies
uv sync

# Run tests
make test

# Run linter
make lint

# Check formatting
make fmt
```

## Code Style

- Run `make lint` before committing
- Run `make fmt` to check formatting
- Python linting and formatting is handled by [ruff](https://docs.astral.sh/ruff/)

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```text
<type>: <description>
```

**Types:**

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation changes
- `refactor`: code refactoring (no functional change)
- `test`: adding or updating tests
- `build`: build system or dependency changes
- `ci`: CI configuration changes
- `chore`: maintenance tasks

**Examples:**

```text
feat(wordlist): add new Gutenberg sources
fix(cli): handle missing clipboard tool
docs: update installation instructions
refactor(pipeline): simplify word validation logic
test: add unit tests for typing model
chore: update linter to latest version
```

## Pull Request Process

1. Fork the repository
1. Create a feature branch
1. Make your changes
1. Ensure tests pass: `make test`
1. Ensure linting passes: `make lint`
1. Submit a pull request

### Branch Naming

Use descriptive branch names with a type prefix:

- `feature/*`: new features
- `fix/*`: bug fixes
- `docs/*`: documentation changes
- `refactor/*`: code refactoring
- `test/*`: test additions or fixes
