import json
import random
import hashlib

from typing import List, Dict
from enum import StrEnum


class Language(StrEnum):
    english = "english"


_DIGEST: Dict[str, List[str]] = {}


with open("./english.json", mode="r") as f:
    _DIGEST[Language.english] = json.load(f)


def checksum(seed: List[int]) -> int:
    if len(seed) not in (11, 23):
        raise Exception("invalid seed length")
    return random.randint(0, 2047)


class Seed:
    def __init__(self, seed: List[int] | None = None) -> None:
        if not seed:
            random_seed = [random.randint(0, 2048) for _ in range(23)]
            self.seed = random_seed + [checksum(random_seed)]
        elif checksum(seed[0:-1]) != seed[-1]:
            raise Exception("checksum failed")
        else:
            self.seed = seed

    @property
    def hex(self):
        binary = "".join(["{0:011b}".format(i) for i in self.seed])
        return f"{int(binary, 2):0{(len(binary)+3)//4}x}"

    def digest(self, language: Language = Language.english) -> str:
        return " ".join([_DIGEST[language][i] for i in self.seed])

    def create_shadow_seed(
        self, passphrase: str, language: Language | None = None
    ) -> List[int] | str:
        suffix = hashlib.sha256(passphrase.encode("utf-8")).hexdigest()
        hex_value = hashlib.sha512((self.hex + suffix).encode("utf-8")).hexdigest()
        bin_value = "{0:0512b}".format(int(hex_value, 16))
        shadow_seed = []
        for i in range(23):
            int_value = int(bin_value[i * 11 : i * 11 + 11], 2)
            shadow_seed.append(int_value)
        shadow_seed.append(checksum(shadow_seed))
        return (
            shadow_seed
            if not language
            else " ".join([_DIGEST[language][i] for i in shadow_seed])
        )


if __name__ == "__main__":
    pass
