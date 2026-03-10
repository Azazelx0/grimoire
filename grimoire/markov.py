"""Markov chain password generator — train on wordlists, generate probable passwords."""

import random
from collections import defaultdict


class MarkovModel:
    def __init__(self, order: int = 2):
        self.order = order
        self.chains: dict[str, list[str]] = defaultdict(list)
        self.starters: list[str] = []

    def train(self, words: list[str]):
        for word in words:
            if len(word) < self.order:
                continue
            prefix = word[:self.order]
            self.starters.append(prefix)
            for i in range(len(word) - self.order):
                key = word[i:i + self.order]
                next_char = word[i + self.order] if i + self.order < len(word) else "\x00"
                self.chains[key].append(next_char)

    def generate_word(self, min_len: int = 6, max_len: int = 16) -> str:
        if not self.starters:
            return ""

        word = random.choice(self.starters)

        for _ in range(max_len - self.order):
            key = word[-self.order:]
            options = self.chains.get(key, [])
            if not options:
                break
            next_char = random.choice(options)
            if next_char == "\x00":
                break
            word += next_char

        if len(word) < min_len:
            return self.generate_word(min_len, max_len)

        return word[:max_len]

    def generate(self, count: int = 1000, min_len: int = 6, max_len: int = 16) -> list[str]:
        seen = set()
        results = []
        attempts = 0
        max_attempts = count * 10

        while len(results) < count and attempts < max_attempts:
            word = self.generate_word(min_len, max_len)
            attempts += 1
            if word and word not in seen:
                seen.add(word)
                results.append(word)

        return results


def train_from_file(path: str, order: int = 2) -> MarkovModel:
    words = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)

    model = MarkovModel(order=order)
    model.train(words)
    return model


def train_from_words(words: list[str], order: int = 2) -> MarkovModel:
    model = MarkovModel(order=order)
    model.train(words)
    return model
