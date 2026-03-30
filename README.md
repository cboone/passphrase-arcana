# Passphrase Arcana

A passphrase [word list](./passphrase-arcana.txt) built from [the vocabularies](#sources) of authors known for distinctive, unusual language, filtered for the [easiest to type](#typing-ease). Also filtered to remove proper nouns, prefixes and suffixes, non-uniquely decodable words, offensive words, homophones, and words that are similar enough that a typo could transform one into the other.

[Standard passphrase word lists](#other-word-lists) prioritize common, everyday words. This list takes the opposite approach: words like "sheepfold", "hexapods", and "acridity" are more memorable precisely because they stand out.

The list is designed for use with [`phraze`][phraze] and [other passphrase generators](#other-passphrase-generators) that can use custom lists. There's also [a helper script](#generating-passphrases) that runs `phraze` to generate a passphrase, then [tests it in several ways](#passphrase-strength-testing) to ensure it's strong and never before compromised.

> [!TIP]
> If you just need a strong non-human readable password, use `openssl rand -base64 32` and you'll be protected against even the quantum crackers of the future. (They'll steal your data another way.)

[**The word list**](#the-word-list) ・
[Generating passphrases](#generating-passphrases) ・
[Entropy and passphrase length](#entropy-and-passphrase-strength) ・
[Passphrase strength testing](#passphrase-strength-testing)<br>
[**About the word list**](#about-the-word-list) ・
[Sources](#sources) ・
[Word selection](#word-selection) ・
[Word list attributes](#word-list-attributes) ・
[Typing ease](#typing-ease)<br>
[**Other tools**](#other-tools) ・
[Passphrase generators](#other-passphrase-generators) ・
[Word lists](#other-word-lists)<br>
[**Security notes**](#additional-security-notes) ・
[Post-quantum considerations](#post-quantum-considerations) ・
[Kerckhoff's principle](#kerckhoffss-principle) ・
[Different entropy measurements](#why-phraze-and-keepassxc-cli-report-different-entropy)<br>
[**Other docs**](./docs/) ・
[Word list metrics](./docs/word-list-metrics.md) ・
[Processing pipeline](./docs/pipeline.md)

## The word list

[`passphrase-arcana.txt`](./passphrase-arcana.txt) contains 24,880 lowercase ASCII words, ready for use with `phraze`:

```bash
phraze --verbose --sep " " --custom-list passphrase-arcana.txt --minimum-entropy 80
```

Produces passphrases like:

```text
sprouting ascendant lifters asbestos kudzu bleaching
profiled beeline tost eggcups coursers gutters
arose speaketh mindless furlongs briskly alguacil
```

## Generating passphrases

[`arcana`](./bin/arcana) is a simple Bash script that runs `phraze` using the `passphrase-arcana` word list, then checks it with several tools to ensure that it's strong and never before compromised.

### Installation

```bash
git clone https://github.com/cboone/passphrase-arcana.git
cd passphrase-arcana
make install             # symlinks bin/arcana to ~/.local/bin/
```

To install in a different directory:

```bash
make install PREFIX=/usr/local
```

To uninstall:

```bash
make uninstall
```

### Usage

`arcana` generates a passphrase and [validates its strength](#passphrase-strength-testing).

```bash
arcana            # default: 80 bits minimum entropy
arcana 100        # request 100 bits
arcana --copy     # copy to clipboard, show diagnostics
arcana --quiet    # just the passphrase, no diagnostics
arcana -qc        # silently copy to clipboard
arcana --setup    # check dependencies, show install instructions
```

If the passphrase has been compromised before (absurdly unlikely, but might as well be sure), the script exits with status 1 and doesn't copy the passphrase to the clipboard or print it to stout.

### Dependencies

Run `arcana --setup` to see what's installed and what's missing.

[`phraze`][phraze] **(required)**<br>
Generates the passphrase. `brew install sts10/phraze/phraze` or `cargo install phraze` or [other methods][phraze-install].

`curl` + `shasum` _(optional)_<br>
[Pwned Passwords][pwned-api] breach check. Both are typically pre-installed.

[`uv`][uv] + [`zxcvbn-python`][zxcvbn-python] _(optional)_<br>
Pattern-based strength scoring with crack time estimates. Install `uv`, then run `uv sync --extra dev` in the repo to set up the Python dependencies.

[keepassxc-cli][keepassxc] _(optional)_<br>
Independent entropy estimate with per-segment breakdown. `brew install keepassxc` or [other methods][keepassxc-download].

### Copying to the system clipboard

If you pass `--copy`, `arcana` will use the appropriate tool from this list to copy the generated passphrase to the system clipbard:

| Tool                 | Platform | Notes                                               |
| -------------------- | -------- | --------------------------------------------------- |
| [`pbcopy2`][pbcopy2] | macOS    | `--conceal` hides from history; `-t 30` auto-clears |
| `pbcopy`             | macOS    | Built-in default                                    |
| `clip.exe`           | WSL      | Built-in Windows clipboard                          |
| `wl-copy`            | Wayland  | `--sensitive`; skips clipboard history              |
| `xclip`              | X11      | Uses `-selection clipboard`                         |
| `xsel`               | X11      | Uses `--clipboard --input`                          |

[`pbcopy2`][pbcopy2] is preferred on macOS because it conceals the passphrase from clipboard history managers and auto-clears the clipboard after 30 seconds. Install it with: `brew install cboone/tap/pbcopy2`

### Script security

The passphrase never leaks outside the script. It is passed to each tool via stdin using `printf` (a shell builtin), so it never appears in shell history or process listings. The Pwned Passwords check uses [k-anonymity][k-anonymity]: only the first 5 characters of the SHA-1 hash leave the machine.

## Entropy and passphrase strength

There are different ways to think about and measure password or passphrase strength. It's hard to make a general rule that covers all cases. The most common metric is [entropy](#how-passphrase-entropy-works),

### How passphrase entropy works

Password or passphrase strength is measured in terms of [information entropy][password-entropy], or the minimum number of bits necessary to hold the information in the password. (Thanks to [the OG Claude](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).) There are different ways to calculate this and to think about this, but the most common for a passphrase with a known word list is:

```text
entropy = num_words x log2(list_size)
```

For this list (24,880 words), each word in your passphrase counts for **14.6 bits** of entropy. This assumes that your attacker knows that you're using this list, which is the safe assumption to make.

| Words | Entropy  | Use case                                    |
| ----- | -------- | ------------------------------------------- |
| ≈4    | 60 bits  | Low-value accounts                          |
| ≈5    | 75 bits  | Most online accounts                        |
| ≈6    | 90 bits  | Important accounts                          |
| ≈7    | 100 bits | High-security accounts, encryption keys     |
| ≈8    | 128 bits | Exceeds NIST SP 800-63B highest level (112) |

The `arcana` script defaults to 80 bits minimum entropy, which requires 6 words from this list (6 x 14.60 = 87.6 bits).

### Recommended minimums

Different organizations and security standards recommend different entropy floors depending on the threat model:

| Minimum  | passphrase-arcana           | Source                                                   | Context                                        |
| -------- | --------------------------- | -------------------------------------------------------- | ---------------------------------------------- |
| ~65 bits | ~4 words                    | [Diceware FAQ][diceware-faq] (5 words from a 7,776 list) | General use, online accounts                   |
| ~77 bits | ~5 words                    | [EFF][eff-long] (6 words from the EFF long list)         | "For most uses"                                |
| 80 bits  | ~5 words (`arcana` default) | [ANSSI][anssi] (French national cybersecurity agency)    | Password-only authentication, no rate limiting |
| 100 bits | ~7 words                    | [ANSSI][anssi]                                           | Encryption keys and long-term secrets          |
| 112 bits | ~8 words                    | [NIST SP 800-63B][nist-63b] (look-up secrets)            | Highest assurance level for authentication     |
| 128 bits | ~9 words                    | [NIST SP 800-57][nist-57], [ANSSI][anssi]                | Cryptographic keys, tokens, long-term security |
| 256 bits | ~18 words                   | Post-quantum ([Grover's algorithm][grovers])             | Quantum-resistant secrets (see below)          |

For most people generating a passphrase for a password manager, email, or disk encryption, 6 words from this list (~88 bits) comfortably exceeds the EFF and ANSSI general-use recommendations. For high-security applications like encryption keys, 8 words (~117 bits) exceeds the NIST 112-bit threshold.

### Passphrase strength testing

The `arcana` script runs three independent checks. Each evaluates passphrase strength from a different angle:

**`phraze`** provides the entropy figure you should rely on for passphrase security. It calculates entropy from the word list size and word count.

**`zxcvbn`** takes a different approach: it models how a real-world attacker cracks passwords by recognizing patterns like dictionary words, keyboard walks, dates, and common substitutions. It reports a 0-4 score, estimated guess count, and crack times at various attack speeds (online throttled, offline slow hash, offline fast hash). For passphrases from a curated list, `zxcvbn` tends to underestimate strength because it matches individual words against its internal dictionaries rather than considering the combinatorial word list space.

**`keepassxc-cli`** estimates entropy per character segment and totals them. Useful for seeing which parts of a passphrase contribute most to its strength, but the total typically overstates security against a word-list-aware attacker.

**Pwned Passwords** checks whether the exact passphrase appears in known data breaches. It uses [k-anonymity][k-anonymity]: only the first 5 characters of the SHA-1 hash leave the machine, so the passphrase is never exposed to the API. A match does not mean the passphrase was _yours_, just that someone has used the same string before.

## About the word list

## Sources

Words are drawn from authors with rich, unusual vocabularies. Most are sourced from [Project Gutenberg][gutenberg] (public domain texts). Two use concordances (word frequency data extracted from copyrighted works, which is non-copyrightable factual data):

| Author              | Works | Source                              | Vocabulary                      |
| ------------------- | ----- | ----------------------------------- | ------------------------------- |
| Herman Melville     | 14    | [Project Gutenberg][pg-melville]    | Nautical, philosophical         |
| H.P. Lovecraft      | 18    | [Project Gutenberg][pg-lovecraft]   | Cosmic, eldritch                |
| Joseph Conrad       | 14    | [Project Gutenberg][pg-conrad]      | Maritime, colonial              |
| James Joyce         | 5     | [Project Gutenberg][pg-joyce]       | Modern experimental             |
| Nathaniel Hawthorne | 8     | [Project Gutenberg][pg-hawthorne]   | Archaic, allegorical            |
| Mark Twain          | 12    | [Project Gutenberg][pg-twain]       | Vernacular, satirical           |
| Lewis Carroll       | 7     | [Project Gutenberg][pg-carroll]     | Nonsense, mathematical          |
| Oscar Wilde         | 12    | [Project Gutenberg][pg-wilde]       | Aesthetic, theatrical           |
| William Shakespeare | 1     | [Project Gutenberg][pg-shakespeare] | Early Modern English            |
| Cormac McCarthy     | 16    | Concordance                         | Archaic, Southern, Southwestern |
| Vladimir Nabokov    | 11    | Concordance                         | Ornate, precise                 |

The McCarthy concordance is parsed from John Sepich's [word list][sepich]. The Nabokov concordance is built at fetch time from [bukvik-workshop-corpora][bukvik] (texts are streamed and discarded; only word frequencies are kept).

### Word list attributes

| Attribute                                                                          | Value           |
| ---------------------------------------------------------------------------------- | --------------- |
| Unique words                                                                       | 24,880          |
| Free of exact duplicates                                                           | yes             |
| Free of [fuzzy duplicates](./docs/word-list-metrics.md#fuzzy-duplicates)           | yes             |
| No non-ASCII characters                                                            | yes             |
| Unicode normalized                                                                 | yes             |
| Free of [prefix words](./docs/word-list-metrics.md#prefix-and-suffix-words)        | yes             |
| Free of [suffix words](./docs/word-list-metrics.md#prefix-and-suffix-words)        | yes             |
| [Uniquely decodable](./docs/word-list-metrics.md#uniquely-decodable)               | yes             |
| [Above brute force line](./docs/word-list-metrics.md#above-brute-force-line)       | yes             |
| Shortest word                                                                      | 4 characters    |
| Longest word                                                                       | 9 characters    |
| Mean word length                                                                   | 7.45 characters |
| [Entropy per word](#how-passphrase-entropy-works)                                  | 14.603 bits     |
| [Efficiency per character](./docs/word-list-metrics.md#efficiency-per-character)   | 1.960 bits      |
| [Shortest edit distance](./docs/word-list-metrics.md#edit-distance)                | 1               |
| [Mean edit distance](./docs/word-list-metrics.md#edit-distance)                    | 7.018           |
| [Unique character prefix](./docs/word-list-metrics.md#unique-character-prefix)     | 9               |
| [Kraft-McMillan inequality](./docs/word-list-metrics.md#kraft-mcmillan-inequality) | satisfied       |

Analyzed with [`wla`][wla]. See the [word list metrics docs](./docs/word-list-metrics.md) for explanations of each metric.

### Typing ease

Every word is scored for QWERTY touch-typing effort using a [Carpalx][carpalx]-inspired model (see [Step 5](./docs/pipeline.md#step-5-score-typing-difficulty)). Words above the configured threshold are filtered out.

The scores for the 24,880 words in the final list range from a minimum 1.25 to a median of 1.94 and a maximum of 2.50. Lower is easier to type. About 32% of words score below 1.8 (easy range), and 55% below 2.0.

The easiest words tend to use home-row and index-finger keys with hand alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29). The hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Other tools

### Other passphrase generators

The word list is a plain text file (one word per line) that works with any passphrase generator that accepts a custom list.

#### CLI tools

| Tool                             | Language | Custom list flag |
| -------------------------------- | -------- | ---------------- |
| [phraze][phraze]                 | Rust     | `--custom-list`  |
| [rusty-diceware][rusty-diceware] | Rust     | `-f`             |
| [diceware][diceware-py]          | Python   | `-w`             |
| [pwgen-go][pwgen-go]             | Go       | via config       |

#### Password managers

[KeePassXC][keepassxc] supports custom word lists for its built-in passphrase generator. Copy the word list into KeePassXC's `share/wordlists/` directory, or use the CLI:

```bash
keepassxc-cli diceware -w passphrase-arcana.txt -W 6
```

[Bitwarden][bitwarden] and [1Password][1password] do not currently support custom word lists for passphrase generation.

### Other word lists

The `passphrase-arcana` list prioritizes distinctive vocabulary over everyday words. If you want common, easy-to-spell words instead, these are good alternatives:

| List                                   | Words  | Bits/word | Description                                                     |
| -------------------------------------- | ------ | --------- | --------------------------------------------------------------- |
| [Orchard Street Long][os-long]         | 17,576 | 14.10     | Common English from Wikipedia and Google Books                  |
| [Orchard Street Medium][os-medium]     | 8,192  | 13.00     | Common English, power-of-2 optimized for phraze                 |
| [EFF Long][eff-long]                   | 7,776  | 12.93     | Common English, designed for easy spelling                      |
| [Orchard Street Diceware][os-diceware] | 7,776  | 12.93     | Common English, diceware-compatible (6^5 words)                 |
| [Orchard Street QWERTY][os-qwerty]     | 1,296  | 10.34     | Optimized for tvs and other devices with a QWERTY layout        |
| [Orchard Street Alpha][os-alpha]       | 1,296  | 10.34     | Optimized for tvs and other devices with an alphabetical layout |
| [EFF Short 1][eff-short]               | 1,296  | 10.34     | Short common words                                              |

Larger lists need fewer words per passphrase to reach the same entropy. A 6-word passphrase from the EFF Long list (~78 bits) is roughly equivalent to a 5-word passphrase from this list (~73 bits).

The [Orchard Street wordlists][orchard-street] are maintained by [Sam Schlinkert][sts10], who also created [`phraze`][phraze].

## Additional security notes

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

## License

MIT

<!-- Reference links -->

[eff-long]: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
[eff-short]: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases
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
[phraze-install]: https://github.com/sts10/phraze#installing
[uv]: https://docs.astral.sh/uv/
[zxcvbn-python]: https://github.com/dwolfhub/zxcvbn-python
[keepassxc-download]: https://keepassxc.org/download/
[password-entropy]: https://en.wikipedia.org/wiki/Password_strength#Entropy_as_a_measure_of_password_strength
[sepich]: http://johnsepich.com/
[bukvik]: https://github.com/Cha-OS/bukvik-workshop-corpora
[wla]: https://github.com/sts10/wla
[bitwarden]: https://bitwarden.com/
[1password]: https://1password.com/
[sts10]: https://github.com/sts10
