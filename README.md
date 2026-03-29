# Passphrase Arcana

A passphrase word list built from the vocabularies of authors known for
distinctive, unusual language. Standard passphrase lists (EFF, diceware)
prioritize common, everyday words. This list takes the opposite approach:
words like "sheepfold", "hexapods", and "acridity" are more memorable
precisely because they stand out.

The list is designed for use with [phraze](https://github.com/sts10/phraze)
and other passphrase generators.

## The word list

**`passphrase-arcana.txt`** contains 31,210 lowercase ASCII words, one per
line, ready for use:

```bash
phraze -c passphrase-arcana.txt -w 5 -s -
```

Sample passphrases:

```text
dampish-mclendon-fatalism-pianists-alpacas
jacobs-discovers-relishing-privily-germans
danaher-drawls-fabrics-skis-obduracy
```

## Word list attributes

Analyzed with [wla](https://github.com/sts10/wla):

| Attribute                 | Value           |
| ------------------------- | --------------- |
| Unique words              | 31,210          |
| Free of exact duplicates  | yes             |
| Free of fuzzy duplicates  | yes             |
| No non-ASCII characters   | yes             |
| Unicode normalized        | yes             |
| Free of prefix words      | yes             |
| Free of suffix words      | yes             |
| Uniquely decodable        | yes             |
| Above brute force line    | yes             |
| Shortest word             | 4 characters    |
| Longest word              | 9 characters    |
| Mean word length          | 7.36 characters |
| Entropy per word          | 14.930 bits     |
| Efficiency per character  | 2.028 bits      |
| Shortest edit distance    | 1               |
| Mean edit distance        | 7.018           |
| Unique character prefix   | 9               |
| Kraft-McMillan inequality | satisfied       |

A 4-word passphrase provides ~60 bits of entropy. A 6-word passphrase
provides ~90 bits.

## Sources

Words are drawn from authors with rich, unusual vocabularies. Most are
sourced from Project Gutenberg (public domain texts). Two use concordances
(word frequency data extracted from copyrighted works, which is
non-copyrightable factual data):

| Author              | Works | Source      | Vocabulary              |
| ------------------- | ----- | ----------- | ----------------------- |
| Herman Melville     | 14    | Gutenberg   | Nautical, philosophical |
| H.P. Lovecraft      | 18    | Gutenberg   | Cosmic, eldritch        |
| Joseph Conrad       | 14    | Gutenberg   | Maritime, colonial      |
| James Joyce         | 5     | Gutenberg   | Experimental            |
| Nathaniel Hawthorne | 8     | Gutenberg   | Archaic, allegorical    |
| Mark Twain          | 12    | Gutenberg   | Vernacular, satirical   |
| Lewis Carroll       | 7     | Gutenberg   | Nonsense, mathematical  |
| Oscar Wilde         | 12    | Gutenberg   | Aesthetic, theatrical   |
| William Shakespeare | 1     | Gutenberg   | Early Modern English    |
| Cormac McCarthy     | 16    | Concordance | Archaic, Southwestern   |
| Vladimir Nabokov    | 11    | Concordance | Ornate, precise         |

The Gutenberg texts are in `data/raw/en/`. The McCarthy concordance is
parsed from John Sepich's
[academic word list](http://johnsepich.com/). The Nabokov concordance is
built at fetch time from
[bukvik-workshop-corpora](https://github.com/Cha-OS/bukvik-workshop-corpora)
(texts are streamed and discarded; only word frequencies are kept).

## Processing pipeline

Python scripts, each reading the previous step's output, orchestrated by a
Makefile and run with `uv`:

```text
fetch_texts + fetch_external ->
  extract_words -> validate_words -> score_typing -> build_list
```

### Step 1: Fetch texts

`fetch_texts.py` downloads texts from Project Gutenberg, strips headers
and footers. `fetch_external.py` handles non-Gutenberg sources: it parses
the McCarthy concordance PDF and builds the Nabokov concordance from
streamed GitHub texts. Ebook IDs and external source URLs are configured
in `config.toml`. Rate-limited and idempotent.

### Step 2: Extract words

Lowercases text, tokenizes with a regex (`[a-z]+`), and filters by length
(4 to 9 characters). Tracks word frequency and the number of distinct source
authors per word.

### Step 3: Validate words

Multi-tier dictionary validation. A word passes if it clears any tier:

1. **wordfreq**: `zipf_frequency(word, lang) > 0`
2. **pyspellchecker**: word is in the spellchecker's dictionary
3. **Multi-author heuristic**: word appears in 3+ authors' texts (catches
   archaic and specialized vocabulary that mainstream dictionaries miss,
   which is the point of this list)

### Step 4: Score typing difficulty

A simplified [Carpalx](https://mk.bcgsc.ca/carpalx/?typing_effort)-inspired
model scores each word for QWERTY touch-typing effort. The model combines:

- **Per-key base effort**: finger strength (index through pinky) and row
  distance from the home row
- **Bigram transition effort**: same-finger penalties, inward/outward roll
  bonuses/penalties, hand alternation bonuses

The score is normalized per character. Words above the configured threshold
(default 2.5) are filtered out. The model is also informed by the
[Typability Index](https://pmc.ncbi.nlm.nih.gov/articles/PMC12901113/)
regression trained on 136 million keystrokes.

### Step 5: Build list

1. Filters out offensive words using `blocklist.txt`
2. Removes prefix words (shorter word dropped when it prefixes a longer one)
3. Removes suffix words (same logic, reversed)
4. Outputs the final sorted list to `passphrase-arcana.txt`

## Blocklist

`blocklist.txt` is a merged, deduplicated combination of three profanity
lists:

- [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words)
  (CC-BY-4.0)
- [Google Profanity Words](https://github.com/coffee-and-fun/google-profanity-words)
  (MIT)
- [dsojevic/profanity-list](https://github.com/dsojevic/profanity-list) (MIT)

1,429 terms total. 174 matched and were removed from the word list.

## Generating passphrases

### Installation

```bash
git clone https://github.com/cboone/passphrase-arcana.git
cd passphrase-arcana
make install             # symlinks bin/arcana to ~/.local/bin/
```

The symlink points back to the repo, so the script always finds the word
list. `git pull` updates both. To use a different prefix:

```bash
make install PREFIX=/usr/local
```

To remove:

```bash
make uninstall
```

### Usage

`arcana` generates a passphrase and validates its strength.
Diagnostics go to stderr; the passphrase goes to stdout.

```bash
arcana            # default: 80 bits minimum entropy
arcana 100        # request 100 bits
arcana -c         # copy to clipboard, show diagnostics
arcana -q         # just the passphrase, no diagnostics
arcana -qc        # silently copy to clipboard
arcana | pbcopy   # pipe passphrase, diagnostics visible
```

The script exits 0 on success and 1 if the passphrase is found in the Pwned
Passwords breach database (in which case the passphrase is printed to stderr
only, not to stdout or the clipboard).

### Tools

**Required:**

- [phraze](https://github.com/sts10/phraze): generates the passphrase
  (`cargo install phraze`)

**Recommended** (checks are skipped with a warning when missing):

- [uv](https://docs.astral.sh/uv/) + `zxcvbn-python` (dev dependency):
  pattern-based strength scoring with crack time estimates
- [keepassxc-cli](https://keepassxc.org/): independent entropy estimate with
  per-segment breakdown (`brew install keepassxc` or system package manager)
- `curl` + `shasum`: [Pwned Passwords](https://haveibeenpwned.com/Passwords)
  breach check (both are typically pre-installed)

**For `--copy`** (one of):

| Tool      | Platform | Notes                             |
| --------- | -------- | --------------------------------- |
| `pbcopy`  | macOS    | Built-in                          |
| `wl-copy` | Wayland  | `--sensitive`; skips clip history |
| `xclip`   | X11      | Uses `-selection clipboard`       |
| `xsel`    | X11      | Uses `--clipboard --input`        |

### Security

The passphrase never leaks outside the script:

- It is passed to each tool via stdin using `printf` (a shell builtin), so
  it never appears in process listings.
- The Pwned Passwords check uses
  [k-anonymity](https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#702702420):
  only the first 5 characters of the SHA-1 hash leave the machine.
- On Wayland, `wl-copy --sensitive` hints clipboard managers not to store the
  content in their history.

## Running the pipeline

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync
make all
```

Individual steps:

```bash
make fetch      # download texts (slow, rate-limited)
make extract    # tokenize and filter
make validate   # dictionary verification
make score      # typing difficulty
make build      # final assembly
```

Run tests:

```bash
make test
```

## Configuration

All parameters are in `config.toml`:

- `general.min_word_length` / `max_word_length`: character length bounds
  (default 4-9)
- `typing.max_effort_per_char`: typing difficulty threshold (default 2.5)
- `languages.en.sources`: mapping of author name to Gutenberg ebook IDs
- `languages.en.external`: non-Gutenberg sources (concordance PDFs, GitHub
  corpora)

## License

MIT
