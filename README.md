# aigit

AI-assisted Git workflow tools for generating commit messages and automating repetitive Git tasks.

aigit is designed to work like a natural Git extension:

```text
write code
  ↓
run tests
  ↓
git add
  ↓
aigit commit
  ↓
review and approve
  ↓
git commit
```

AI suggests changes, but the developer remains in control. aigit never creates a commit or modifies files without approval.

## Current Features

- Generate Conventional Commit messages from staged changes
- OpenAI provider support
- Fake provider for local testing
- Project-level configuration
- `.env` secret loading
- Ruff formatting and linting
- Bandit security scanning
- pip-audit dependency scanning
- Combined security report generation
- GitHub Actions CI
- Release Please integration

## Requirements

- Python 3.11+
- Git
- An OpenAI API key for the OpenAI provider

## Installation

Clone the repository:

```bash
git clone https://github.com/imIwKy/aigit.git
cd aigit
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install aigit in editable mode:

```bash
python -m pip install -e ".[dev]"
```

Editable installation means changes to the source code are immediately available when running `aigit`.

Verify the installation:

```bash
aigit --help
aigit --version
```

## Basic Usage

aigit operates on the Git repository in the current working directory.

Stage changes first:

```bash
git add path/to/file.py
```

Generate a commit message:

```bash
aigit commit
```

aigit will:

1. Read the staged diff.
2. Send the diff to the configured provider.
3. Display a suggested commit message.
4. Ask for approval.
5. Create the commit only if approved.

Example:

```text
Suggested commit message:
--------------------------------
feat(provider): add OpenAI commit provider

- Add OpenAI provider implementation
- Load API keys from environment configuration
- Add provider tests
--------------------------------
Create this commit? [y/N]:
```

Press `y` to create the commit. Any other response cancels it.

## Configuration

Project configuration is stored in:

```text
.aigit/config.json
```

Example:

```json
{
  "provider": {
    "name": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.2,
    "system_prompt": "Generate a Release Please-compatible Conventional Commit message. Return only the commit message. Do not use Markdown code fences or quotation marks. Use feat only for genuinely new user-visible capabilities. Use fix for corrections to existing behavior. Use chore, ci, build, test, docs, or refactor for changes that do not alter user-facing behavior. Use breaking changes only for incompatible changes."
  },
  "commit": {
    "max_title_length": 72
  }
}
```

The provider configuration supports:

| Setting | Description |
|---|---|
| `name` | Provider identifier, such as `fake` or `openai` |
| `model` | Model override |
| `temperature` | LLM response temperature |
| `system_prompt` | Provider behavior instructions |
| `fake_message` | Message returned by the fake provider |
| `max_title_length` | Maximum commit title length |

Provider definitions contain provider-specific defaults such as endpoints and API key environment variable names. Project configuration selects and overrides those defaults.

## API Keys and Secrets

Do not store API keys in `.aigit/config.json`.

For local development, create a `.env` file in the project repository:

```dotenv
OPENAI_API_KEY=your-api-key
```

Alternatively, create a global aigit environment file:

```text
~/.config/aigit/.env
```

The shell environment takes precedence over `.env` values:

```bash
export OPENAI_API_KEY="your-api-key"
```

`.env` files must not be committed. The repository ignores them through `.gitignore`.

A template is available in:

```text
.env.example
```

## Providers

### Fake Provider

The fake provider is useful for testing the workflow without making API requests:

```json
{
  "provider": {
    "name": "fake",
    "fake_message": "chore: test commit"
  }
}
```

### OpenAI Provider

Use the OpenAI provider with:

```json
{
  "provider": {
    "name": "openai",
    "model": "gpt-4o-mini"
  }
}
```

The provider uses the `OPENAI_API_KEY` environment variable.

## Release Please Commit Semantics

aigit prompts are designed to work with Google's Release Please tool.

Use:

```text
feat(scope): add new user-facing functionality
```

for a new feature. This normally creates a minor release.

Use:

```text
fix(scope): correct existing behavior
```

for a bug fix. This normally creates a patch release.

Use:

```text
feat(config)!: replace configuration format

BREAKING CHANGE: configuration files must be migrated
```

for an incompatible change. This normally creates a major release.

Use maintenance types for changes that should not trigger a release:

```text
chore(ci): update workflow
ci: configure GitHub Actions
build: update packaging configuration
test: add provider tests
docs: update README
refactor: simplify provider creation
```

## Development Commands

Run tests:

```bash
pytest
```

Run tests with concise output:

```bash
pytest -q
```

Format Python files:

```bash
ruff format .
```

Check formatting without modifying files:

```bash
ruff format --check .
```

Run linting:

```bash
ruff check .
```

Automatically apply supported lint fixes:

```bash
ruff check --fix .
```

Run Bandit:

```bash
bandit -r src -c pyproject.toml
```

Run dependency auditing:

```bash
pip-audit
```

Generate security reports:

```bash
bandit \
  -r src \
  -c pyproject.toml \
  -f json \
  -o bandit-report.json || true

pip-audit \
  --format json \
  --output pip-audit-report.json || true

python scripts/security_report.py
```

The combined report is written to:

```text
security-report.md
```

Generated security reports should not be committed.

## VS Code

Install the Ruff extension:

```text
Ruff
Publisher: Astral Software
```

The project settings enable:

- Format on save
- Ruff as the Python formatter
- Import organization
- Ruff linting on save
- Automatic supported Ruff fixes

Project settings are stored in:

```text
.vscode/settings.json
```

## GitHub Actions

The repository includes CI workflows for:

- Python formatting
- Python linting
- Python tests
- Bandit security scanning
- pip-audit dependency scanning
- Combined security reports
- Release Please

Security reports are uploaded as GitHub Actions artifacts and posted as pull request comments.

Required checks should be configured for the `stable` branch:

```text
Python Format / Check Python formatting
Python Lint / Run Ruff lint
Python Tests / Run Python tests
Security Report / Generate security report
```

## Release Please

The main branch for this repository is:

```text
stable
```

Release Please is configured through:

```text
release-please-config.json
.release-please-manifest.json
.github/workflows/release-please.yml
```

When releasable Conventional Commits are pushed to `stable`, Release Please creates or updates a release pull request.

After the release pull request is merged, Release Please updates:

- `pyproject.toml`
- `CHANGELOG.md`
- Git tags
- GitHub releases

The release workflow can enable auto-merge after required checks pass.

## Project Structure

```text
aigit/
├── .aigit/
│   └── config.json
├── .github/
│   └── workflows/
├── scripts/
│   ├── __init__.py
│   └── security_report.py
├── src/
│   └── aigit/
│       ├── __main__.py
│       ├── cli.py
│       ├── git.py
│       ├── config/
│       ├── providers/
│       └── workflows/
├── tests/
│   ├── unit/
│   └── regression/
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

## Design Principles

- AI suggests; the developer approves.
- Never silently modify code or documentation.
- Use Git diffs as the safety mechanism.
- Keep commands small and composable.
- Keep provider implementations behind a common interface.
- Keep secrets out of project configuration.
- Prefer explicit approval before mutations.
- Use CI to enforce formatting, linting, tests, and security checks.