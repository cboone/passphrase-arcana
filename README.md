# Passphrase Arcana

A passphrase word list built from the vocabularies of authors known for
distinctive, unusual language. Standard passphrase lists
([EFF][eff-dice], [diceware][diceware],
[Orchard Street][orchard-street])
prioritize common, everyday words. This list takes the opposite approach:
words like "sheepfold", "hexapods", and "acridity" are more memorable
precisely because they stand out.

The list is designed for use with [phraze](https://github.com/sts10/phraze)
and other passphrase generators. For lists built from common words instead,
see the [Orchard Street wordlists][orchard-street] (by the same author
as phraze), or the [EFF dice lists][eff-dice].

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

## Typing ease

Every word is scored for QWERTY touch-typing effort using a
[Carpalx][carpalx]-inspired model (see
[Step 4](#step-4-score-typing-difficulty)). Words above the configured
threshold are filtered out. The scores for the 31,210 words in the final
list:

| Statistic       | Effort per character |
| --------------- | -------------------- |
| Minimum         | 1.25                 |
| 10th percentile | 1.63                 |
| 25th percentile | 1.75                 |
| Median          | 1.94                 |
| Mean            | 1.97                 |
| 75th percentile | 2.19                 |
| 90th percentile | 2.36                 |
| Maximum         | 2.50 (threshold)     |

Lower is easier. The scale runs from ~1.0 (home-row keys with hand
alternation) to 2.5 (the configured cutoff). About 44% of words score
below 1.8 (easy range), and 64% below 2.0.

Easiest words tend to use home-row and index-finger keys with hand
alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29).
Hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger
bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Entropy and passphrase length

### How passphrase entropy works

Entropy measures how many guesses an attacker needs to crack a passphrase.
With a known word list, the calculation is:

```text
entropy = num_words x log2(list_size)
```

For this list (31,210 words): **14.93 bits per word**.

| Words | Entropy   | Use case                                    |
| ----- | --------- | ------------------------------------------- |
| 4     | ~60 bits  | Low-value accounts                          |
| 5     | ~75 bits  | Most online accounts                        |
| 6     | ~90 bits  | Important accounts, the `arcana` default    |
| 7     | ~105 bits | High-security accounts, encryption keys     |
| 8     | ~119 bits | Exceeds NIST SP 800-63B highest level (112) |

The `arcana` script defaults to 80 bits minimum entropy, which requires
6 words from this list (6 x 14.93 = 89.6 bits).

### Why phraze and keepassxc-cli report different entropy

Both tools are correct, but they model different attacks:

**phraze** uses word-level entropy: `log2(list_size) x num_words`. This
assumes the attacker knows you are using this specific word list and is
guessing word by word. This is the conservative estimate and the right
threat model for passphrases ([Kerckhoffs's principle][kerckhoffs]:
assume the attacker knows everything about your system except the
passphrase itself).

**keepassxc-cli** uses character-level analysis. It examines the
passphrase as a string of characters, recognizes patterns (dictionary
words, sequences, repeated characters), and estimates entropy from that.
It does not know which word list generated the passphrase, so it applies
a general-purpose model. This often produces a higher number because
character-level brute force against a long passphrase is harder than
word-level guessing against a known list.

**Which to trust:** Use phraze's estimate (the word-level one). It
represents the realistic attack: an adversary who knows you use
passphrase-arcana.txt and is enumerating word combinations. The
keepassxc-cli number is useful as a sanity check, but it overstates
security against a targeted attack.

## Sources

Words are drawn from authors with rich, unusual vocabularies. Most are
sourced from [Project Gutenberg][gutenberg] (public domain texts). Two
use concordances (word frequency data extracted from copyrighted works,
which is non-copyrightable factual data):

| Author                                | Works | Source            | Vocabulary              |
| ------------------------------------- | ----- | ----------------- | ----------------------- |
| [Herman Melville][pg-melville]        | 14    | Project Gutenberg | Nautical, philosophical |
| [H.P. Lovecraft][pg-lovecraft]        | 18    | Project Gutenberg | Cosmic, eldritch        |
| [Joseph Conrad][pg-conrad]            | 14    | Project Gutenberg | Maritime, colonial      |
| [James Joyce][pg-joyce]               | 5     | Project Gutenberg | Experimental            |
| [Nathaniel Hawthorne][pg-hawthorne]   | 8     | Project Gutenberg | Archaic, allegorical    |
| [Mark Twain][pg-twain]                | 12    | Project Gutenberg | Vernacular, satirical   |
| [Lewis Carroll][pg-carroll]           | 7     | Project Gutenberg | Nonsense, mathematical  |
| [Oscar Wilde][pg-wilde]               | 12    | Project Gutenberg | Aesthetic, theatrical   |
| [William Shakespeare][pg-shakespeare] | 1     | Project Gutenberg | Early Modern English    |
| Cormac McCarthy                       | 16    | Concordance       | Archaic, Southwestern   |
| Vladimir Nabokov                      | 11    | Concordance       | Ornate, precise         |

The Project Gutenberg texts are in `data/raw/en/`. The McCarthy
concordance is parsed from John Sepich's
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
and footers. `fetch_external.py` handles non-Project Gutenberg sources: it parses
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
- `languages.en.sources`: mapping of author name to Project Gutenberg ebook IDs
- `languages.en.external`: non-Project Gutenberg sources (concordance PDFs, GitHub
  corpora)

## Other wordlists

This list prioritizes distinctive vocabulary over everyday words. If you
want common, easy-to-spell words instead, these are good alternatives:

| List                                   |  Words | Bits/word | Description                                     |
| -------------------------------------- | -----: | --------: | ----------------------------------------------- |
| **Passphrase Arcana**                  | 31,210 |     14.93 | Literary vocabulary, distinctive words          |
| [Orchard Street Long][os-long]         | 17,576 |     14.10 | Common English from Wikipedia and Google Books  |
| [Orchard Street Medium][os-medium]     |  8,192 |     13.00 | Common English, power-of-2 optimized for phraze |
| [EFF Long][eff-long]                   |  7,776 |     12.93 | Common English, designed for easy spelling      |
| [Orchard Street Diceware][os-diceware] |  7,776 |     12.93 | Common English, diceware-compatible (6^5 words) |
| [Orchard Street QWERTY][os-qwerty]     |  1,296 |     10.34 | Optimized for QWERTY typing ease                |
| [Orchard Street Alpha][os-alpha]       |  1,296 |     10.34 | Alphabetically distinct, for reading aloud      |
| [EFF Short 1][eff-short]               |  1,296 |     10.34 | Short common words                              |

Larger lists need fewer words per passphrase to reach the same entropy.
A 6-word passphrase from the EFF Long list (~78 bits) is roughly
equivalent to a 5-word passphrase from this list (~75 bits).

The [Orchard Street wordlists][orchard-street] are maintained by
[Sam Schlinkert](https://github.com/sts10), who also created
[phraze](https://github.com/sts10/phraze).

## License

MIT

<!-- Reference links -->

[eff-dice]: https://www.eff.org/dice
[eff-long]: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
[eff-short]: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
[diceware]: https://theworld.com/~reinhold/diceware.html
[orchard-street]: https://github.com/sts10/orchard-street-wordlists
[os-long]: https://github.com/sts10/orchard-street-wordlists/blob/main/lists/orchard-street-long.txt
[os-medium]: https://github.com/sts10/orchard-street-wordlists/blob/main/lists/orchard-street-medium.txt
[os-diceware]: https://github.com/sts10/orchard-street-wordlists/blob/main/lists/orchard-street-diceware.txt
[os-qwerty]: https://github.com/sts10/orchard-street-wordlists/blob/main/lists/orchard-street-qwerty.txt
[os-alpha]: https://github.com/sts10/orchard-street-wordlists/blob/main/lists/orchard-street-alpha.txt
[gutenberg]: https://www.gutenberg.org/
[pg-melville]: https://www.gutenberg.org/ebooks/author/9
[pg-lovecraft]: https://www.gutenberg.org/ebooks/author/34724
[pg-conrad]: https://www.gutenberg.org/ebooks/author/125
[pg-joyce]: https://www.gutenberg.org/ebooks/author/1039
[pg-hawthorne]: https://www.gutenberg.org/ebooks/author/28
[pg-twain]: https://www.gutenberg.org/ebooks/author/53
[pg-carroll]: https://www.gutenberg.org/ebooks/author/7
[pg-wilde]: https://www.gutenberg.org/ebooks/author/111
[pg-shakespeare]: https://www.gutenberg.org/ebooks/author/65
[carpalx]: https://mk.bcgsc.ca/carpalx/?typing_effort
[kerckhoffs]: https://en.wikipedia.org/wiki/Kerckhoffs%27s_principle
