import json
import random
import hashlib

from functools import cache
from typing import List, Dict
from enum import StrEnum


class Language(StrEnum):
    english = "english"


_DIGEST: Dict[str, List[str]] = {}


with open("./english.json", mode="r") as f:
    _DIGEST[Language.english] = json.load(f)


@cache
def checksum(bits: str) -> List[int]:
    if len(bits) != 256:
        raise Exception("invalid bit length")
    checksum_hex = hashlib.sha256(
        int(bits, 2).to_bytes(length=32, byteorder="big", signed=False)
    ).hexdigest()[0:2]
    complete_seed_bits = bits + "{0:08b}".format(int(checksum_hex, 16))
    return [int(complete_seed_bits[i * 11 : i * 11 + 11], 2) for i in range(24)]


class Seed:
    def __init__(self, seed: List[int] | None = None) -> None:
        if not seed:
            random_256_bits = "{0:0256b}".format(random.randint(0, 2**256 - 1))
            self.bytes = int(random_256_bits, 2).to_bytes(
                length=32, byteorder="big", signed=False
            )
            self.seed = checksum(random_256_bits)
        else:
            bits_256 = ("".join(["{0:011b}".format(i) for i in seed]))[0:256]
            if checksum(bits_256) != seed:
                raise Exception("invalid checksum")
            self.bytes = int(bits_256, 2).to_bytes(
                length=32, byteorder="big", signed=False
            )
            self.seed = seed

    @cache
    def digest(self, language: Language = Language.english) -> str:
        return " ".join([_DIGEST[language][i] for i in self.seed])

    def create_shadow_seed(
        self, passphrase: str, language: Language | None = None
    ) -> List[int] | str:
        suffix = hashlib.sha256(passphrase.encode("utf-8")).digest()
        shadow_seed_bytes = hashlib.sha256(self.bytes + suffix).digest()
        shadow_seed_bits = "{0:0256b}".format(
            int.from_bytes(shadow_seed_bytes, byteorder="big", signed=False)
        )
        shadow_seed = checksum(shadow_seed_bits)
        return (
            shadow_seed
            if not language
            else " ".join([_DIGEST[language][i] for i in shadow_seed])
        )


if __name__ == "__main__":
    pass
