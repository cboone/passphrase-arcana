.PHONY: all clean fetch extract validate score build

all: build

fetch:
	uv run src/fetch_texts.py

extract: fetch
	uv run src/extract_words.py

validate: extract
	uv run src/validate_words.py

score: validate
	uv run src/score_typing.py

build: score
	uv run src/build_list.py

clean:
	rm -rf data/raw data/words data/validated data/scored

clean-output:
	rm -rf output/*

test:
	uv run pytest tests/ -v
