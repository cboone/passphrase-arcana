# Passphrase Arcana

A passphrase [word list](./passphrase-arcana.txt) built from [the vocabularies](#sources) of authors known for distinctive, unusual language, filtered for the [easiest to type](#typing-ease). Also filtered to remove proper nouns, prefixes and suffixes, non-uniquely decodable words, offensive words, homophones, and words that are similar enough that a typo could transform one into the other.

[Standard passphrase word lists](#other-word-lists) prioritize common, everyday words. This list takes the opposite approach: words like "sheepfold", "hexapods", and "acridity" are more memorable precisely because they stand out. It's [the XKCD approach](https://xkcd.com/936/), but inverted.

The list is designed for use with [`phraze`][phraze] and [other passphrase generators](#the-word-list) that can use custom lists. At 24,497 words it provides 14.7 bits of entropy per word.

> [!TIP]
> If you just need a strong non-human readable password, use `openssl rand -base64 32` and you'll be protected against even [the quantum crackers of the future](#post-quantum-considerations). (They'll steal your data another way.)

[The word list](#the-word-list) ・
[Entropy and passphrase strength](#entropy-and-passphrase-strength) ・
[Recommended minimum entropy](#recommended-minimums) ・
[Word list sources](#sources) ・
[Word list metrics](#word-list-metrics) ・
[Other word lists](#other-word-lists) ・
[Post-quantum considerations](#post-quantum-considerations) ・
[Kerckhoff's principle](#kerckhoffss-principle) ・
[Word list metrics explanations](#word-list-metrics) ・
[Minimum entropy calculations](#minimum-entropy-calculations) ・
[Processing pipeline](./docs/pipeline.md)

## The word list

[`passphrase-arcana.txt`](./passphrase-arcana.txt) contains 26,497 lowercase ASCII words, ready for use with `phraze`:

```bash
phraze --verbose --sep " " --custom-list passphrase-arcana.txt --minimum-entropy 60
```

Produces passphrases like:

```text
composers chessmen peepshow embarks matchlock
sobs panache sidled sulkiness headless
nastier gnarly chuckles farewells miseries
```

Or use [`diceware`][diceware-py] or [`keepassxc-cli`][keepassxc]:

```bash
diceware --no-caps --delimiter " " --num 4 < passphrase-arcana.txt
keepassxc-cli diceware --word-list passphrase-arcana.txt --words 4
```

Bitwarden, 1Password, and Proton Pass do not support custom word lists.

I like `phraze` because it's the only tool that allows you to set a minimum entropy value for your passphrase. For all the others you need to work backwards from entropy / strength to number of words.

### Typing ease

Besides the interesting sources and the extensive filtering and validation, the best thing about this list is that it's [filtered for ease of typing](./docs/pipeline.md#step-5-score-typing-difficulty). Every word is scored for QWERTY touch-typing effort using a [Carpalx][carpalx]-inspired model. Words above the configured threshold are filtered out.

The scores for the 26,497 words in the final list range from a minimum of 1.25 to a median of 1.95 and a maximum of 2.5. Lower is easier to type. About 32% of words score below 1.8 (easy range), and 55% below 2.0.

The easiest words tend to use home-row and index-finger keys with hand alternation: "duds" (1.25), "dusks" (1.26), "disks" (1.29). The hardest words (at the 2.5 boundary) involve bottom-row keys, same-finger bigrams, or pinky stretches: "thwarted", "wharves", "withy".

## Entropy and passphrase strength

### Recommended minimums

#### _My recommendations_

See [the minimum entropy calculations section](#minimum-entropy-calculations) for the details and sources behind these numbers. For more widely accepted numbers, see [the official recommendations section](#official-recommendations).

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

### Sources

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

| Attribute                                               | Value           |
| ------------------------------------------------------- | --------------- |
| Unique words                                            | 26,497          |
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
| Mean word length                                        | 7.53 characters |
| [Entropy per word](#how-passphrase-entropy-works)       | 14.694 bits     |
| [Efficiency per character](#efficiency-per-character)   | 1.953 bits      |
| [Shortest edit distance](#edit-distance)                | 1               |
| [Mean edit distance](#edit-distance)                    | 7.094           |
| [Unique character prefix](#unique-character-prefix)     | 9               |
| [Kraft-McMillan inequality](#kraft-mcmillan-inequality) | satisfied       |

Analyzed with [`wla`][wla]. See the [word list metrics docs]() for explanations of each metric.

## Other word lists

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

## Word list metrics

Definitions for the metrics in the word list attributes table. All are computed by [wla](https://github.com/sts10/wla).

### Fuzzy duplicates

Words that are identical except for minor typographical differences. For example, "theater" and "theatre", or "color" and "colour". A list free of fuzzy duplicates avoids ambiguity when a user hears or reads a passphrase word.

### Prefix and suffix words

A prefix word is a word that is the beginning of another word in the list. For example, if both "cat" and "catalog" are in the list, "cat" is a prefix word. Suffix words are the reverse: "log" would be a suffix of "catalog". Removing these ensures the list is safe to use without separators between words, since the decoder can always determine where one word ends and the next begins.

### Uniquely decodable

A list is uniquely decodable if, when you concatenate words from it without separators, there is exactly one way to split the result back into the original words. This is a stronger property than being free of prefix words: it guarantees unambiguous decoding even in edge cases where prefix-freeness alone would not. In practice, a list that is both prefix-free and suffix-free is always uniquely decodable.

### Above brute force line

The list has enough words that randomly selecting from it provides more entropy per character than brute-forcing a random password of the same length. This is the minimum bar for a passphrase word list to be worthwhile compared to a random character password.

## Efficiency per character

Entropy per word divided by mean word length. Higher values mean more entropy per keystroke. This list's efficiency of 1.95 bits/character means a 50-character passphrase (about 6 words with spaces) provides ~88 bits of entropy, compared to ~50 bits from a random string of 50 lowercase letters (which has ~4.7 bits per character but is much harder to remember).

### Edit distance

The [Levenshtein edit distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two words is the minimum number of single-character insertions, deletions, or substitutions needed to transform one into the other. The shortest edit distance in the list is the distance between the two most similar words. A higher value means the list is more resistant to typos causing one valid word to be mistaken for another. A shortest edit distance of 1 means there exists at least one pair of words differing by a single character (e.g., "word" and "cord").

### Unique character prefix

The minimum number of leading characters needed to uniquely identify every word in the list. With a value of 9 (equal to the maximum word length), some words require their full length to be distinguished. This matters for autocomplete systems: a lower value means fewer characters are needed to disambiguate.

### Kraft-McMillan inequality

A mathematical condition from [information theory](https://en.wikipedia.org/wiki/Kraft%27s_inequality) that must hold for a set of codewords to be uniquely decodable. If the inequality is satisfied, it is theoretically possible to construct a prefix code with the given codeword lengths. For passphrase word lists, satisfying this inequality confirms the list's structure supports unambiguous concatenation.

## Minimum entropy calculations

### Account types and usage contexts

#### 30 bits / 2 words

##### _Hardware-enforced rate limiting (macOS on M1+)_

These limits are enforced by [the Secure Enclave](https://support.apple.com/guide/security/the-secure-enclave-sec59b0b31ff/1/web/1) and can't be circumvented by restarts. The following assumes you have all the obvious security features turned on: require a password after sleep, File Vault, etc.

[From a fresh boot](https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/1/web/1), macOS allows three authentication attempts with no delay between them. After the fourth, you wait 1 minute; after the fifth, 5 minutes. Then 15 minutes, 1 hour, 3 hours, and 8 hours after the ninth attempt. After those 10 attempts are exhausted, 10 more are available in recoveryOS, and if those are also used up, 10 additional attempts are available for each FileVault recovery mechanism — iCloud recovery, FileVault recovery key, and institutional key — for a maximum of 30 additional attempts. Once all of those are gone, the Secure Enclave stops processing decryption and verification requests entirely and the data on the drive becomes unrecoverable.

The internal SSD is [protected by a key tied to the secret UID](https://support.apple.com/guide/security/the-secure-enclave-sec59b0b31ff/1/web/1) (generated randomly during processor manufacturing by the TRNG inside the Secure Enclave and fused into the hardware, thus never visible from the outside), so removing it from the machine without authenticating after a fresh boot renders its contents completely unaccessible.

Thus, before first authentication, 50 authentication attempts is the maximum before the device is inoperable. Which means that basically any random would be sufficient.

After first authentication, the SSD is unlocked (so make sure you have File Vault on), and [authentication attempts are rate limited](https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/1/web/1) but without a maximum. The fastest attempts are allowed to be made appears to be every 80ms, but real world tests seem to imply the actual limits are even more severe.

In the worst case scenario, assuming the fastest possible repeated authentication attempt timing, an attacker could make about 12.5 attempts per second, or 45,000 per hour, or about 1 million per day. That's equivalent to about 20 bits of entropy to crack your password in one day. Going up to 30 bits means an attacker will need about 3 years.

##### _Accounts with a hardware key_

##### _Throwaway accounts (forum registrations)_

##### _SSH key created with high rounds setting (-a 100 or higher)_

##### _WPA3_

##### _LUKS2_

#### 45 bits / 3 words

##### _Accounts with TOTP_

##### _SSH key created with default rounds setting (-a 16)_

##### _GPG key with strong settings (AES-256, SHA-512, maximum S2K)_

##### _WPA2_

##### _WPA3 for extra safety_

##### _LUKS1_

#### 60 bits / 4 words

##### _Accounts with weak 2FA (SMS or email) or no 2FA_

##### _GPG key with default settings (CAST5, SHA-1)_

#### 75 bits / 5 words

##### _Important accounts_

#### 90 bits / 6 words

##### _Secret protecting accounts_

#### Passwords and PINs

##### _iOS and iPadOS_

[As with macOS](#hardware-enforced-rate-limiting-macos-on-m1), these limits are enforced at the hardware level using [the Secure Enclave](https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/1/web/1) and can't be circumvented by restarts.

The internal storage is [protected by a key tied to the secret UID](https://support.apple.com/guide/security/the-secure-enclave-sec59b0b31ff/1/web/1) (generated randomly during processor manufacturing by the TRNG inside the Secure Enclave and fused into the hardware, thus never visible from the outside), so attempting to crack machine without authenticating renders its contents completely unaccessible.

iOS and iPadOS allow [a maximum of 10 authentication attempts](https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/1/web/1) before locking and requiring you to connect to a computer and perform recovery there. The first three authentication attempts have no delay between them. After the fourth, you wait 1 minute; after the fifth, 5 minutes. Then 15 minutes, 1 hour, 3 hours, and 8 hours after the ninth attempt. If you turn on Erase Data, the device will be completely erased after the tenth failed attempt.

Limiting an attacker to 10 total attempts means almost any random passcode is enough. A 6 digits gives you 20 bits of entropy, or 1 million possible codes, which is plenty. Of course, choosing a random PIN is rarely done.

As for forensic bypass tools, there are [no known techniques to brute-force](https://blog.elcomsoft.com/2025/01/the-evolution-of-ios-passcode-security/) an iPhone with an A14 or newer processor (iPhone 12 or higher). The last model that is known to have been brute-force cracked was an iPhone SE 2020 (A13 processor), and brute-forcing on that device was rate limited to about 2 attempts per minute. (Older phones were able to be brute-forced at a faster, but still very slow, rate.)

At that rate, it takes over a year to try 1 million codes. So again, 6 digits, or 20 bits of entropy, is plenty.

The bigger risk with phone passwords is being observed entering it: shoulder-surfing, whether by a bystander or a video camera. To minimize this risk you need to optimize your password selection differently. Still, of course, choose randomly; using a common password or basing a password on personal information removes almost all entropy and makes cracking extremely easy.

The best option is to use 2-3 words that equal around 8-12 characters that you can type easily and smoothly, no breaks between words, no obvious patterns from which to derive information about what it is. Keep the password all lowercase alphabetical characters, no numbers, no symbols, no need to change keyboards or hit the space bar. As uniform as possible.

10 characters of all lowercase letters gives around 47 bits of entropy, far more than an iPhone needs. But more importantly it means that even if someone sees part of what you type, your password is still extremely difficult to guess.

##### _YubiKey and other hardware devices_

YubiKeys allow [a maximum of 8 attempts](https://support.yubico.com/s/article/Understanding-YubiKey-PINs) before locking and requiring it to be reset.

If chosen randomly (an important caveat for any PIN), a 4 digit PIN is sufficient. 6 digits is more than enough.

##### _SSH key protected by Keychain_

##### _Important account with unknown storage and protection_

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.

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
