# passphrase-arcana

## Overview

A passphrase word list built from the vocabularies of authors known for distinctive, unusual language.

## Structure

```text
passphrase-arcana/
├── src/                    # Python pipeline scripts
│   ├── fetch_texts.py           # Download texts from Standard Ebooks and Project Gutenberg
│   ├── fetch_external.py        # Parse PDFs and fetch concordances
│   ├── standardebooks.py        # Standard Ebooks fetch and HTML extraction
│   ├── gutenberg.py             # Project Gutenberg fetch and boilerplate stripping
│   ├── extract_words.py         # Tokenize and filter words by length
│   ├── filter_proper_nouns.py   # Remove likely proper nouns via capitalization
│   ├── validate_words.py        # Multi-tier dictionary validation
│   ├── score_typing.py          # QWERTY typing difficulty scoring
│   ├── build_list.py            # Final assembly via tidy (Schlinkert pruning)
│   ├── typing_model.py          # Carpalx-inspired typing effort model
│   └── generate_homophones.py   # One-time CMU dict homophone CSV generation
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
make clean      # Remove intermediate pipeline outputs
```

Dependencies are managed with `uv`. Linting uses `ruff` (configured in `pyproject.toml`). The build step requires [tidy](https://github.com/sts10/tidy) (`cargo install tidy`) for Schlinkert pruning.

## Conventions

- Conventional commits with scopes: `feat(wordlist):`, `feat(sources):`, `refactor(pipeline):`
- Python formatting and linting via ruff
