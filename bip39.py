from __future__ import annotations

import secrets
import hashlib

from functools import cache
from typing import List
from enum import IntEnum

from lang import Lang, seed_to_words, words_to_seed


class SeedSize(IntEnum):
    seed_phrase_24 = 256
    seed_phrase_12 = 128


@cache
def checksum(bits: str) -> List[int]:
    if len(bits) == 256:
        checksum_hex = hashlib.sha256(
            int(bits, 2).to_bytes(length=32, byteorder="big", signed=False)
        ).hexdigest()[0:2]
        complete_seed_bits = bits + "{0:08b}".format(int(checksum_hex, 16))
        return [int(complete_seed_bits[i * 11 : i * 11 + 11], 2) for i in range(24)]
    elif len(bits) == 128:
        checksum_hex = hashlib.sha256(
            int(bits, 2).to_bytes(length=16, byteorder="big", signed=False)
        ).hexdigest()[0]
        complete_seed_bits = bits + "{0:04b}".format(int(checksum_hex, 16))
        return [int(complete_seed_bits[i * 11 : i * 11 + 11], 2) for i in range(12)]
    else:
        raise Exception("invalid seed size")


class Wallet:
    _instances = {SeedSize.seed_phrase_24: {}, SeedSize.seed_phrase_12: {}}

    @staticmethod
    def new(
        size: SeedSize = SeedSize.seed_phrase_24, user_entropy: str | None = None
    ) -> Wallet:
        if user_entropy:
            random_entropy_bytes = secrets.randbits(size).to_bytes(
                size // 8, byteorder="big", signed=False
            )
            user_entropy_bytes = hashlib.sha256(user_entropy.encode("utf-8")).digest()
            entropy = int(
                hashlib.sha256(random_entropy_bytes + user_entropy_bytes).hexdigest()[
                    0 : size // 4
                ],
                16,
            )
        else:
            entropy = secrets.randbits(size)
        return Wallet._get_instance(entropy, size)

    @staticmethod
    def from_seed(
        seed: List[int] | str,
        lang: Lang = Lang.English,
    ) -> Wallet:
        seed_list = words_to_seed(seed, lang) if type(seed) == str else seed
        if len(seed_list) == 24:
            size = SeedSize.seed_phrase_24
        elif len(seed_list) == 12:
            size = SeedSize.seed_phrase_12
        else:
            raise Exception("invalid seed size")
        bits = ("".join(["{0:011b}".format(i) for i in seed_list]))[0:size]
        if checksum(bits) != seed_list:
            raise Exception("invalid checksum")
        uint = int(bits, 2)
        return Wallet._get_instance(uint, size)

    @staticmethod
    def _get_instance(entropy: int, size: SeedSize) -> Wallet:
        if entropy in Wallet._instances[size]:
            return Wallet._instances[size][entropy]
        else:
            return Wallet(entropy, size)

    def __init__(self, entropy: int, size: SeedSize) -> None:
        if entropy in Wallet._instances[size]:
            raise Exception("duplication error")
        Wallet._instances[size][entropy] = self
        self._bytes = entropy.to_bytes(length=size // 8, byteorder="big", signed=False)
        self._seed = checksum(f"{entropy:0{size}b}")

    @property
    def bytes(self):
        return self._bytes

    @property
    def seed(self):
        return self._seed.copy()

    @cache
    def words(self, lang: Lang = Lang.English) -> str:
        return seed_to_words(self.seed, lang)

    def get_shadow_wallet(
        self, passphrase: str, size: SeedSize = SeedSize.seed_phrase_24
    ) -> Wallet:
        suffix = hashlib.sha256(passphrase.encode("utf-8")).digest()
        entropy = int(
            hashlib.sha256(self.bytes + suffix).hexdigest()[0 : size // 4], 16
        )
        return Wallet._get_instance(entropy, size)
