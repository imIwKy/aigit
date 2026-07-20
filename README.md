# aigit

AI-assisted Git workflow tools for generating commit messages and automating repetitive Git tasks.

aigit helps developers generate commit messages from staged Git changes while keeping the developer in control.

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

AI suggests changes, but the developer remains responsible for the final result. aigit never creates commits or modifies files without approval.

---

# Using aigit

This section contains information for users installing and using aigit.

## Features

- Generate commit messages from staged Git changes
- OpenAI provider support
- Fake provider for local testing
- Project-level configuration
- Environment-based secret loading

## Requirements

- Python 3.11+
- Git
- An API key for the configured AI provider

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

Install aigit:

```bash
python -m pip install -e .
```

Verify the installation:

```bash
aigit --help
aigit --version
```

## Basic Usage

aigit operates on the Git repository in the current working directory.

Stage changes:

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
3. Generate a commit message.
4. Ask for approval.
5. Create the commit only after approval.

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

Only approving the prompt creates the commit.

---

# Configuration

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
    "system_prompt": "Generate a commit message from the staged changes."
  },
  "commit": {
    "max_title_length": 72
  }
}
```

Configuration options:

| Setting | Description |
|---|---|
| `name` | Provider identifier |
| `model` | AI model override |
| `temperature` | AI response temperature |
| `system_prompt` | Instructions sent to the provider |
| `fake_message` | Fake provider response |
| `max_title_length` | Maximum commit title length |

Provider implementations may provide defaults such as API endpoints and environment variable names. Project configuration overrides those defaults.

---

# API Keys and Secrets

Do not store API keys in:

```text
.aigit/config.json
```

For local development, create:

```text
.env
```

Example:

```dotenv
OPENAI_API_KEY=your-api-key
```

Alternatively:

```text
~/.config/aigit/.env
```

Environment variables take precedence over `.env` values:

```bash
export OPENAI_API_KEY="your-api-key"
```

`.env` files should not be committed.

A template is available:

```text
.env.example
```

---

# Providers

## Fake Provider

The fake provider allows testing without making API requests.

Example:

```json
{
  "provider": {
    "name": "fake",
    "fake_message": "chore: test commit"
  }
}
```

## OpenAI Provider

Example:

```json
{
  "provider": {
    "name": "openai",
    "model": "gpt-4o-mini"
  }
}
```

The OpenAI provider uses:

```text
OPENAI_API_KEY
```

for authentication.

---

# Commit Message Formats

aigit does not enforce a commit message format.

The generated output is controlled by the configured provider prompt.

For example, a project may configure a provider to generate Conventional Commit messages:

```text
feat(scope): add new functionality
```

or:

```text
fix(scope): correct existing behavior
```

Other formats can be used by changing the provider configuration.

---

# Developing aigit

This section contains information for contributors, maintainers, and people creating forks.

---

# Development Setup

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

---

# Project Structure

```text
aigit/
├── .aigit/
│   └── config.json
├── .github/
│   └── workflows/
├── scripts/
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

---

# Architecture

aigit separates Git workflow handling from AI provider implementations.

The provider layer handles:

- Communication with AI services
- Provider-specific configuration
- Generating commit suggestions

The workflow layer handles:

- Git interaction
- Reading staged changes
- User approval
- Commit creation

The goal is to keep providers replaceable and prevent provider-specific logic from leaking into the core workflow.

---

# Development Commands

## Tests

```bash
pytest
```

```bash
pytest -q
```

## Formatting

```bash
ruff format .
```

Check formatting:

```bash
ruff format --check .
```

## Linting

```bash
ruff check .
```

Apply fixes:

```bash
ruff check --fix .
```

## Security

Run Bandit:

```bash
bandit -r src -c pyproject.toml
```

Run dependency auditing:

```bash
pip-audit
```

Generate combined security reports:

```bash
python scripts/security_report.py
```

Generated reports should not be committed.

---

# Repository Tooling

The repository uses:

- Ruff formatting and linting
- Bandit security scanning
- pip-audit dependency scanning
- GitHub Actions CI
- Release automation

These tools enforce repository quality but are not required for using aigit.

---

# Release Process

The repository release process uses Release Please.

Configuration:

```text
release-please-config.json
.release-please-manifest.json
.github/workflows/release-please.yml
```

The release workflow manages:

- Version updates
- Changelog generation
- Git tags
- GitHub releases

The main development branch is:

```text
stable
```

---

# Design Principles

- AI suggests; developers approve.
- Never silently modify files.
- Use Git diffs as the safety boundary.
- Keep commands small and composable.
- Keep providers behind a common interface.
- Keep secrets outside project configuration.
- Require explicit approval before mutations.