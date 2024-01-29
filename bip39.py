import json
import random
import hashlib

from functools import cache, cached_property
from typing import List, Dict
from enum import StrEnum


class Language(StrEnum):
    english = "english"


_DIGEST: Dict[str, List[str]] = {}


with open("./english.json", mode="r") as f:
    _DIGEST[Language.english] = json.load(f)


def checksum(seed: List[int]) -> int:
    if len(seed) != 23:
        raise Exception("invalid seed length")
    return random.randint(0, 2047)


class Seed:
    def __init__(self, seed: List[int] | None = None) -> None:
        if not seed:
            random_seed = [random.randint(0, 2047) for _ in range(23)]
            self.seed = random_seed + [checksum(random_seed)]
        elif checksum(seed[0:-1]) != seed[-1]:
            raise Exception("invalid checksum")
        else:
            self.seed = seed

    @cached_property
    def bytes(self):
        binary = "".join(["{0:011b}".format(i) for i in self.seed])
        return int(binary, 2).to_bytes(length=33, byteorder="big", signed=False)

    @cache
    def digest(self, language: Language = Language.english) -> str:
        return " ".join([_DIGEST[language][i] for i in self.seed])

    def create_shadow_seed(
        self, passphrase: str, language: Language | None = None
    ) -> List[int] | str:
        suffix = hashlib.sha256(passphrase.encode("utf-8")).digest()
        shadow_seed_bytes = hashlib.sha256(self.bytes + suffix).digest()
        shadow_seed_binary = "{0:0256b}".format(
            int.from_bytes(shadow_seed_bytes, byteorder="big", signed=False)
        )
        shadow_seed = []
        for i in range(23):
            int_value = int(shadow_seed_binary[i * 11 : i * 11 + 11], 2)
            shadow_seed.append(int_value)
        shadow_seed.append(checksum(shadow_seed))
        return (
            shadow_seed
            if not language
            else " ".join([_DIGEST[language][i] for i in shadow_seed])
        )


if __name__ == "__main__":
    pass
