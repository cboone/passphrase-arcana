# passphrase-arcana

## Overview

A passphrase word list built from the vocabularies of authors known for distinctive, unusual language, plus a CLI tool for generating passphrases from it.

## Structure

```text
passphrase-arcana/
├── bin/arcana              # Bash CLI for generating passphrases (wraps phraze)
├── src/                    # Python pipeline scripts
│   ├── fetch_texts.py      # Download texts from Project Gutenberg
│   ├── fetch_external.py   # Parse PDFs and fetch concordances
│   ├── extract_words.py         # Tokenize and filter words by length
│   ├── filter_proper_nouns.py   # Remove likely proper nouns via capitalization
│   ├── validate_words.py        # Multi-tier dictionary validation
│   ├── score_typing.py     # QWERTY typing difficulty scoring
│   ├── build_list.py       # Final assembly and blocklist filtering
│   └── typing_model.py     # Carpalx-inspired typing effort model
├── tests/                  # pytest test suite
├── data/                   # Pipeline input/output data
├── config.toml             # Pipeline configuration
├── pyproject.toml          # Python project metadata and dependencies
├── Makefile                # Build orchestration
└── passphrase-arcana.txt   # Generated word list
```

## Development

```bash
make            # Run the full pipeline (fetch, extract, validate, score, build)
make test       # Run pytest
make install    # Symlink bin/arcana to ~/.local/bin/
make clean      # Remove intermediate pipeline outputs
```

Dependencies are managed with `uv`. Linting uses `ruff` (configured in `pyproject.toml`). The build step requires [tidy](https://github.com/sts10/tidy) (`cargo install tidy`) for Schlinkert pruning.

## Conventions

- Conventional commits with scopes: `feat(wordlist):`, `fix(cli):`, `refactor(pipeline):`
- Single version number for the whole repo (word list + CLI ship together)
- Python formatting and linting via ruff

## Design decisions

### arcana stdin security model

The arcana script pipes the passphrase into every tool via stdin (`printf '%s' "$passphrase" | tool`), never as a CLI argument. `printf` is a shell builtin and invisible to `ps`. This is why we use `uv run python3` for zxcvbn and `curl+shasum` for Pwned Passwords instead of the `zxcvbn-cli` and `pwned pw` CLIs, which take the password as an argument and briefly expose it in process listings. Do not replace these with the CLI equivalents without solving the stdin issue first.
