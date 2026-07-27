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
review, edit, or regenerate
  ↓
git commit
```

AI suggests changes, but the developer remains responsible for the final result. aigit never creates commits or modifies files without approval.

---

# Using aigit

This section contains information for users installing and using aigit.

## Features

- Generate commit messages from staged Git changes
- Review, edit, regenerate, or reject a suggested message before it is committed
- Pluggable AI providers: bring your own OpenAI-compatible or Anthropic-compatible endpoint, defined in project configuration
- Built-in fake provider for local testing without API calls
- Project-level configuration
- Environment-based secret loading
- Optional debug logging for troubleshooting

## Requirements

- Python 3.11+
- Git
- An API key for the configured AI provider (not required when using the fake provider)

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

Choose an action: [y]es, [e]dit, [r]egenerate, [N]o:
```

At the prompt you can:

- `y` — create the commit with the suggested message.
- `e` — open the message in an editor before committing (see [Editing Commit Messages](#editing-commit-messages)).
- `r` — discard the suggestion and ask the provider to generate a new one.
- `N` (or Enter) — cancel without creating a commit.

Only choosing `y` (optionally after editing) creates the commit.

### Editing Commit Messages

Choosing `e` opens the suggested message in an editor:

- aigit uses the `VISUAL` environment variable if set, otherwise `EDITOR`.
- If neither is set, aigit falls back to Notepad, which is only available on Windows. On Linux and macOS, set `VISUAL` or `EDITOR` to use the edit option.
- The message is written to a temporary file, opened in the editor, and read back once the editor exits. An empty file is rejected.

### Other Commands

```bash
aigit docs
aigit pr
```

The `docs` and `pr` subcommands are registered in the CLI but are not implemented yet; running them prints a "not implemented" message and exits successfully.

### Debug Logging

Pass `--debug` before the subcommand to enable detailed diagnostic logging on stderr, including which provider and configuration values were selected:

```bash
aigit --debug commit
```

Without `--debug`, only warnings and errors are shown.

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
| `provider.name` | Name of the provider to use, matching a key in `.aigit/providers.json` (or `fake`) |
| `provider.model` | AI model override; falls back to the provider's default model |
| `provider.temperature` | AI response temperature |
| `provider.system_prompt` | Instructions sent to the provider |
| `provider.fake_message` | Message returned by the fake provider |
| `commit.provider` | Overrides `provider.name` specifically for the commit workflow |
| `commit.max_title_length` | Maximum commit title length (currently informational; not yet enforced by the CLI) |

If `.aigit/config.json` is missing, aigit runs with defaults (no provider selected by name, `temperature` `0.2`, `max_title_length` `72`).

Provider *implementations* (their protocol, base URL, default model, and API key variable) are defined separately, in `.aigit/providers.json` — see [Providers](#providers) below.

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

aigit loads the global `~/.config/aigit/.env` file first, then the project-level `.env` file. Environment variables already set — either exported in your shell or loaded from the global file — always take precedence over values in the project `.env` file:

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

aigit's AI providers are split into two layers:

- **Protocols** — built into aigit's code: `fake`, `openai-compatible`, and `anthropic`.
- **Definitions** — named providers you configure, each backed by one of the protocols above.

Only the `fake` provider is available out of the box. To use a real AI provider, define it in:

```text
.aigit/providers.json
```

Example, defining an OpenAI provider and an Anthropic provider:

```json
{
  "default": "openai",
  "providers": {
    "openai": {
      "display_name": "OpenAI",
      "protocol": "openai-compatible",
      "base_url": "https://api.openai.com/v1",
      "api_key_environment_variable": "OPENAI_API_KEY",
      "default_model": "gpt-4o-mini"
    },
    "claude": {
      "display_name": "Anthropic",
      "protocol": "anthropic",
      "base_url": null,
      "api_key_environment_variable": "ANTHROPIC_API_KEY",
      "default_model": "claude-3-5-sonnet-latest"
    }
  }
}
```

Provider definition fields:

| Field | Description |
|---|---|
| `display_name` | Human-readable name for the provider |
| `protocol` | One of `openai-compatible`, `anthropic`, or `fake` |
| `base_url` | API base URL (required for `openai-compatible`; ignored for `anthropic` and `fake`) |
| `api_key_environment_variable` | Name of the environment variable holding the API key |
| `default_model` | Model used when `provider.model` is not set in `config.json` |

The top-level `default` key selects which provider is used when `provider.name` (and `commit.provider`) are not set in `config.json`.

## Provider Selection

When resolving which provider to use, aigit applies these rules in order:

1. `commit.provider` in `config.json`, if set.
2. Otherwise `provider.name` in `config.json`, if set.
3. Otherwise the `default` key in `providers.json`, if set.
4. Otherwise, if exactly one non-`fake` provider is defined, that provider is used automatically.
5. Otherwise, aigit raises an error: with zero non-`fake` providers defined it reports that no usable provider is configured; with more than one it asks you to set a provider explicitly.

## Fake Provider

The fake provider allows testing without making API requests. It requires no entry in `providers.json` and no API key.

Example:

```json
{
  "provider": {
    "name": "fake",
    "fake_message": "chore: test commit"
  }
}
```

## OpenAI-Compatible Provider

The `openai-compatible` protocol works with the OpenAI API as well as any service exposing an OpenAI-compatible chat completions endpoint (for example, locally hosted models), by pointing `base_url` at that service.

```json
{
  "provider": {
    "name": "openai",
    "model": "gpt-4o-mini"
  }
}
```

The API key is read from whichever environment variable is set as `api_key_environment_variable` in the provider's definition (`OPENAI_API_KEY` in the example above). If a provider definition omits `api_key_environment_variable`, a placeholder key is used, which is appropriate for local endpoints that don't require authentication.

## Anthropic Provider

The `anthropic` protocol talks to the Anthropic Messages API.

```json
{
  "provider": {
    "name": "claude",
    "model": "claude-3-5-sonnet-latest"
  }
}
```

An `api_key_environment_variable` is required for the `anthropic` protocol (for example, `ANTHROPIC_API_KEY`).

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
│   ├── config.json
│   └── providers.json
├── .github/
│   └── workflows/
├── scripts/
│   └── security_report.py
├── src/
│   └── aigit/
│       ├── __main__.py
│       ├── cli.py
│       ├── git.py
│       ├── logging_config.py
│       ├── config/
│       │   ├── environment.py
│       │   ├── loader.py
│       │   └── models.py
│       ├── providers/
│       │   ├── anthropic.py
│       │   ├── base.py
│       │   ├── definitions.py
│       │   ├── factory.py
│       │   ├── fake.py
│       │   ├── loader.py
│       │   ├── openai_compatible.py
│       │   └── registry.py
│       └── workflows/
│           └── commit.py
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

- Loading provider definitions from `.aigit/providers.json`
- Selecting the appropriate provider (`ProviderRegistry`) and constructing it (`ProviderFactory`)
- Communication with AI services (`fake`, `openai-compatible`, `anthropic` protocols)
- Generating commit suggestions

The workflow layer handles:

- Git interaction (`GitRepository`)
- Reading staged changes
- Presenting the suggestion and collecting approval, edits, or regeneration requests
- Launching an external editor when the user chooses to edit a message
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

By default this reads `bandit-report.json` and `pip-audit-report.json` from the current directory and writes `security-report.md`. Pass `--bandit`, `--pip-audit`, or `--output` to use different paths.

Generated reports should not be committed.

---

# Repository Tooling

The repository uses:

- Ruff formatting and linting
- Bandit security scanning
- pip-audit dependency scanning
- Gitleaks secret scanning
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
