# Bootstrap Project: passphrase-arcana

## Context

passphrase-arcana is a Python 3.11+ project with a Bash CLI wrapper (`bin/arcana`). It has a solid local development setup (Makefile, uv, pytest, ruff) but lacks DevOps infrastructure, agent configuration, community files, and secret scanning. This plan adds those missing pieces and establishes conventions for release management.

## Project Detection

- **Type:** Python data-processing pipeline + Bash CLI tool
- **Package manager:** uv
- **Linter:** ruff (configured in `pyproject.toml`)
- **Tests:** pytest (`tests/`)
- **Build:** Makefile (fetch, extract, validate, score, build, install, test)

## Release Management Decisions

- **Single version** for the whole repo (word list + CLI script ship together)
- **Conventional commits with scopes**: `feat(wordlist):`, `fix(cli):`, etc.
- **Release skill** handles changelog generation, version bumping, tagging, and GitHub Releases (no git-cliff needed)
- CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/) format
- Version tracked in `pyproject.toml` `[project].version`

## Existing Infrastructure

| Item                       | Status                                |
| -------------------------- | ------------------------------------- |
| LICENSE (MIT)              | Exists                                |
| README.md                  | Exists                                |
| .gitignore                 | Exists                                |
| Makefile                   | Exists                                |
| pyproject.toml             | Exists                                |
| config.toml                | Exists                                |
| tests/ (pytest)            | Exists                                |
| CHANGELOG.md               | Missing                               |
| AGENTS.md / CLAUDE.md      | Missing                               |
| .claude/settings.json      | Missing                               |
| .github/workflows/         | Missing                               |
| Linter config (standalone) | Missing (ruff in pyproject.toml only) |
| Secret scanning            | Missing                               |
| Community files            | Missing                               |

## Bootstrap Plan

| #   | Tool                    | Status         | What it does                                                                                               |
| --- | ----------------------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | scaffold-new-repo       | Scoped down    | Agent config (AGENTS.md, CLAUDE.md, .claude/settings.json, .github/copilot-instructions.md) + CHANGELOG.md |
| 2   | setup-ci                | Will run       | GitHub Actions CI workflow (uv, pytest, ruff)                                                              |
| 3   | setup-linters           | Scoped down    | Cross-language tools only (EditorConfig, Prettier, markdownlint); ruff already handles Python              |
| 4   | setup-secret-scanning   | Will run       | Gitleaks + TruffleHog GitHub Actions workflows                                                             |
| 5   | add-community-files     | Will run       | CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, PR template                                              |
| 6   | scaffold-go-cli         | Not applicable | Python project                                                                                             |
| 7   | add-goreleaser-homebrew | Not applicable | Not a Go project                                                                                           |
| 8   | setup-installers        | Not applicable | Bash script, not a compiled binary                                                                         |
| 9   | add-scrut-cli-tests     | Skipped        | bin/arcana depends on external tools (phraze, keepassxc-cli) that complicate testing                       |

## Execution Order

1. `scaffold-new-repo` (scoped down: agent config + CHANGELOG only)
2. `setup-ci` (Python CI workflow)
3. `setup-linters` (scoped down: cross-language tools only)
4. `setup-secret-scanning`
5. `add-community-files`

## Verification

- Run `make test` to confirm existing pytest tests still pass
- Run linters via `lint-and-fix` to verify linter setup
- Inspect `.github/workflows/` for correct CI, secret scanning workflows
- Verify agent config files are present and well-formed
- Confirm `pyproject.toml` has a `version` field the release skill can detect
