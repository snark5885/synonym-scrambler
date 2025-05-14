# Synonym Scrambler

A command-line tool to scramble input text by replacing words with contextually similar synonyms, without using an LLM. Built to obfuscate writing patterns and confuse AI detectors.

---

## Features

- No AI/LLM usage — pure NLP stack
- Replaces **nouns, verbs, adjectives, and adverbs**
- Uses **WordNet** via `nltk` for synonym sourcing
- Ensures replacements match **tense and plurality**
- Preserves sentence structure while introducing variation
- Customizable replacement rate
- Kind of bad - spits out results that are readable but awkward and not always contextually accurate

---

## Usage

```bash
python synonym_scrambler.py input.txt --rate 0.6 --output out.txt
```

---

## Setup

```bash
pip install -r requirements.txt
python -m nltk.downloader wordnet
python -m spacy download en_core_web_sm
```

---

## How It Works

1. Identifies replaceable parts of speech: nouns, verbs, adjectives, and adverbs
2. Finds synonyms using WordNet via `nltk`
3. Filters based on vector similarity, morphology, and word frequency
4. Replaces a percentage of eligible words with contextually similar synonyms


---

## License

MIT License