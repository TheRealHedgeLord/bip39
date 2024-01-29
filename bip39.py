from __future__ import annotations

import random
import hashlib

from functools import cache
from typing import List

from lang import Lang, seed_to_words


@cache
def checksum(bits256: str) -> List[int]:
    if len(bits256) != 256:
        raise Exception("invalid bit length")
    checksum_hex = hashlib.sha256(
        int(bits256, 2).to_bytes(length=32, byteorder="big", signed=False)
    ).hexdigest()[0:2]
    complete_seed_bits = bits256 + "{0:08b}".format(int(checksum_hex, 16))
    return [int(complete_seed_bits[i * 11 : i * 11 + 11], 2) for i in range(24)]


class Wallet:
    _instances = {}

    @staticmethod
    def new() -> Wallet:
        random_uint256 = random.randint(0, 2**256 - 1)
        return Wallet._create_instance(random_uint256)

    @staticmethod
    def from_seed(seed: List[int]) -> Wallet:
        bits256 = ("".join(["{0:011b}".format(i) for i in seed]))[0:256]
        if checksum(bits256) != seed:
            raise Exception("invalid checksum")
        uint256 = int(bits256, 2)
        if uint256 in Wallet._instances:
            return Wallet._instances[uint256]
        else:
            return Wallet(uint256)

    @staticmethod
    def _create_instance(uint256: int) -> Wallet:
        if uint256 in Wallet._instances:
            return Wallet._instances[uint256]
        else:
            return Wallet(uint256)

    def __init__(self, uint256: int) -> None:
        if uint256 in Wallet._instances:
            raise Exception("duplication error")
        Wallet._instances[uint256] = self
        self.bytes = uint256.to_bytes(length=32, byteorder="big", signed=False)
        self.seed = checksum("{0:0256b}".format(uint256))

    @cache
    def words(self, lang: Lang = Lang.English) -> str:
        return seed_to_words(self.seed, lang)

    def create_shadow_wallet(self, passphrase: str) -> Wallet:
        suffix = hashlib.sha256(passphrase.encode("utf-8")).digest()
        shadow_seed_bytes = hashlib.sha256(self.bytes + suffix).digest()
        shadow_seed_uint256 = int.from_bytes(
            shadow_seed_bytes, byteorder="big", signed=False
        )
        return Wallet._create_instance(shadow_seed_uint256)
