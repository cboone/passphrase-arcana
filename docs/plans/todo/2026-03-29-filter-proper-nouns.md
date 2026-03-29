# Filter proper nouns from word list

## Context

The extract step lowercases all text before tokenizing, so proper nouns like "Ahab", "Starbuck", and "Jacobs" enter the pipeline as lowercase words. This adds character names, place names, and other proper nouns to the final word list. Adding best-effort filtering will improve list quality.

## Approach

New script `src/filter_proper_nouns.py` as a pipeline step between extract and validate.

**Heuristic:** A word is likely a proper noun if it never appears in lowercase form in any raw text file. The raw files in `data/raw/{lang}/` preserve original capitalization. Common words like "whale" appear lowercase thousands of times and are kept. Words like "Ahab" only appear capitalized and are removed.

Concordance-sourced files (McCarthy, Nabokov) are already all-lowercase, so every concordance word passes the filter automatically. This is an accepted limitation.

## Files to create

### `src/filter_proper_nouns.py`

Two functions plus `main()`:

- `scan_lowercase_tokens(raw_dir: Path, min_len: int, max_len: int) -> set[str]`: Scan all `*.txt` files in `raw_dir`, find tokens matching `[a-z]+` in the original text (already lowercase in source), return the set.

- `filter_csv(csv_path: Path, seen_lowercase: set[str]) -> tuple[list[str], list[str]]`: Read `word_frequencies.csv`, partition into kept (word in `seen_lowercase`) and removed. Return `(kept_words, removed_words)`.

- `main()`: Load config, iterate languages, scan raw dir, filter CSV, rewrite `word_frequencies.csv` and `all_words.txt` with only kept words, write `proper_nouns_removed.txt` for inspection, print stats.

Follows existing conventions: `ROOT`, `CONFIG`, `DATA_RAW`, `DATA_WORDS` constants, `tomllib` for config, print in `[{lang_name}]` format.

### `tests/test_filter_proper_nouns.py`

Test `scan_lowercase_tokens` with synthetic text files and `filter_csv` with synthetic CSVs using `tmp_path` fixture.

## Files to modify

### `Makefile`

- Add `filter-nouns` to `.PHONY` line
- Add target: `filter-nouns: extract` -> `uv run src/filter_proper_nouns.py`
- Change `validate: extract` to `validate: filter-nouns`

### `README.md`

- Update pipeline diagram to include `filter_proper_nouns`
- Renumber steps (current 3-5 become 4-6)
- Insert new "Step 3: Filter proper nouns" section
- Add `make filter-nouns` to the individual steps list

### `AGENTS.md`

- Add `filter_proper_nouns.py` to the file tree

## Verification

1. `make test` to verify new and existing tests pass
2. `make extract filter-nouns` and inspect `data/words/en/proper_nouns_removed.txt`
3. Spot-check: "ahab", "starbuck", "queequeg" should be in removed list
4. Spot-check: "whale", "darkness", "eldritch" should NOT be in removed list
5. `make all` end-to-end to produce a valid final word list
6. Run linters via `make lint` and `make fmt`
