# Passphrase Word List Pipeline

## Context

Standard passphrase word lists (EFF, diceware) prioritize common, recognizable words. This project takes the opposite approach: sourcing words from authors known for unusual, evocative vocabularies (Melville, Lovecraft, Joyce, Twain, Carroll, Wilde, Baudelaire, Proust, Machado de Assis, etc.) to produce passphrases that are more memorable precisely because the words are distinctive. The list targets `phraze` as the passphrase generator and supports English, French, and Portuguese (with diacritics removed).

## Pipeline Overview

Five Python scripts, each reading from the previous step's output, orchestrated by a Makefile:

```text
fetch_texts → extract_words → validate_words → score_typing → build_list
```

All scripts invoked via `uv run`. Intermediate data in `data/` (gitignored). Final output in `output/`.

## Project Structure

```text
word-lists/
  pyproject.toml
  Makefile
  config.toml                       # Authors, ebook IDs, thresholds
  src/
    fetch_texts.py                  # Step 1: Download Gutenberg texts
    extract_words.py                # Step 2: Tokenize, strip diacritics, filter by length
    validate_words.py               # Step 3: Dictionary verification
    score_typing.py                 # Step 4: Typing difficulty scores
    build_list.py                   # Step 5: Deduplicate, remove prefix words, output
    typing_model.py                 # Library: QWERTY typing effort model
    gutenberg.py                    # Library: Gutenberg fetch/clean helpers
  data/                             # Intermediate files (gitignored)
    raw/{lang}/                     # Downloaded texts
    words/{lang}/                   # Extracted word sets
    validated/                      # Dictionary-verified words
    scored/                         # Words with typing scores
  output/                           # Final word lists
    word-list.txt                   # Combined list for phraze
  tests/
    test_typing_model.py
```

## Step 1: Fetch Texts (`src/fetch_texts.py`)

- Read `config.toml` for Project Gutenberg ebook IDs per language/author
- Download from `https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt`
- Strip Gutenberg headers/footers (`*** START OF` / `*** END OF` markers)
- Save to `data/raw/{lang}/{author}_{id}.txt`
- Rate limit: 1 second between requests
- Skip already-downloaded files

### Source Authors and Gutenberg Ebook IDs

All IDs to be verified during implementation. The fetch script should log detected language from the Gutenberg header and warn on mismatches. Pick one edition per work (avoid duplicate IDs for the same text).

**English:**

- **Melville**: 2701 (Moby Dick), 11231 (Bartleby), 1900 (Typee), 4045 (Omoo), 8118 (Redburn), 10712 (White Jacket), 34970 (Pierre), 21816 (The Confidence-Man), 15859 (The Piazza Tales), 76513 (Billy Budd), 13720 (Mardi Vol 1), 13721 (Mardi Vol 2), 12384 (Battle-Pieces), 12841 (John Marr and Other Poems)
- **Lovecraft**: 68283 (The Call of Cthulhu), 70652 (At the Mountains of Madness), 50133 (The Dunwich Horror), 31469 (The Shunned House), 73181 (The Shadow Over Innsmouth), 68236 (The Colour Out of Space), 73547 (The Case of Charles Dexter Ward), 68553 (The Festival), 72966 (The Horror at Red Hook), 73230 (The Thing on the Doorstep), 71167 (Through the Gates of the Silver Key), 70486 (The Lurking Fear), 73233 (The Haunter of the Dark), 73177 (Cool Air), 70478 (The Silver Key), 70912 (The Curse of Yig), 68547 (He), 73182 (The Quest of Iranon)
- **Conrad**: 219 (Heart of Darkness), 21435 (Lord Jim), 2021 (Nostromo), 974 (The Secret Agent), 220 (The Secret Sharer), 2480 (Under Western Eyes), 6378 (Victory), 1142 (Typhoon), 17731 (The Nigger of the Narcissus), 525 (Youth), 451 (The Shadow Line), 1202 (Tales of Unrest), 2305 (A Set of Six), 1058 (The Mirror of the Sea), 638 (An Outcast of the Islands)
- **Joyce**: 4300 (Ulysses), 2814 (Dubliners), 4217 (A Portrait of the Artist as a Young Man), 2817 (Chamber Music), 55945 (Exiles)
- **Hawthorne**: 33 (The Scarlet Letter), 77 (The House of the Seven Gables), 2081 (The Blithedale Romance), 512 (Mosses from an Old Manse), 13707 (Twice-Told Tales), 2181 (The Marble Faun Vol 1), 1916 (The Great Stone Face), 8090 (Our Old Home)
- **Twain**: 76 (Huckleberry Finn), 74 (Tom Sawyer), 1837 (The Prince and the Pauper), 245 (Life on the Mississippi), 3176 (The Innocents Abroad), 86 (A Connecticut Yankee), 3177 (Roughing It), 2895 (Following the Equator), 3178 (The Gilded Age), 3186 (The Mysterious Stranger), 3189 (Sketches New and Old), 70 (What Is Man?)
- **Carroll**: 11 (Alice's Adventures in Wonderland), 12 (Through the Looking-Glass), 13 (The Hunting of the Snark), 620 (Sylvie and Bruno), 651 (Phantasmagoria), 28696 (Symbolic Logic), 29042 (A Tangled Tale)
- **Wilde**: 174 (The Picture of Dorian Gray), 844 (The Importance of Being Earnest), 885 (An Ideal Husband), 790 (Lady Windermere's Fan), 854 (A Woman of No Importance), 921 (De Profundis), 902 (The Happy Prince), 14522 (The Canterville Ghost), 773 (Lord Arthur Savile's Crime), 1057 (Poems with Ballad of Reading Gaol), 887 (Intentions), 14062 (Miscellanies)

**French (original language only):**

- **Baudelaire**: 6099 (Les Fleurs du Mal), 13792 (Journaux intimes), 26710 (Les Epaves)
- **Verne**: 20973 (Le Tour du monde en 80 jours), 4791 (Voyage au Centre de la Terre), 14287 (L'Ile mysterieuse), 5097 (Vingt mille Lieues sous les Mers), 38674 (De la Terre a la Lune)
- **Dumas**: 17989 (Le Comte de Monte-Cristo Tome I), 13951 (Les Trois Mousquetaires)
- **Flaubert**: 14155 (Madame Bovary), 57525 (Trois Contes), 66505 (Bouvard et Pecuchet)
- **Proust**: 2650 (Du cote de chez Swann), 2998 (A l'ombre des jeunes filles en fleurs Pt 1), 2999 (Pt 2), 3000 (Pt 3), 8946 (Le Cote de Guermantes Pt 1), 12999 (Pt 2), 13743 (Pt 3), 15288 (Sodome et Gomorrhe Pt 1), 15075 (Pt 2), 58698 (Les Plaisirs et les Jours), 60720 (La Prisonniere), 64145 (Pastiches et Melanges), 64427 (Albertine disparue Vol 1), 74090 (Le Temps retrouve T1), 74091 (T2)

**Portuguese (original language only):**

- **Machado de Assis**: 55752 (Dom Casmurro), 54829 (Memorias Posthumas de Braz Cubas), 55682 (Quincas Borba), 57001 (Papeis Avulsos), 53101 (A Mao e a Luva), 33056 (Historias Sem Data), 67162 (Helena), 67935 (Reliquias de Casa Velha), 67780 (Yaya Garcia), 55797 (Memorial de Ayres), 56737 (Esau e Jacob), 61653 (Poesias Completas)
- **Eca de Queiros**: 40409 (Os Maias), 31971 (O Crime do Padre Amaro), 42942 (O Primo Basilio), 17515 (A Reliquia), 18220 (A Cidade e as Serras), 23145 (A Illustre Casa de Ramires), 27637 (A Correspondencia de Fradique Mendes), 16384 (O Mandarim), 31347 (Contos), 25641 (Cartas de Inglaterra), 68986 (Prosas Barbaras)
- **Camoes**: 3333 (Os Lusiadas), 31509 (Obras Completas T2), 37192 (Obras Completas T3)

**Totals**: ~80 English works, ~25 French works, ~26 Portuguese works (~131 texts)

## Step 2: Extract Words (`src/extract_words.py`)

- Lowercase all text
- For French/Portuguese: strip diacritics using `unicodedata.normalize('NFKD')` + remove combining marks (category `Mn`), producing ASCII-only words
- Tokenize with `re.findall(r'[a-z]+', text)`
- Filter by length: `min_word_length` to `max_word_length` (configured in `config.toml`, default 4-9)
- Track word frequency and number of source authors per word
- Output: `data/words/{lang}/all_words.txt` (unique, sorted) and `data/words/{lang}/word_frequencies.csv` (word, count, num_authors)
- Maintain a mapping from stripped form to original accented form(s) for validation

## Step 3: Validate Words (`src/validate_words.py`)

Multi-tier validation, a word passes if it clears any tier:

1. **wordfreq**: `zipf_frequency(word, lang) > 0` (using the original accented form for French/Portuguese lookups)
2. **pyspellchecker**: `word in spell.known([word])`
3. **Multi-author heuristic**: word appears in 3+ authors' texts (catches archaic/specialized vocabulary that mainstream dictionaries miss, which is exactly what we want)

Output: `data/validated/{lang}_validated.txt` and `data/validated/{lang}_rejected.txt` (for manual review).

## Step 4: Score Typing Difficulty (`src/score_typing.py`)

Uses a simplified Carpalx-inspired model defined in `src/typing_model.py`.

### Typing Model

Informed by the Carpalx triad effort model and the Typability Index regression (PMC12901113), simplified for per-word scoring:

**Per-key base effort** incorporates:

- Row distance from home row (home=0, top=+0.5, bottom=+0.8)
- Finger strength (index=1.0, middle=1.1, ring=1.3, pinky=1.6)
- Lateral stretch penalty for center column keys (+0.3)

**Bigram transition effort** incorporates:

- Same-finger penalty (worst: 2.5+, scaled by row distance)
- Same-hand outward roll penalty (+0.5)
- Same-hand inward roll bonus (-0.5)
- Same-hand row change penalty (+0.3 per row)
- Hand alternation bonus (-0.3)

**Word score** = `(sum of key efforts + sum of bigram efforts) / word length`

Filter threshold: `max_effort_per_char` (default 2.5, tunable). Words above this are removed.

Output: `data/scored/{lang}_scored.tsv` (word, effort_score).

### Key Effort Values

```text
Home row:  a=1.6  s=1.3  d=1.1  f=1.0  g=1.3  h=1.3  j=1.0  k=1.1  l=1.3
Top row:   q=2.4  w=1.95 e=1.65 r=1.5  t=1.8  y=1.8  u=1.5  i=1.65 o=1.95 p=2.4
Bottom:    z=2.88 x=2.34 c=1.98 v=1.8  b=2.1  n=1.8  m=1.8
```

## Step 5: Build Final List (`src/build_list.py`)

1. Load scored words for all languages
2. Cross-language deduplication (keep first occurrence, priority: en > fr > pt)
3. Prefix-word removal: sort by length, use a trie to find prefix conflicts, remove the shorter word
4. Sort alphabetically
5. Output `output/word-list.txt` (one word per line, phraze-compatible)
6. Print statistics: total words, bits of entropy per word (`log2(count)`), mean word length, mean typing effort

Target: 10,000+ words (~13.3 bits of entropy per word).

## Configuration (`config.toml`)

All ebook IDs populated from the Source Authors section above. Format:

```toml
[general]
min_word_length = 4
max_word_length = 9
target_list_size = 10000

[typing]
max_effort_per_char = 2.5

[languages.en]
name = "English"
[languages.en.sources]
melville = [2701, 11231, 1900, 4045, ...]
lovecraft = [68283, 70652, 50133, ...]
# ... etc
```

## Dependencies (`pyproject.toml`)

```toml
[project]
name = "word-lists"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "wordfreq>=3.0",
    "pyspellchecker>=0.8",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4"]
```

## Verification

1. **Entropy**: `log2(list_length)` >= 13 bits (8,192+ words)
2. **Typing scores**: spot-check that "hand", "jade" score low; "quizzical", "pizzazz" score high
3. **Phraze integration**: `phraze --custom-list output/word-list.txt -w 4` works and reports expected entropy
4. **Diacritics**: no characters outside `[a-z]` in output
5. **Length bounds**: all words satisfy min/max constraints
6. **Prefix-free**: no word in the list is a prefix of another
7. **Sample review**: manually check 100 random words for validity

## Implementation Order

1. Project setup: `pyproject.toml`, `config.toml`, `Makefile`, `.gitignore`, directory structure
2. `src/gutenberg.py` + `src/fetch_texts.py` (test with one book per language)
3. `src/extract_words.py` with diacritics stripping
4. `src/typing_model.py` with unit tests (self-contained, can develop independently)
5. `src/validate_words.py`
6. `src/score_typing.py`
7. `src/build_list.py` with prefix-free removal
8. Full pipeline run, review output, tune parameters
9. README update

## Critical Files

- `src/typing_model.py`: most novel component, needs careful testing
- `src/extract_words.py`: core data pipeline, shapes everything downstream
- `src/validate_words.py`: determines list quality; multi-tier approach must balance inclusion of interesting vocabulary against garbage
- `config.toml`: all ebook IDs and thresholds; errors propagate everywhere
- `src/build_list.py`: produces the actual deliverable
