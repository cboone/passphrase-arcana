# Passphrase Arcana

A passphrase [word list](./passphrase-arcana.txt) built from [the vocabularies](#sources) of authors known for distinctive, unusual language, filtered for medium length and [easy typing](#typing-ease).

[Standard passphrase word lists](#other-word-lists) prioritize common, everyday words. This list takes the opposite approach: words like "sheepfold", "hexapods", and "acridity" are more memorable precisely because they stand out.

The list is designed for use with [`phraze`](https://github.com/sts10/phraze) and [other passphrase generators](#other-passphrase-generators) that can use custom lists. There's also [a helper script](#generating-passphrases) that runs `phraze` to generate a passphrase, then [tests it in several ways](#other-passphrase-testing-tools) to ensure it's strong and never before used.

[**The word list**](#the-word-list) ・
[**Other passphrase generators**](#other-passphrase-generators) ・
[**Generating passphrases**](#generating-passphrases) ・
[**Word list attributes**](#word-list-attributes) ・
[**Typing ease**](#typing-ease) ・
[**Entropy and passphrase length**](#entropy-and-passphrase-length) ・
[**Sources**](#sources) ・
[**Processing pipeline**](#processing-pipeline) ・
[**Other word lists**](#other-word-lists) ・
[**Appendix: word list metrics**](#appendix-word-list-metrics)

## The word list

[`passphrase-arcana.txt`](./passphrase-arcana.txt) contains 24,880 lowercase ASCII words, one per line, ready for use with `phraze`:

```bash
phraze --verbose --sep " " --custom-list passphrase-arcana.txt --minimum-entropy 80
```

Sample passphrases:

```text
sprouting ascendant lifters asbestos kudzu bleaching
profiled beeline tost eggcups coursers gutters
arose speaketh mindless furlongs briskly alguacil
```

For lists built from common words instead, see the [Orchard Street wordlists][orchard-street] (by the same author as phraze), or the [EFF dice lists][eff-dice].

([EFF][eff-dice], [diceware][diceware], [Orchard Street][orchard-street])

## Other passphrase generators

The word list is a plain text file (one word per line) that works with any passphrase generator that accepts a custom list. Beyond `phraze`, here are some options:

### CLI tools

| Tool                             | Language | Custom list flag | Install                  |
| -------------------------------- | -------- | ---------------- | ------------------------ |
| [phraze][phraze]                 | Rust     | `--custom-list`  | `cargo install phraze`   |
| [rusty-diceware][rusty-diceware] | Rust     | `-f`             | `cargo install diceware` |
| [diceware][diceware-py]          | Python   | `-w`             | `pip install diceware`   |
| [pwgen-go][pwgen-go]             | Go       | via config       | `go install` or Homebrew |

Example with rusty-diceware:

```bash
diceware -f passphrase-arcana.txt -n 6
```

Example with the Python diceware tool:

```bash
diceware -w passphrase-arcana.txt -n 6
```

### Password managers

[KeePassXC][keepassxc] supports custom word lists for its built-in passphrase generator. Copy the word list into KeePassXC's `share/wordlists/` directory, or use the CLI:

```bash
keepassxc-cli diceware -w passphrase-arcana.txt -W 6
```

KeePassXC requires lists with at least 1,000 words and warns below 4,000. This list's 24,880 words are well above both thresholds.

[Bitwarden](https://bitwarden.com/) and [1Password](https://1password.com/) do not currently support custom word lists for passphrase generation.

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

**For `--copy`** (first available is used):

| Tool                 | Platform | Notes                                               |
| -------------------- | -------- | --------------------------------------------------- |
| [`pbcopy2`][pbcopy2] | macOS    | `--conceal` hides from history; `-t 30` auto-clears |
| `pbcopy`             | macOS    | Built-in fallback                                   |
| `clip.exe`           | WSL      | Built-in Windows clipboard                          |
| `wl-copy`            | Wayland  | `--sensitive`; skips clip history                   |
| `xclip`              | X11      | Uses `-selection clipboard`                         |
| `xsel`               | X11      | Uses `--clipboard --input`                          |

[`pbcopy2`][pbcopy2] is preferred when available because it conceals the passphrase from clipboard history managers and auto-clears it after 30 seconds. Install with `brew install cboone/tap/pbcopy2`. Without it, the script falls back to the platform's native clipboard tool.

### Security

The passphrase never leaks outside the script:

- It is passed to each tool via stdin using `printf` (a shell builtin), so it never appears in process listings.
- The Pwned Passwords check uses [k-anonymity](https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#702702420): only the first 5 characters of the SHA-1 hash leave the machine.
- On Wayland, `wl-copy --sensitive` hints clipboard managers not to store the content in their history.

## Word list attributes

Analyzed with [wla](https://github.com/sts10/wla). See the [appendix](#appendix-word-list-metrics) for explanations of each metric.

| Attribute                                               | Value           |
| ------------------------------------------------------- | --------------- |
| Unique words                                            | 24,880          |
| Free of exact duplicates                                | yes             |
| Free of [fuzzy duplicates](#fuzzy-duplicates)           | yes             |
| No non-ASCII characters                                 | yes             |
| Unicode normalized                                      | yes             |
| Free of [prefix words](#prefix-and-suffix-words)        | yes             |
| Free of [suffix words](#prefix-and-suffix-words)        | yes             |
| [Uniquely decodable](#uniquely-decodable)               | yes             |
| [Above brute force line](#above-brute-force-line)       | yes             |
| Shortest word                                           | 4 characters    |
| Longest word                                            | 9 characters    |
| Mean word length                                        | 7.45 characters |
| [Entropy per word](#how-passphrase-entropy-works)       | 14.603 bits     |
| [Efficiency per character](#efficiency-per-character)   | 1.960 bits      |
| [Shortest edit distance](#edit-distance)                | 1               |
| [Mean edit distance](#edit-distance)                    | 7.018           |
| [Unique character prefix](#unique-character-prefix)     | 9               |
| [Kraft-McMillan inequality](#kraft-mcmillan-inequality) | satisfied       |

A 4-word passphrase provides ~58 bits of entropy. A 6-word passphrase provides ~88 bits.

## Typing ease

Every word is scored for QWERTY touch-typing effort using a [Carpalx][carpalx]-inspired model (see [Step 5](docs/pipeline.md#step-5-score-typing-difficulty)). Words above the configured threshold are filtered out. The scores for the 24,880 words in the final list:

| Statistic       | Effort per character |
| --------------- | -------------------- |
| Minimum         | 1.25                 |
| 10th percentile | 1.64                 |
| 25th percentile | 1.75                 |
| Median          | 1.94                 |
| Mean            | 1.97                 |
| 75th percentile | 2.19                 |
| 90th percentile | 2.36                 |
| Maximum         | 2.50 (threshold)     |

Lower is easier. The scale runs from ~1.0 (home-row keys with hand alternation) to 2.5 (the configured cutoff). About 32% of words score below 1.8 (easy range), and 55% below 2.0.

Easiest words tend to use home-row and index-finger keys with hand alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29). Hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Entropy and passphrase length

### How passphrase entropy works

Entropy measures how many guesses an attacker needs to crack a passphrase. With a known word list, the calculation is:

```text
entropy = num_words x log2(list_size)
```

For this list (24,880 words): **14.60 bits per word**.

| Words | Entropy   | Length | Use case                                    |
| ----- | --------- | ------ | ------------------------------------------- |
| 4     | ~58 bits  | ~33 ch | Low-value accounts                          |
| 5     | ~73 bits  | ~42 ch | Most online accounts                        |
| 6     | ~88 bits  | ~50 ch | Important accounts, the `arcana` default    |
| 7     | ~102 bits | ~58 ch | High-security accounts, encryption keys     |
| 8     | ~117 bits | ~67 ch | Exceeds NIST SP 800-63B highest level (112) |

Length assumes space separators and the list's mean word length of 7.45 characters.

The `arcana` script defaults to 80 bits minimum entropy, which requires 6 words from this list (6 x 14.60 = 87.6 bits).

### Recommended minimums

Different organizations and security standards recommend different entropy floors depending on the threat model:

| Minimum  | Source                                                   | Context                                        |
| -------- | -------------------------------------------------------- | ---------------------------------------------- |
| ~65 bits | [Diceware FAQ][diceware-faq] (5 words from a 7,776 list) | General use, online accounts                   |
| ~77 bits | [EFF][eff-long] (6 words from the EFF long list)         | "For most uses"                                |
| 80 bits  | [ANSSI][anssi] (French national cybersecurity agency)    | Password-only authentication, no rate limiting |
| 100 bits | [ANSSI][anssi]                                           | Encryption keys and long-term secrets          |
| 112 bits | [NIST SP 800-63B][nist-63b] (look-up secrets)            | Highest assurance level for authentication     |
| 128 bits | [NIST SP 800-57][nist-57], [ANSSI][anssi]                | Cryptographic keys, tokens, long-term security |
| 256 bits | Post-quantum ([Grover's algorithm][grovers])             | Quantum-resistant secrets (see below)          |

For most people generating a passphrase for a password manager, email, or disk encryption, 6 words from this list (~88 bits) comfortably exceeds the EFF and ANSSI general-use recommendations. For high-security applications like encryption keys, 8 words (~117 bits) approaches the NIST 112-bit threshold.

### Post-quantum considerations

[Grover's algorithm][grovers], a quantum computing algorithm, provides a square-root speedup for brute-force search. This effectively halves your security bits: 128-bit entropy drops to 64-bit security against a quantum attacker, and 256 bits drops to 128. NIST's post-quantum guidance recommends 256-bit symmetric keys (equivalent to 128-bit post-quantum security) for long-term protection.

For passphrases, 256 bits would require ~18 words from this list, which is not practical. In reality, passphrases protect secrets that are processed through slow key derivation functions (argon2, bcrypt, scrypt) before use, and each hash evaluation adds significant cost to both classical and quantum brute force. A 10-word passphrase (~146 bits) run through argon2 is likely adequate even against future quantum computers, but the honest answer is that nobody knows exactly when or whether large-scale quantum brute force will become feasible.

If you need a secret that is unambiguously quantum-resistant without relying on key stretching, use a random string instead of a passphrase:

```bash
openssl rand -base64 32    # 256 bits of entropy, ~44 characters
```

The argument to `openssl rand -base64` is the number of random **bytes**. Each byte contributes 8 bits of entropy, so the mapping is straightforward:

| Bytes | Entropy  | Output length | Quantum-equivalent |
| ----- | -------- | ------------- | ------------------ |
| 16    | 128 bits | ~24 chars     | 64 bits            |
| 24    | 192 bits | ~32 chars     | 96 bits            |
| 32    | 256 bits | ~44 chars     | 128 bits           |
| 48    | 384 bits | ~64 chars     | 192 bits           |

The output is longer than the input because base64 encodes 3 bytes into 4 printable characters, but the entropy comes entirely from the random bytes, not the encoding. These strings are not human-memorable, so they are best suited for secrets stored in a password manager or used programmatically.

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

Six-step Python pipeline, orchestrated by a Makefile and run with `uv`:

```text
fetch -> extract -> filter proper nouns -> validate -> score typing -> build
```

Each step is idempotent: fetches are cached, and `make all` skips completed steps. See **[docs/pipeline.md](docs/pipeline.md)** for the full documentation of each step, the blocklist, configuration, and how to run individual steps.

Quick start:

```bash
uv sync
make all       # run the full pipeline
make test      # run tests
```

## Other word lists

This list prioritizes distinctive vocabulary over everyday words. If you want common, easy-to-spell words instead, these are good alternatives:

| List                                   |  Words | Bits/word | Description                                     |
| -------------------------------------- | -----: | --------: | ----------------------------------------------- |
| **Passphrase Arcana**                  | 24,880 |     14.60 | Literary vocabulary, distinctive words          |
| [Orchard Street Long][os-long]         | 17,576 |     14.10 | Common English from Wikipedia and Google Books  |
| [Orchard Street Medium][os-medium]     |  8,192 |     13.00 | Common English, power-of-2 optimized for phraze |
| [EFF Long][eff-long]                   |  7,776 |     12.93 | Common English, designed for easy spelling      |
| [Orchard Street Diceware][os-diceware] |  7,776 |     12.93 | Common English, diceware-compatible (6^5 words) |
| [Orchard Street QWERTY][os-qwerty]     |  1,296 |     10.34 | Optimized for QWERTY typing ease                |
| [Orchard Street Alpha][os-alpha]       |  1,296 |     10.34 | Alphabetically distinct, for reading aloud      |
| [EFF Short 1][eff-short]               |  1,296 |     10.34 | Short common words                              |

Larger lists need fewer words per passphrase to reach the same entropy. A 6-word passphrase from the EFF Long list (~78 bits) is roughly equivalent to a 5-word passphrase from this list (~73 bits).

The [Orchard Street wordlists][orchard-street] are maintained by [Sam Schlinkert](https://github.com/sts10), who also created [phraze](https://github.com/sts10/phraze).

## Appendix: word list metrics

Definitions for the metrics in the [word list attributes](#word-list-attributes) table. All are computed by [wla](https://github.com/sts10/wla).

### Fuzzy duplicates

Words that are identical except for minor typographical differences. For example, "theater" and "theatre", or "color" and "colour". A list free of fuzzy duplicates avoids ambiguity when a user hears or reads a passphrase word.

### Prefix and suffix words

A prefix word is a word that is the beginning of another word in the list. For example, if both "cat" and "catalog" are in the list, "cat" is a prefix word. Suffix words are the reverse: "log" would be a suffix of "catalog". Removing these ensures the list is safe to use without separators between words, since the decoder can always determine where one word ends and the next begins.

### Uniquely decodable

A list is uniquely decodable if, when you concatenate words from it without separators, there is exactly one way to split the result back into the original words. This is a stronger property than being free of prefix words: it guarantees unambiguous decoding even in edge cases where prefix-freeness alone would not. In practice, a list that is both prefix-free and suffix-free is always uniquely decodable.

### Above brute force line

The list has enough words that randomly selecting from it provides more entropy per character than brute-forcing a random password of the same length. This is the minimum bar for a passphrase word list to be worthwhile compared to a random character password.

### Efficiency per character

Entropy per word divided by mean word length. Higher values mean more entropy per keystroke. This list's efficiency of 1.96 bits/character means a 50-character passphrase (about 6 words with spaces) provides ~88 bits of entropy, compared to ~50 bits from a random string of 50 lowercase letters (which has ~4.7 bits per character but is much harder to remember).

### Edit distance

The [Levenshtein edit distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two words is the minimum number of single-character insertions, deletions, or substitutions needed to transform one into the other. The shortest edit distance in the list is the distance between the two most similar words. A higher value means the list is more resistant to typos causing one valid word to be mistaken for another. A shortest edit distance of 1 means there exists at least one pair of words differing by a single character (e.g., "word" and "cord").

### Unique character prefix

The minimum number of leading characters needed to uniquely identify every word in the list. With a value of 9 (equal to the maximum word length), some words require their full length to be distinguished. This matters for autocomplete systems: a lower value means fewer characters are needed to disambiguate.

### Kraft-McMillan inequality

A mathematical condition from [information theory](https://en.wikipedia.org/wiki/Kraft%27s_inequality) that must hold for a set of codewords to be uniquely decodable. If the inequality is satisfied, it is theoretically possible to construct a prefix code with the given codeword lengths. For passphrase word lists, satisfying this inequality confirms the list's structure supports unambiguous concatenation.

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
[rusty-diceware]: https://crates.io/crates/diceware
[diceware-py]: https://github.com/ulif/diceware
[pwgen-go]: https://github.com/gabe565/pwgen-go
[diceware-faq]: https://theworld.com/~reinhold/dicewarefaq.html
[anssi]: https://www.ssi.gouv.fr/en/
[nist-63b]: https://pages.nist.gov/800-63-3/sp800-63b.html
[nist-57]: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
[grovers]: https://en.wikipedia.org/wiki/Grover%27s_algorithm
[pbcopy2]: https://github.com/cboone/pbcopy2
