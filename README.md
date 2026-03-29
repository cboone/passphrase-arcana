# Passphrase Arcana

A passphrase word list built from the vocabularies of authors known for distinctive, unusual language. Standard passphrase lists ([EFF][eff-dice], [diceware][diceware], [Orchard Street][orchard-street]) prioritize common, everyday words. This list takes the opposite approach: words like "sheepfold", "hexapods", and "acridity" are more memorable precisely because they stand out.

The list is designed for use with [phraze](https://github.com/sts10/phraze) and other passphrase generators. For lists built from common words instead, see the [Orchard Street wordlists][orchard-street] (by the same author as phraze), or the [EFF dice lists][eff-dice].

[The word list](#the-word-list)
[Generating passphrases](#generating-passphrases)
[Word list attributes](#word-list-attributes)
[Typing ease](#typing-ease)
[Entropy and passphrase length](#entropy-and-passphrase-length)
[Sources](#sources)
[Processing pipeline](#processing-pipeline)
[Blocklist](#blocklist)
[Running the pipeline](#running-the-pipeline)
[Configuration](#configuration)
[Other wordlists](#other-wordlists)

## The word list

**`passphrase-arcana.txt`** contains 27,445 lowercase ASCII words, one per line, ready for use with phraze or any passphrase generator:

```bash
phraze --verbose --sep " " --custom-list passphrase-arcana.txt --minimum-entropy 80
```

Sample passphrases:

```text
nocturnes wornout lamenting jars morels prominent
artlessly luckier pursed chimiques movers childbed
makeup withdraws beseems seraglios federals waxen
```

## Generating passphrases

### Installation

```bash
git clone https://github.com/cboone/passphrase-arcana.git
cd passphrase-arcana
make install             # symlinks bin/arcana to ~/.local/bin/
```

The symlink points back to the repo, so the script always finds the word list. `git pull` updates both. To use a different prefix:

```bash
make install PREFIX=/usr/local
```

To remove:

```bash
make uninstall
```

### Usage

`arcana` generates a passphrase and validates its strength. Diagnostics go to stderr; the passphrase goes to stdout.

```bash
arcana            # default: 80 bits minimum entropy
arcana 100        # request 100 bits
arcana -c         # copy to clipboard, show diagnostics
arcana -q         # just the passphrase, no diagnostics
arcana -qc        # silently copy to clipboard
arcana | pbcopy   # pipe passphrase, diagnostics visible
```

The script exits 0 on success and 1 if the passphrase is found in the Pwned Passwords breach database (in which case the passphrase is printed to stderr only, not to stdout or the clipboard).

### Tools

**Required:**

- [phraze](https://github.com/sts10/phraze): generates the passphrase (`cargo install phraze`)

**Recommended** (checks are skipped with a warning when missing):

- [uv](https://docs.astral.sh/uv/) + `zxcvbn-python` (dev dependency): pattern-based strength scoring with crack time estimates
- [keepassxc-cli](https://keepassxc.org/): independent entropy estimate with per-segment breakdown (`brew install keepassxc` or system package manager)
- `curl` + `shasum`: [Pwned Passwords](https://haveibeenpwned.com/Passwords) breach check (both are typically pre-installed)

**For `--copy`** (one of):

| Tool      | Platform | Notes                             |
| --------- | -------- | --------------------------------- |
| `pbcopy`  | macOS    | Built-in                          |
| `wl-copy` | Wayland  | `--sensitive`; skips clip history |
| `xclip`   | X11      | Uses `-selection clipboard`       |
| `xsel`    | X11      | Uses `--clipboard --input`        |

### Security

The passphrase never leaks outside the script:

- It is passed to each tool via stdin using `printf` (a shell builtin), so it never appears in process listings.
- The Pwned Passwords check uses [k-anonymity](https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#702702420): only the first 5 characters of the SHA-1 hash leave the machine.
- On Wayland, `wl-copy --sensitive` hints clipboard managers not to store the content in their history.

## Word list attributes

Analyzed with [wla](https://github.com/sts10/wla):

| Attribute                 | Value           |
| ------------------------- | --------------- |
| Unique words              | 27,445          |
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
| Mean word length          | 7.40 characters |
| Entropy per word          | 14.744 bits     |
| Efficiency per character  | 1.993 bits      |
| Shortest edit distance    | 1               |
| Mean edit distance        | 7.018           |
| Unique character prefix   | 9               |
| Kraft-McMillan inequality | satisfied       |

A 4-word passphrase provides ~59 bits of entropy. A 6-word passphrase provides ~88 bits.

## Typing ease

Every word is scored for QWERTY touch-typing effort using a [Carpalx][carpalx]-inspired model (see [Step 5](#step-5-score-typing-difficulty)). Words above the configured threshold are filtered out. The scores for the 27,445 words in the final list:

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

Lower is easier. The scale runs from ~1.0 (home-row keys with hand alternation) to 2.5 (the configured cutoff). About 33% of words score below 1.8 (easy range), and 56% below 2.0.

Easiest words tend to use home-row and index-finger keys with hand alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29). Hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Entropy and passphrase length

### How passphrase entropy works

Entropy measures how many guesses an attacker needs to crack a passphrase. With a known word list, the calculation is:

```text
entropy = num_words x log2(list_size)
```

For this list (27,445 words): **14.74 bits per word**.

| Words | Entropy   | Length | Use case                                    |
| ----- | --------- | ------ | ------------------------------------------- |
| 4     | ~59 bits  | ~33 ch | Low-value accounts                          |
| 5     | ~74 bits  | ~41 ch | Most online accounts                        |
| 6     | ~88 bits  | ~49 ch | Important accounts, the `arcana` default    |
| 7     | ~103 bits | ~58 ch | High-security accounts, encryption keys     |
| 8     | ~118 bits | ~66 ch | Exceeds NIST SP 800-63B highest level (112) |

Length assumes space separators and the list's mean word length of 7.4 characters.

The `arcana` script defaults to 80 bits minimum entropy, which requires 6 words from this list (6 x 14.74 = 88.4 bits).

### Kerckhoffs's principle

The entropy calculation above assumes the attacker knows which word list you are using. This follows [Kerckhoffs's principle][kerckhoffs], a foundational concept in cryptography: a system should remain secure even if everything about it is public knowledge except the secret itself. For passphrases, this means assuming the attacker knows:

- That you are using a word-based passphrase
- Which word list you drew from
- How many words you chose
- The separator character

The only secret is _which specific words_ were randomly selected. This is the correct, conservative way to evaluate passphrase strength. A passphrase that is only secure because the attacker does not know your word list is not secure at all, because you cannot control what an attacker knows.

### Why phraze and keepassxc-cli report different entropy

Both tools are correct, but they model different attacks:

**phraze** uses word-level entropy: `log2(list_size) x num_words`. This assumes the attacker knows your word list and is guessing word by word (Kerckhoffs's principle, as described above).

**keepassxc-cli** uses character-level analysis. It examines the passphrase as a string of characters, recognizes patterns (dictionary words, sequences, repeated characters), and estimates entropy from that. It does not know which word list generated the passphrase, so it applies a general-purpose model. This often produces a higher number because character-level brute force against a long passphrase is harder than word-level guessing against a known list.

**Which to trust:** Use phraze's estimate (the word-level one). It represents the realistic attack: an adversary who knows you use passphrase-arcana.txt and is enumerating word combinations. The keepassxc-cli number is useful as a sanity check, but it overstates security against a targeted attack.

### Other passphrase testing tools

The `arcana` script runs three independent checks. Each evaluates passphrase strength from a different angle:

| Tool                         | What it measures                               | Install                           |
| ---------------------------- | ---------------------------------------------- | --------------------------------- |
| [phraze][phraze]             | Word-level entropy from list size              | `cargo install phraze`            |
| [zxcvbn][zxcvbn]             | Pattern-based guessability and crack time      | `uv sync --extra dev`             |
| [keepassxc-cli][keepassxc]   | Character-level entropy with segment breakdown | `brew install keepassxc`          |
| [Pwned Passwords][pwned-api] | Breach database lookup (k-anonymity)           | `curl` + `shasum` (pre-installed) |

**phraze** provides the entropy figure you should rely on for passphrase security. It calculates entropy from the word list size and word count.

**zxcvbn** (by Dropbox) takes a different approach: it models how a real-world attacker cracks passwords by recognizing patterns like dictionary words, keyboard walks, dates, and common substitutions. It reports a 0-4 score, estimated guess count, and crack times at various attack speeds (online throttled, offline slow hash, offline fast hash). For passphrases from a curated list, zxcvbn tends to underestimate strength because it matches individual words against its internal dictionaries rather than considering the combinatorial word list space.

**keepassxc-cli** estimates entropy per character segment and totals them. Useful for seeing which parts of a passphrase contribute most to its strength, but the total typically overstates security against a word-list-aware attacker (see [Why phraze and keepassxc-cli report different entropy](#why-phraze-and-keepassxc-cli-report-different-entropy) above).

**Pwned Passwords** checks whether the exact passphrase appears in known data breaches. It uses [k-anonymity][k-anonymity]: only the first 5 characters of the SHA-1 hash leave the machine, so the passphrase is never exposed to the API. A match does not mean the passphrase was _yours_, just that someone has used the same string before.

## Sources

Words are drawn from authors with rich, unusual vocabularies. Most are sourced from [Project Gutenberg][gutenberg] (public domain texts). Two use concordances (word frequency data extracted from copyrighted works, which is non-copyrightable factual data):

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

The Project Gutenberg texts are in `data/raw/en/`. The McCarthy concordance is parsed from John Sepich's [academic word list](http://johnsepich.com/). The Nabokov concordance is built at fetch time from [bukvik-workshop-corpora](https://github.com/Cha-OS/bukvik-workshop-corpora) (texts are streamed and discarded; only word frequencies are kept).

## Processing pipeline

Python scripts, each reading the previous step's output, orchestrated by a Makefile and run with `uv`:

```text
fetch_texts + fetch_external ->
  extract_words -> filter_proper_nouns -> validate_words -> score_typing -> build_list
```

### Step 1: Fetch texts

`fetch_texts.py` downloads texts from Project Gutenberg, strips headers and footers. `fetch_external.py` handles non-Project Gutenberg sources: it parses the McCarthy concordance PDF and builds the Nabokov concordance from streamed GitHub texts. Ebook IDs and external source URLs are configured in `config.toml`.

Both scripts are idempotent: they check whether each file already exists and skip the download if so. Running `make fetch` (or `make all`) on a populated `data/raw/` directory completes instantly. Only `make clean` removes the cached files, triggering fresh downloads on the next run.

### Step 2: Extract words

Lowercases text, tokenizes with a regex (`[a-z]+`), and filters by length (4 to 9 characters). Tracks word frequency and the number of distinct source authors per word.

### Step 3: Filter proper nouns

Best-effort removal of likely proper nouns. Scans the raw text files (which preserve original capitalization) for words that never appear in lowercase form. Words like "whale" appear lowercase thousands of times and are kept; words like "Ahab" that only appear capitalized are removed.

Concordance-sourced words (McCarthy, Nabokov) are already entirely lowercase in the raw files, so they pass the filter automatically. The filter writes removed words to `data/words/{lang}/proper_nouns_removed.txt` for manual inspection.

### Step 4: Validate words

Multi-tier dictionary validation. A word passes if it clears any tier:

1. **wordfreq**: `zipf_frequency(word, lang) > 0`
2. **pyspellchecker**: word is in the spellchecker's dictionary
3. **Multi-author heuristic**: word appears in 3+ authors' texts (catches archaic and specialized vocabulary that mainstream dictionaries miss, which is the point of this list)

### Step 5: Score typing difficulty

A simplified [Carpalx](https://mk.bcgsc.ca/carpalx/?typing_effort)-inspired model scores each word for QWERTY touch-typing effort. The model combines:

- **Per-key base effort**: finger strength (index through pinky) and row distance from the home row
- **Bigram transition effort**: same-finger penalties, inward/outward roll bonuses/penalties, hand alternation bonuses

The score is normalized per character. Words above the configured threshold (default 2.5) are filtered out. The model is also informed by the [Typability Index](https://pmc.ncbi.nlm.nih.gov/articles/PMC12901113/) regression trained on 136 million keystrokes.

### Step 6: Build list

1. Filters out offensive words using `blocklist.txt`
2. Removes prefix words (shorter word dropped when it prefixes a longer one)
3. Removes suffix words (same logic, reversed)
4. Outputs the final sorted list to `passphrase-arcana.txt`

## Blocklist

`blocklist.txt` is a merged, deduplicated combination of three profanity lists:

- [LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words) (CC-BY-4.0)
- [Google Profanity Words](https://github.com/coffee-and-fun/google-profanity-words) (MIT)
- [dsojevic/profanity-list](https://github.com/dsojevic/profanity-list) (MIT)

1,429 terms total. 167 matched and were removed from the word list.

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

## Other wordlists

This list prioritizes distinctive vocabulary over everyday words. If you want common, easy-to-spell words instead, these are good alternatives:

| List                                   |  Words | Bits/word | Description                                     |
| -------------------------------------- | -----: | --------: | ----------------------------------------------- |
| **Passphrase Arcana**                  | 27,445 |     14.74 | Literary vocabulary, distinctive words          |
| [Orchard Street Long][os-long]         | 17,576 |     14.10 | Common English from Wikipedia and Google Books  |
| [Orchard Street Medium][os-medium]     |  8,192 |     13.00 | Common English, power-of-2 optimized for phraze |
| [EFF Long][eff-long]                   |  7,776 |     12.93 | Common English, designed for easy spelling      |
| [Orchard Street Diceware][os-diceware] |  7,776 |     12.93 | Common English, diceware-compatible (6^5 words) |
| [Orchard Street QWERTY][os-qwerty]     |  1,296 |     10.34 | Optimized for QWERTY typing ease                |
| [Orchard Street Alpha][os-alpha]       |  1,296 |     10.34 | Alphabetically distinct, for reading aloud      |
| [EFF Short 1][eff-short]               |  1,296 |     10.34 | Short common words                              |

Larger lists need fewer words per passphrase to reach the same entropy. A 6-word passphrase from the EFF Long list (~78 bits) is roughly equivalent to a 5-word passphrase from this list (~74 bits).

The [Orchard Street wordlists][orchard-street] are maintained by [Sam Schlinkert](https://github.com/sts10), who also created [phraze](https://github.com/sts10/phraze).

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
[phraze]: https://github.com/sts10/phraze
[zxcvbn]: https://github.com/dropbox/zxcvbn
[keepassxc]: https://keepassxc.org/
[pwned-api]: https://haveibeenpwned.com/Passwords
[k-anonymity]: https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#702702420
