from pathlib import Path

CORPUS_PATH = Path("data/marpa_corpus_v2.txt")


def load_text():
    return CORPUS_PATH.read_text(encoding="utf-8")


def build_tokenizer(text):
    chars = sorted(list(set(text)))
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}

    def encode(s):
        return [stoi[c] for c in s if c in stoi]

    def decode(tokens):
        return "".join([itos[i] for i in tokens])

    return chars, stoi, itos, encode, decode