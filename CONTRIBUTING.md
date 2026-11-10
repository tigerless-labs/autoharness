# First-Contribution Guide (CONTRIBUTING.md)

Welcome to AutoHarness! This guide helps first-time contributors get set up and submit their first pull request.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Running Tests](#running-tests)
- [First Pull Request Checklist](#first-pull-request-checklist)
- [License](#license)

## 🛠️ Getting Started

### Requirements

- **Python 3.11+** — autoharness runs entirely as Python (zero third-party dependencies). The hooks resolve bare `python3`, so an older interpreter earlier on your PATH (Xcode ships 3.9.6 at `/usr/bin/python3`) turns every hook off for the session.

### Installation

```bash
# 1. Install as a Claude Code plugin (recommended)
claude plugin marketplace add tigerless-labs/autoharness
claude plugin install autoharness@autoharness

# 2. Refresh the catalog and update
claude plugin marketplace update autoharness
claude plugin update autoharness@autoharness

# 3. Restart Claude Code to apply

# Or install locally (for development)
python3 -m pip install -e .
```

### Configuration

Every knob is an `AUTOHARNESS_*` environment variable with a built-in default — nothing to configure unless you want to change the pace.

## 🧪 Running Tests

### Offline Tests (no model account needed)

```bash
python3 -m pytest -m "not live" -q
```

This runs the test suite excluding any tests marked as `live` (which require a Claude Code host). An empty collection is tolerated in CI, but locally you should see tests run.

### Lint

```bash
ruff check .
```

This repo uses Ruff with the following lint rules enabled (per `ruff.toml`):

- `E4` — literal computation
- `E7` — assignment to conditional
- `E9` — syntax warnings
- `F` — flakes
- `I` — import sorting
- `UP` — pyupgrade
- `B` — bugbear

### Live Tests (requires Claude Code host)

```bash
python3 -m pytest -q
```

These tests require an active Claude Code host and are excluded from CI via the `not live` marker.

## 📁 Project Structure

### Key Directories

- **`src/autoharness/`** — Core source code (the main package)
- **`tests/`** — Test suite (offline-capable, with `live` marker for host-dependent tests)
- **`skills/`** — Sample skills contributed by the community
- **`docs/`** — Documentation and references
- **`hooks/`** — Claude Code plugin hooks
- **`.github/workflows/`** — CI workflows (lint + test matrix)
- **`README.md`** — Project overview; **link your contribution guide from here**

### Good First Contribution Areas

- **Documentation** — Expanding the `README.md`, adding examples, improving tutorials
- **Tests** — Adding new test cases, especially offline tests that don't require a model account
- **Bug fixes** — Addressing issues labeled `good first issue` or `bug`
- **New skills** — Creating sample skills following the pattern in `skills/`

## 📬 First Pull Request Checklist

Before opening a PR, ensure the following:

- [ ] The change is described clearly in the PR title and body
- [ ] You have read the [issue](https://github.com/tigerless-labs/autoharness/issues/281) (or created one if filing a new bug/feature)
- [ ] You have [run the offline tests](#running-tests) and they pass
- [ ] You have [run the linter](#running-tests) and it passes
- [ ] Your change is **documentation-only** or **does not alter runtime behavior, defaults, or core workflows** (per acceptance criteria)
- [ ] You have [added yourself to the PR body] (`@Yi-111-a` or maintainer handle) for review
- [ ] The PR follows the [PULL_REQUEST_TEMPLATE](https://github.com/tigerless-labs/autoharness/.github/pull_request_template.md) if one exists

### Acceptance Criteria

1. The documented requirements, commands, and paths match the repository configuration.
2. First-time contributors can run the offline tests without a model account or API credentials.
3. Links work, steps are reproducible, and the guide is concise and easy to follow.
4. The change is documentation-only and does not alter runtime behavior, defaults, or core workflows.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Found a issue?** Please [open an issue](https://github.com/tigerless-labs/autoharness/issues) or [submit a pull request](https://github.com/tigerless-labs/autoharness/pulls).