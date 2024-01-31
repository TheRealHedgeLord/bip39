import os
import json

from enum import StrEnum
from typing import List

_LANG = {}

for file_name in os.listdir("./wordlists/"):
    if file_name[-5::] == ".json":
        with open(f"./wordlists/{file_name}", mode="r") as f:
            _LANG[file_name[0:-5]] = json.load(f)


class Lang(StrEnum):
    English = "English"


def seed_to_words(seed: List[int], lang: Lang) -> str:
    return " ".join([_LANG[lang][i] for i in seed])


def words_to_seed(words: str, lang: Lang) -> List[int]:
    return [_LANG[lang].index(word) for word in words.split(" ") if word]
