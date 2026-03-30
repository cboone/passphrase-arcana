# Word list metrics

Definitions for the metrics in the word list attributes table in the [README](../README.md). All are computed by [wla](https://github.com/sts10/wla).

## Fuzzy duplicates

Words that are identical except for minor typographical differences. For example, "theater" and "theatre", or "color" and "colour". A list free of fuzzy duplicates avoids ambiguity when a user hears or reads a passphrase word.

## Prefix and suffix words

A prefix word is a word that is the beginning of another word in the list. For example, if both "cat" and "catalog" are in the list, "cat" is a prefix word. Suffix words are the reverse: "log" would be a suffix of "catalog". Removing these ensures the list is safe to use without separators between words, since the decoder can always determine where one word ends and the next begins.

## Uniquely decodable

A list is uniquely decodable if, when you concatenate words from it without separators, there is exactly one way to split the result back into the original words. This is a stronger property than being free of prefix words: it guarantees unambiguous decoding even in edge cases where prefix-freeness alone would not. In practice, a list that is both prefix-free and suffix-free is always uniquely decodable.

## Above brute force line

The list has enough words that randomly selecting from it provides more entropy per character than brute-forcing a random password of the same length. This is the minimum bar for a passphrase word list to be worthwhile compared to a random character password.

## Efficiency per character

Entropy per word divided by mean word length. Higher values mean more entropy per keystroke. This list's efficiency of 1.96 bits/character means a 50-character passphrase (about 6 words with spaces) provides ~88 bits of entropy, compared to ~50 bits from a random string of 50 lowercase letters (which has ~4.7 bits per character but is much harder to remember).

## Edit distance

The [Levenshtein edit distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two words is the minimum number of single-character insertions, deletions, or substitutions needed to transform one into the other. The shortest edit distance in the list is the distance between the two most similar words. A higher value means the list is more resistant to typos causing one valid word to be mistaken for another. A shortest edit distance of 1 means there exists at least one pair of words differing by a single character (e.g., "word" and "cord").

## Unique character prefix

The minimum number of leading characters needed to uniquely identify every word in the list. With a value of 9 (equal to the maximum word length), some words require their full length to be distinguished. This matters for autocomplete systems: a lower value means fewer characters are needed to disambiguate.

## Kraft-McMillan inequality

A mathematical condition from [information theory](https://en.wikipedia.org/wiki/Kraft%27s_inequality) that must hold for a set of codewords to be uniquely decodable. If the inequality is satisfied, it is theoretically possible to construct a prefix code with the given codeword lengths. For passphrase word lists, satisfying this inequality confirms the list's structure supports unambiguous concatenation.
