# This file is for decrypting the AES ECB block from the given ciphertext
import Crypto
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

sym_key: bytes = b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
ciphertext: bytes = b"\xf5\x27\x7b\x20\xc7\x09\x61\xbd\x0c\xa4\xac\x07\x0b\x15\x69\x28"

def decrypt_aes_ecb(ciphertext: hex, sym_key: hex) -> hex:
    """
    This function decrypts the AES ECB block from the given ciphertext
    :param ciphertext: ciphertext to be decrypted
    :param sym_key: symmetric key to be used for decryption
    :return: decrypted ciphertext
    """
    cipher = AES.new(sym_key, AES.MODE_ECB)
    return cipher.decrypt(ciphertext)

plaintext: bytes = decrypt_aes_ecb(ciphertext, sym_key)

plaintext_str: str = plaintext.decode("utf-8")

print(plaintext_str)