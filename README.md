# Passphrase Arcana

A passphrase [word list](./passphrase-arcana.txt) built from [the vocabularies](#sources) of authors known for distinctive, unusual language, filtered for the [easiest to type](#typing-ease). Also filtered to remove proper nouns, prefixes and suffixes, non-uniquely decodable words, offensive words, homophones, and words that are similar enough that a typo could transform one into the other.

[Standard passphrase word lists](#other-word-lists) prioritize common, everyday words. This list takes the opposite approach: words like "sheepfold", "hexapods", and "acridity" are more memorable precisely because they stand out. It's [the XKCD approach](https://xkcd.com/936/), but inverted.

The list is designed for use with [`phraze`][phraze] and [other passphrase generators](#other-passphrase-generators) that can use custom lists. At 24,497 words it provides 14.7 bits of entropy per word.

> [!TIP]
> If you just need a strong non-human readable password, use `openssl rand -base64 32` and you'll be protected against even [the quantum crackers of the future](#post-quantum-considerations). (They'll steal your data another way.)

[The word list](#the-word-list) ・
[Entropy and passphrase strength](#entropy-and-passphrase-strength) ・
[About the word list](#about-the-word-list) ・
[Sources](#sources) ・
[Other word lists](#other-word-lists) ・
[Post-quantum considerations](#post-quantum-considerations) ・
[Kerckhoff's principle](#kerckhoffss-principle) ・
[Word list metrics](./docs/word-list-metrics.md) ・
[Processing pipeline](./docs/pipeline.md)

## The word list

[`passphrase-arcana.txt`](./passphrase-arcana.txt) contains 26,497 lowercase ASCII words, ready for use with `phraze`:

```bash
phraze --verbose --sep " " --custom-list passphrase-arcana.txt --minimum-entropy 60
```

Produces passphrases like:

```text
empoison juicily aloofly tabooing gyratory
composers chessmen peepshow embarks matchlock
sobs panache sidled sulkiness headless
```

Or use [`diceware`][diceware-py] or [`keepassxc-cli`][keepassxc]:

```bash
diceware --no-caps --delimiter " " --num 4 < passphrase-arcana.txt
keepassxc-cli diceware --word-list passphrase-arcana.txt --words 4
```

Bitwarden, 1Password, and Proton Pass do not support custom word lists.

I like `phraze` because it's the only tool that allows you to set a minimum entropy value for your passphrase. For all the others you need to work backwards from entropy / strength to number of words.

### Typing ease

Besides the interesting sources and the extensive filtering and validation, the best thing about this list is that it's [filtered for ease of typing](./docs/pipeline.md#step-5-score-typing-difficulty). I believe this is the only passphrase word list that takes this into account.

Every word is scored for QWERTY touch-typing effort using a [Carpalx][carpalx]-inspired model. Words above the configured threshold are filtered out.

The scores for the 26,497 words in the final list range from a minimum of 1.25 to a median of 1.95 and a maximum of 2.50. Lower is easier to type. About 32% of words score below 1.8 (easy range), and 55% below 2.0.

The easiest words tend to use home-row and index-finger keys with hand alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29). The hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Entropy and passphrase strength

### Recommended minimums

#### _My recommendations_

| Account type / usage context                                                                                                                                                                                           | Number of words from passphrase-arcana (~15 bits/word) | Number of words from EFF long list or Orchard Street medium list (13 bits/word) | Minimum information entropy | Minimum guessing entropy                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- | --------------------------- | ------------------------------------------------------------------- |
| Hardware-enforced rate limiting (macOS on M1+) <br> Accounts with a hardware key <br> Throwaway accounts (forum registrations) <br> SSH key created with high rounds setting (`-a 100` or higher) <br> WPA3 <br> LUKS2 | 2 words                                                | 2-3 words                                                                       | 30 bits                     | 536 million guesses                                                 |
| Accounts with TOTP <br> SSH key created with default rounds setting (`-a 16`) <br> GPG key with strong settings (AES-256, SHA-512, maximum S2K) <br> WPA2 <br> WPA3 for extra safety <br> LUKS1                        | 3 words                                                | 3-4 words                                                                       | 45 bits                     | 17.6 trillion guesses (number of red blood cells in the human body) |
| Accounts with weak 2FA (SMS or email) or no 2FA <br> GPG key with default settings (CAST5, SHA-1)                                                                                                                      | 4 words                                                | 5 words                                                                         | 60 bits                     | 576 quadrillion guesses                                             |
| Important accounts                                                                                                                                                                                                     | 5 words                                                | 6 words                                                                         | 75 bits                     | 18.9 sextillion guesses (number of grains of sand on Earth)         |
| Secret protecting accounts                                                                                                                                                                                             | 6 words                                                | 7 words                                                                         | 90 bits                     | 619 septillion guesses                                              |

Passwords and PINs:

- iOS: all lowercase, no spaces, no keyboard switching (numbers and symbols), 8-12 characters typed smoothly, eg 1-2 passphrase-arcana words with no separator
- YubiKey or other severely rate-limited hardware devices: 4 digit **random** code
- SSH key protected by Keychain or similar: 20+ character (128+ bits) **random** string, eg `openssl rand -base64 24`
- Important account with unknown storage and protection: 45+ character (256+ bits) **random** string, eg `openssl rand -base64 32`

I emphasize "random" in the list above, because it's critical that they be truly (cryptographically) random.

#### _Official recommendations_

Different organizations and security standards recommend different entropy floors depending on the threat model:

| Usage context                                  | Number of words from passphrase-arcana (~15 bits/word) | Number of words from EFF long list or Orchard Street medium list (13 bits/word) | Minimum entropy | Minimum guessing entropy          | Source                                                   |
| ---------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- | --------------- | --------------------------------- | -------------------------------------------------------- |
| General use, online accounts                   | 4-5 words                                              | 5 words                                                                         | ~65 bits        | 18.5 quintillion guesses          | [Diceware FAQ][diceware-faq] (5 words from a 7,776 list) |
| "For most uses"                                | 5 words                                                | 6 words                                                                         | ~77 bits        | 75.6 sextillion guesses           | [EFF][eff-long] (6 words from the EFF long list)         |
| Password-only authentication, no rate limiting | 6 words                                                | 6 words                                                                         | 80 bits         | 604 sextillion guesses            | [ANSSI][anssi] (French national cybersecurity agency)    |
| Encryption keys and long-term secrets          | 7 words                                                | 8 words                                                                         | 100 bits        | 633 octillion guesses             | [ANSSI][anssi]                                           |
| Highest assurance level for authentication     | 8 words                                                | 9 words                                                                         | 112 bits        | 2.6 decillion guesses             | [NIST SP 800-63B][nist-63b] (look-up secrets)            |
| Cryptographic keys, tokens, long-term security | 9 words                                                | 10 words                                                                        | 128 bits        | 170 undecillion guesses           | [NIST SP 800-57][nist-57], [ANSSI][anssi]                |
| Quantum-resistant secrets (see below)          | 18 words                                               | 20 words                                                                        | 256 bits        | 57.9 quattuorvigintillion guesses | Post-quantum ([Grover's algorithm][grovers])             |

For most people generating a passphrase for a password manager, email, or disk encryption, 6 words from this list (~88 bits) comfortably exceeds the EFF and ANSSI general-use recommendations.

For high-security applications like encryption keys, 8 words (~118 bits) exceeds the NIST 112-bit threshold. If you're worrying about 256 bit level security, you're better off with [a random password](#post-quantum-considerations).

### Entropy and other strength measurements

There are different ways to think about password or passphrase strength, and they fall into three general buckets: measurements of the randomness of generation, measurements of the quantity of guesses needed, and measurements of the difficulty of cracking.

The most common metric is [entropy](#how-passphrase-entropy-works) ([information or Shannon entropy](<https://en.wikipedia.org/wiki/Entropy_(information_theory)>)), which is a mathematical measure of the randomness of the secret. That can be measured either in terms of the randomness of the characters in the secret or the randomness of the selection of words in the passphrase. Entropy is a useful metric in guiding secret generation, since it provides an abstract measurement of how random the process is. From the cracking perspective, it's less useful, since it really only captures how hard it would be to brute-force crack a password. (Generate random characters or word combinations until you find a match.)

When generating a password or passphrase randomly (truly randomly, using [a cryptographically secure random number generator](https://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator)), [guessing entropy](https://www.isiweb.ee.ethz.ch/papers/arch/mass-inspec-1994-4.pdf) can be calculated from the information entropy and vice versa. In other words, the randomness of the generation process dictates how many guesses an attacker would need, assuming brute-force random guessing.

Password cracking these days (early 2026) is much more advanced than simple brute forcing, though that's always a fall back option. Tools like [John the Ripper](https://github.com/openwall/john) and [Hashcat](https://github.com/hashcat/hashcat) create combinations and permutations of words and numbers and symbols, using rules that follow how people create passwords in real life. The newest generation of tools, like [PassLLM](https://github.com/Tzohar/PassLLM), use neural networks trained on massive datasets of breached passwords and incorporate leaked PII data as well. And as the capabilities of the frontier LLMs continue to advance, password security will get harder and harder to maintain.

All of which is to say, measuring cracking time using the kinds of algorithms actually at use in the wild needs to be far more sophisticated than just measuring randomness or brute force difficulty.

### How passphrase entropy works

Password or passphrase strength is measured in terms of [information entropy][password-entropy], or the minimum number of bits necessary to hold the information in the password. (Thanks to [the OG Claude](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).)

The entropy of a password or passphrase is a function of how many characters or words it has in it and how many characters or words there are to choose from:

```math
\mathrm{entropy} = \text{count} \times \log_2(\textup{possible values})
```

If you have a password that's [truly random](#post-quantum-considerations), a string of characters generated with a cryptographical random number generator, the entropy is:

```math
\mathrm{entropy} = \text{password length} \times \log_2(\textup{possible characters})
```

Let's say you create a 6 character password from the 26 lowercase English letters:

```math
\mathrm{entropy} = 6 \text{ characters} \times \log_2(26 \text{ possible characters})
```

```math
\mathrm{entropy} = 6 \text{ characters} \times 4.7 \text{ bits} / \text{character}
```

```math
\mathrm{entropy} = 28.2 \text{ bits}
```

Similarly, if you have a passphrase that's generated by randomly selecting from a known list (which [you should assume it to be](#kerckhoffss-principle)), the entropy is:

```math
\mathrm{entropy} = \mathrm{words} \times \log_2(\textup{list size})
```

For this list (26,497 words), each word in your passphrase counts for 14.7 bits of entropy. A 6-word passphrase provides:

```math
\mathrm{entropy} = 6 \text{ words} \times \log_2(26\,497 \text{ possible words})
```

```math
\mathrm{entropy} = 6 \text{ words} \times 14.7 \text{ bits} / \text{word}
```

```math
\text{entropy} = 88.2 \text{ bits}
```

### How guessing entropy works

Guessing entropy is a measurement of how many random (brute-force) guesses it will take to crack a password. If the password is randomly generated, the number of guesses needed is simple:

```math
\text{guessing entropy} = \frac {(\text{possible values} + 1)} 2
```

The intuition behind this is straightforward. The information entropy tells us how many bits of information are required to encode a password. If a password has 88 bits of entropy, there are $2 ^ {88}$ possible passwords. On average, to guess one password will take half as long as enumerating all possible passwords, so ${2 ^ {88}} / 2$. And since you have to start with 1 guess, it becomes ${(2 ^ {88} + 1)} / 2$.

So if you have a 6 character password randomly generated from the lowercase English letters, the number of guesses required to crack it would be, on average:

```math
\text{guessing entropy} = \frac {(2 ^ {28.2} \text{ bits} + 1 \text{ bit})} {2 \text{ bits} / \text{guess}}
```

```math
\text{guessing entropy} = \frac {309 \text{ million bits}} {2 \text{ bits} / \text{guess}}
```

```math
\text{guessing entropy} = 154 \text{ million guesses}
```

Or for a 6 word passphrase randomly generated from this list:

```math
\text{guessing entropy} = \frac {(2 ^ {88.2} \text{ bits} + 1 \text{ bit})} {2 \text{ bits} / \text{guess}}
```

```math
\text{guessing entropy} = \frac {328 \text{ undecillion bits}} {2 \text{ bits} / \text{guess}}
```

```math
\text{guessing entropy} = 164 \text{ undecillion guesses}
```

And if you're rusty on what an undecillion is, it's a billion billion billion billion, or 1 with 37 zeros after it. A whole hell of a lot.

## About the word list

## Sources

Words are drawn from authors with rich, unusual vocabularies. Most are sourced from [Standard Ebooks][se] (preferred, professionally proofread) and [Project Gutenberg][gutenberg] (public domain texts). Two use concordances (word frequency data extracted from copyrighted works, which is non-copyrightable factual data):

| Author                 | Source                         | Vocabulary                      |
| ---------------------- | ------------------------------ | ------------------------------- |
| Jane Austen            | [SE][se] + [PG][pg-austen]     | Regency, ironic                 |
| Ambrose Bierce         | [PG][pg-bierce]                | Satirical, military, sardonic   |
| Charlotte Bronte       | [SE][se] + [PG][pg-cbronte]    | Gothic, passionate              |
| Emily Bronte           | [PG][pg-ebronte]               | Yorkshire moors, gothic         |
| Lewis Carroll          | [SE][se] + [PG][pg-carroll]    | Nonsense, mathematical          |
| Agatha Christie        | [SE][se] + [PG][pg-christie]   | Detective, conversational       |
| Joseph Conrad          | [SE][se] + [PG][pg-conrad]     | Maritime, colonial              |
| Arthur Conan Doyle     | [PG][pg-doyle]                 | Detective, scientific           |
| W.E.B. Du Bois         | [PG][pg-dubois]                | Sociological, literary          |
| George Eliot           | [SE][se] + [PG][pg-eliot]      | Victorian, psychological        |
| F. Scott Fitzgerald    | [SE][se] + [PG][pg-fitzgerald] | Jazz Age, lyrical               |
| Thomas Hardy           | [SE][se] + [PG][pg-hardy]      | Wessex dialect, archaic rural   |
| Nathaniel Hawthorne    | [PG][pg-hawthorne]             | Archaic, allegorical            |
| Zora Neale Hurston     | [PG][pg-hurston]               | Southern dialect, folklore      |
| Henry James            | [SE][se] + [PG][pg-hjames]     | Psychological, ornate           |
| James Joyce            | [SE][se] + [PG][pg-joyce]      | Modern experimental             |
| Rudyard Kipling        | [PG][pg-kipling]               | Colonial, Indian, vernacular    |
| Jack London            | [PG][pg-london]                | Wilderness, frontier, maritime  |
| H.P. Lovecraft         | [PG][pg-lovecraft]             | Cosmic, eldritch                |
| Cormac McCarthy        | Concordance                    | Archaic, Southern, Southwestern |
| Herman Melville        | [SE][se] + [PG][pg-melville]   | Nautical, philosophical         |
| William Morris         | [SE][se] + [PG][pg-morris]     | Pseudo-medieval, archaic        |
| Vladimir Nabokov       | Concordance                    | Ornate, precise                 |
| Edgar Allan Poe        | [SE][se] + [PG][pg-poe]        | Gothic, macabre, scientific     |
| William Shakespeare    | [PG][pg-shakespeare]           | Early Modern English            |
| Mary Shelley           | [SE][se] + [PG][pg-mshelley]   | Gothic, Romantic                |
| Robert Louis Stevenson | [SE][se] + [PG][pg-stevenson]  | Scottish, maritime, gothic      |
| Mark Twain             | [SE][se] + [PG][pg-twain]      | Vernacular, satirical           |
| Edith Wharton          | [PG][pg-wharton]               | Gilded Age, social, literary    |
| Oscar Wilde            | [SE][se] + [PG][pg-wilde]      | Aesthetic, theatrical           |
| P.G. Wodehouse         | [SE][se] + [PG][pg-wodehouse]  | Comic, Edwardian                |
| Virginia Woolf         | [SE][se] + [PG][pg-woolf]      | Impressionistic, psychological  |

The McCarthy concordance is parsed from John Sepich's [word list][sepich]. The Nabokov concordance is built at fetch time from [bukvik-workshop-corpora][bukvik] (texts are streamed and discarded; only word frequencies are kept).

### Word list attributes

| Attribute                                                                          | Value           |
| ---------------------------------------------------------------------------------- | --------------- |
| Unique words                                                                       | 26,497          |
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
| Mean word length                                                                   | 7.53 characters |
| [Entropy per word](#how-passphrase-entropy-works)                                  | 14.694 bits     |
| [Efficiency per character](./docs/word-list-metrics.md#efficiency-per-character)   | 1.953 bits      |
| [Shortest edit distance](./docs/word-list-metrics.md#edit-distance)                | 1               |
| [Mean edit distance](./docs/word-list-metrics.md#edit-distance)                    | 7.094           |
| [Unique character prefix](./docs/word-list-metrics.md#unique-character-prefix)     | 9               |
| [Kraft-McMillan inequality](./docs/word-list-metrics.md#kraft-mcmillan-inequality) | satisfied       |

Analyzed with [`wla`][wla]. See the [word list metrics docs](./docs/word-list-metrics.md) for explanations of each metric.

## Other tools

### Other passphrase generators

The word list is a plain text file (one word per line) that works with any passphrase generator that accepts a custom list.

| Tool                    | Custom list flag                                  |
| ----------------------- | ------------------------------------------------- |
| [phraze][phraze]        | `--custom-list passphrase-arcana.txt`             |
| [diceware][diceware-py] | `-w passphrase-arcana.txt`                        |
| [KeePassXC][keepassxc]  | `keepassxc-cli diceware -w passphrase-arcana.txt` |

Bitwarden, 1Password, and Proton Pass do not support custom word lists.

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

For passphrases, 256 bits would require ~18 words from this list, which is not practical. In reality, passphrases protect secrets that are processed through slow key derivation functions (argon2, bcrypt, scrypt) before use, and each hash evaluation adds significant cost to both classical and quantum brute force. A 10-word passphrase (~147 bits) run through argon2 is likely adequate even against future quantum computers, but the honest answer is that nobody knows exactly when or whether large-scale quantum brute force will become feasible.

If you need a secret that is unambiguously quantum-resistant without relying on key stretching, use a random string instead of a passphrase:

```bash
openssl rand -base64 48   # 48 bytes * 8 bits / byte = 256 bits of entropy
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
[pg-fitzgerald]: https://www.gutenberg.org/ebooks/author/420
[pg-eliot]: https://www.gutenberg.org/ebooks/author/90
[pg-cbronte]: https://www.gutenberg.org/ebooks/author/408
[pg-austen]: https://www.gutenberg.org/ebooks/author/68
[pg-dubois]: https://www.gutenberg.org/ebooks/author/226
[pg-hjames]: https://www.gutenberg.org/ebooks/author/113
[pg-mshelley]: https://www.gutenberg.org/ebooks/author/61
[pg-christie]: https://www.gutenberg.org/ebooks/author/451
[pg-bierce]: https://www.gutenberg.org/ebooks/author/206
[pg-doyle]: https://www.gutenberg.org/ebooks/author/69
[pg-ebronte]: https://www.gutenberg.org/ebooks/author/405
[pg-hardy]: https://www.gutenberg.org/ebooks/author/23
[pg-hurston]: https://www.gutenberg.org/ebooks/author/6368
[pg-kipling]: https://www.gutenberg.org/ebooks/author/132
[pg-london]: https://www.gutenberg.org/ebooks/author/120
[pg-morris]: https://www.gutenberg.org/ebooks/author/314
[pg-poe]: https://www.gutenberg.org/ebooks/author/481
[pg-stevenson]: https://www.gutenberg.org/ebooks/author/35
[pg-wharton]: https://www.gutenberg.org/ebooks/author/104
[pg-wodehouse]: https://www.gutenberg.org/ebooks/author/783
[pg-woolf]: https://www.gutenberg.org/ebooks/author/6328
[se]: https://standardebooks.org/
[carpalx]: https://mk.bcgsc.ca/carpalx/?typing_effort
[kerckhoffs]: https://en.wikipedia.org/wiki/Kerckhoffs%27s_principle
[phraze]: https://github.com/sts10/phraze
[keepassxc]: https://keepassxc.org/
[diceware-py]: https://github.com/ulif/diceware
[diceware-faq]: https://theworld.com/~reinhold/dicewarefaq.html
[anssi]: https://www.ssi.gouv.fr/en/
[nist-63b]: https://pages.nist.gov/800-63-3/sp800-63b.html
[nist-57]: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
[grovers]: https://en.wikipedia.org/wiki/Grover%27s_algorithm
[password-entropy]: https://en.wikipedia.org/wiki/Password_strength#Entropy_as_a_measure_of_password_strength
[sepich]: http://johnsepich.com/
[bukvik]: https://github.com/Cha-OS/bukvik-workshop-corpora
[wla]: https://github.com/sts10/wla
[sts10]: https://github.com/sts10
