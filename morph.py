import json
import random
import hashlib

with open("./english.json", mode="r") as f:
    _WORDS = json.load(f)


def generate_random_mnemonic(size: int = 24) -> str:
    words = []
    for i in range(size):
        words.append(_WORDS[random.randint(0, 2047)])
    return " ".join(words)


def word_to_bin(word: str) -> str:
    for i in range(len(_WORDS)):
        if word == _WORDS[i]:
            return "{0:011b}".format(i)
    raise Exception(f"{word} is not a BIP39 word")


def bin_to_word(binary: str) -> str:
    return _WORDS[int(binary, 2)]


def mnemonic_to_bin(mnemonic: str) -> str:
    words = mnemonic.split(" ")
    return "".join([word_to_bin(word) for word in words])


def bin_to_mnemonic(binary: str) -> str:
    words = []
    for i in range(int(len(binary) / 11)):
        words.append(bin_to_word(binary[i * 11 : i * 11 + 11]))
    return " ".join(words)


def passphrase_to_bin(passphrase: str) -> str:
    return "{0:0512b}".format(
        int(hashlib.sha512(passphrase.encode("utf-8")).hexdigest(), 16)
    )


def morph(mnemonic: str, passphrase: str) -> str:
    binary1 = mnemonic_to_bin(mnemonic)
    binary2 = passphrase_to_bin(passphrase)
    new_binary = ""
    for i in range(len(binary1)):
        char1 = binary1[i]
        char2 = binary2[i]
        if char1 == char2:
            new_binary += "0"
        else:
            new_binary += "1"
    return bin_to_mnemonic(new_binary)


if __name__ == "__main__":
    pass
