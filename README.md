# Word Lists

A passphrase word list built from the vocabularies of authors known for
distinctive, unusual language. Standard passphrase lists (EFF, diceware)
prioritize common, everyday words. This list takes the opposite approach:
words like "sheepfold", "hexapods", and "acridity" are more memorable
precisely because they stand out.

The list is designed for use with [phraze](https://github.com/sts10/phraze)
and other passphrase generators.

## The word list

**`output/word-list.txt`** contains 24,168 lowercase ASCII words, one per
line, ready for use:

```bash
phraze -c output/word-list.txt -w 5 -s -
```

Sample passphrases:

```text
premisses-morocco-textured-impotent-saratoga
sheepfold-hexapods-thrifty-ibsen-resulted
palette-availing-acridity-nilus-keenest
```

## Word list attributes

Analyzed with [wla](https://github.com/sts10/wla):

| Attribute                 | Value           |
| ------------------------- | --------------- |
| Unique words              | 24,168          |
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
| Entropy per word          | 14.561 bits     |
| Efficiency per character  | 1.979 bits      |
| Shortest edit distance    | 1               |
| Mean edit distance        | 7.001           |
| Unique character prefix   | 9               |
| Kraft-McMillan inequality | satisfied       |

A 4-word passphrase provides ~58 bits of entropy. A 6-word passphrase
provides ~87 bits.

## Sources

Words are extracted from Project Gutenberg texts by authors with rich,
unusual vocabularies:

| Author              | Works | Notable vocabulary                     |
| ------------------- | ----- | -------------------------------------- |
| Herman Melville     | 14    | Nautical, archaic, philosophical       |
| H.P. Lovecraft      | 18    | Cosmic horror, pseudo-scientific       |
| Joseph Conrad       | 14    | Maritime, colonial, psychological      |
| James Joyce         | 5     | Experimental, multilingual, neologisms |
| Nathaniel Hawthorne | 8     | Archaic New England, allegorical       |
| Mark Twain          | 12    | Vernacular, satirical, regional        |
| Lewis Carroll       | 7     | Nonsense, mathematical, invented       |
| Oscar Wilde         | 12    | Aesthetic, epigrammatic, theatrical    |

90 texts total. The raw texts are included in `data/raw/en/`.

## Processing pipeline

Five Python scripts, each reading the previous step's output, orchestrated
by a Makefile and run with `uv`:

```text
fetch_texts -> extract_words -> validate_words -> score_typing -> build_list
```

### Step 1: Fetch texts

Downloads texts from Project Gutenberg, strips headers and footers. Ebook
IDs are configured in `config.toml`. Rate-limited and idempotent.

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
4. Outputs the final sorted list to `output/word-list.txt`

## Blocklist

`blocklist.txt` is a merged, deduplicated combination of three profanity
lists:

- [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words)
  (CC-BY-4.0)
- [Google Profanity Words](https://github.com/coffee-and-fun/google-profanity-words)
  (MIT)
- [dsojevic/profanity-list](https://github.com/dsojevic/profanity-list) (MIT)

1,429 terms total. 113 matched and were removed from the word list.

## Generating passphrases

`bin/generate-passphrase` generates a passphrase and validates its strength
using multiple tools:

```bash
bin/generate-passphrase        # default: 80 bits minimum entropy
bin/generate-passphrase 100    # 100 bits minimum entropy
```

It runs [phraze](https://github.com/sts10/phraze) to generate the passphrase,
then checks it against:

- [zxcvbn](https://github.com/dropbox/zxcvbn) for pattern-based strength
  scoring and crack time estimates
- [KeePassXC](https://keepassxc.org/) (`keepassxc-cli estimate --advanced`)
  for an independent entropy estimate with per-segment breakdown
- [Pwned Passwords](https://haveibeenpwned.com/Passwords) to confirm the
  passphrase has not appeared in known breaches

The passphrase never leaks outside the script: it is passed to each tool via
stdin (using `printf`, a shell builtin, so it never appears in process
listings), and the Pwned Passwords check uses
[k-anonymity](https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#702702420)
(only the first 5 characters of the SHA-1 hash leave the machine).

Requires `phraze`, `keepassxc-cli`, and `uv` (which provides `zxcvbn-python`
from the project's dev dependencies).

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

## License

MIT
