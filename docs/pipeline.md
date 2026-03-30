# Processing pipeline

Python scripts, each reading the previous step's output, orchestrated by a Makefile and run with `uv`:

```text
fetch_texts + fetch_external ->
  extract_words -> filter_proper_nouns -> validate_words -> score_typing -> build_list
```

## Step 1: Fetch texts

`fetch_texts.py` downloads texts from Project Gutenberg, strips headers and footers. `fetch_external.py` handles non-Project Gutenberg sources: it parses the McCarthy concordance PDF and builds the Nabokov concordance from streamed GitHub texts. Ebook IDs and external source URLs are configured in `config.toml`.

Both scripts are idempotent: they check whether each file already exists and skip the download if so. Running `make fetch` (or `make all`) on a populated `data/raw/` directory completes instantly. Only `make clean` removes the cached files, triggering fresh downloads on the next run.

The Nabokov concordance build filters likely proper nouns during generation by scanning the original mixed-case text for words that never appear in lowercase form. An unfiltered version is preserved in `data/reference/` for inspection.

## Step 2: Extract words

Lowercases text, tokenizes with a regex (`[a-z]+`), and filters by length (4 to 9 characters). Tracks word frequency and the number of distinct source authors per word.

## Step 3: Filter proper nouns

Best-effort removal of likely proper nouns from Project Gutenberg sources. Scans the raw text files (which preserve original capitalization) for words that never appear in lowercase form. Words like "whale" appear lowercase thousands of times and are kept; words like "Ahab" that only appear capitalized are removed.

Concordance-sourced words are already filtered during generation (Step 1 for Nabokov) or are naturally lowercase (McCarthy PDF extraction). The filter writes removed words to `data/words/{lang}/proper_nouns_removed.txt` for manual inspection.

## Step 4: Validate words

Multi-tier dictionary validation. A word passes if it clears any tier:

1. **wordfreq**: `zipf_frequency(word, lang) > 0`
2. **pyspellchecker**: word is in the spellchecker's dictionary
3. **Multi-author heuristic**: word appears in 3+ authors' texts (catches archaic and specialized vocabulary that mainstream dictionaries miss, which is the point of this list)

## Step 5: Score typing difficulty

A simplified [Carpalx](https://mk.bcgsc.ca/carpalx/?typing_effort)-inspired model scores each word for QWERTY touch-typing effort. The model combines:

- **Per-key base effort**: finger strength (index through pinky) and row distance from the home row
- **Bigram transition effort**: same-finger penalties, inward/outward roll bonuses/penalties, hand alternation bonuses

The score is normalized per character. Words above the configured threshold (default 2.5) are filtered out. The model is also informed by the [Typability Index](https://pmc.ncbi.nlm.nih.gov/articles/PMC12901113/) regression trained on 136 million keystrokes.

## Step 6: Build list

1. Filters out offensive words using `blocklist.txt`
2. Removes prefix words (shorter word dropped when it prefixes a longer one)
3. Removes suffix words (same logic, reversed)
4. Outputs the final sorted list to `passphrase-arcana.txt`

## Blocklist

`blocklist.txt` is a merged, deduplicated combination of three profanity lists:

- [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words) (CC-BY-4.0)
- [Google Profanity Words](https://github.com/coffee-and-fun/google-profanity-words) (MIT)
- [dsojevic/profanity-list](https://github.com/dsojevic/profanity-list) (MIT)

1,429 terms total. 166 matched and were removed from the word list.

## Running the pipeline

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync
make all
```

Individual steps:

```bash
make fetch                # download texts (slow first run, cached after)
make extract              # tokenize and filter
make filter-proper-nouns  # remove likely proper nouns
make validate             # dictionary verification
make score                # typing difficulty
make build                # final assembly
```

Run tests:

```bash
make test
```

## Configuration

All parameters are in `config.toml`:

- `general.min_word_length` / `max_word_length`: character length bounds (default 4-9)
- `typing.max_effort_per_char`: typing difficulty threshold (default 2.5)
- `languages.en.sources`: mapping of author name to Project Gutenberg ebook IDs
- `languages.en.external`: non-Project Gutenberg sources (concordance PDFs, GitHub corpora)
