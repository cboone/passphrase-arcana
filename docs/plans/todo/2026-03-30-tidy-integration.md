# Replace build step with tidy, add homophones and archaic filtering

## Context

The current `build_list.py` does prefix/suffix word removal in Python, which is the least sophisticated approach to ensuring unique decodability. sts10's `tidy` tool (already installed at `~/.cargo/bin/tidy`) offers Schlinkert pruning, which uses the Sardinas-Patterson algorithm to achieve unique decodability while keeping ~31% more words (32,513 vs 24,880).

Additionally, the list contains homophone pairs (discrete/discreet, principal/principle) that cause confusion when remembering a passphrase, and a handful of archaic verb forms (bloweth, callest) that slipped through validation.

## Changes

### 1. Generate homophones CSV from CMU Pronouncing Dictionary

Create `src/generate_homophones.py` that:
- Downloads the CMU dict from `https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict`
- Groups words by pronunciation (stripping stress markers)
- Writes homophone pairs as CSV to `data/homophones.csv` (one pair per line, e.g. `discreet,discrete`)
- For groups of 3+, writes all pairwise combinations
- This is a one-time generation step, not part of the regular pipeline. The CSV is committed to the repo and maintained as a data file.

### 2. Create archaic forms reject list

Create `data/archaic_rejects.txt` containing the 7 archaic verb forms that pass validation:
```text
bloweth
callest
desirest
listeth
requireth
sleepest
talkest
```

This is a hand-curated list. New entries can be added manually as they're found.

### 3. Rewrite `src/build_list.py` to use tidy

The current build_list.py (140 lines of Python: load scored words, blocklist filtering, prefix removal, suffix removal, statistics) is replaced by a script that:

1. Extracts words from the scored TSV (strip header and effort column)
2. Writes a temporary plain word list
3. Calls tidy with:
   - `-r blocklist.txt` (reject offensive words)
   - `-r data/archaic_rejects.txt` (reject archaic forms)
   - `--homophones data/homophones.csv` (remove confusable homophones)
   - `-K` (Schlinkert pruning for unique decodability)
   - `-AAAA` (print full attributes)
   - `-o passphrase-arcana.txt` (output)
4. Reads tidy's attribute output and prints stats

The Python prefix/suffix removal code (~90 lines) is deleted entirely. tidy handles it better.

Alternatively, the build step could be a pure Makefile recipe calling tidy directly. But keeping a Python wrapper preserves the multi-language dedup logic and statistics output that match the other pipeline steps.

### 4. Update Makefile

No structural changes needed. The `build` target still calls `uv run src/build_list.py`. The script internally calls tidy.

### 5. Update docs

- `docs/pipeline.md`: Update Step 6 to describe tidy, Schlinkert pruning, homophone removal
- `README.md`: Update word count, entropy, attributes table once final numbers are known
- `AGENTS.md`: Note tidy dependency in Development section

## Files to create

- `src/generate_homophones.py` (one-time script)
- `data/homophones.csv` (generated, committed)
- `data/archaic_rejects.txt` (hand-curated)

## Files to modify

- `src/build_list.py` (rewrite to shell out to tidy)
- `docs/pipeline.md` (update Step 6)
- `README.md` (update stats after rebuild)
- `AGENTS.md` (note tidy dependency)

## Verification

1. `make test` to ensure existing tests pass
2. `make build` to rebuild with tidy
3. Compare word count: expect ~32,000 words (up from 24,880)
4. Verify tidy reports "Uniquely decodable?: true"
5. Spot-check that homophones are removed (discrete/discreet should not both be present)
6. Spot-check that archaic forms are removed (bloweth, callest gone)
7. Generate sample passphrases with `phraze`
8. Run `arcana --setup` and `arcana` to verify the full flow
