#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from binascii import hexlify, unhexlify

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class RSACipher:
    def __init__(self):
        try:
            self.public_key, self.private_key = self._GenerateKeyPair()
        except Exception as e:
            print(f"[Error] Failed to generate RSA key pair: {e}")

    @staticmethod
    def _GenerateKeyPair() -> tuple:
        try:
            keyPair = RSA.generate(1024)
            pub_key = keyPair.publickey()
            public_key = pub_key.export_key()
            return public_key, keyPair
        except Exception as e:
            print(f"[Error] Failed to generate RSA key pair: {e}")
            return None, None

    @staticmethod
    def Encrypt(public_key_pem, data) -> bytes:
        try:
            public_key = RSA.import_key(public_key_pem)
            encryptor = PKCS1_OAEP.new(public_key)
            encrypted = encryptor.encrypt(data)
            return hexlify(encrypted)
        except Exception as e:
            print(f"[Error] Failed to encrypt data: {e}")
            return b""

    def Decrypt(self, data) -> bytes:
        try:
            decryptor = PKCS1_OAEP.new(self.private_key)
            decrypted = decryptor.decrypt(unhexlify(data))
            return decrypted
        except Exception as e:
            print(f"[Error] Failed to decrypt data: {e}")
            return b""

class AESCipher:
    def __init__(self, key):
        self.key = key

    def Encrypt(self, data: bytes) -> bytes:
        try:
            iv = get_random_bytes(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            if isinstance(data, str):
                data = data.encode("utf8")
            return hexlify(iv + cipher.encrypt(pad(data, AES.block_size)))
        except Exception as e:
            print(f"[Error] Failed to encrypt data with AES: {e}")
            return b""

    def Decrypt(self, data: bytes) -> bytes:
        try:
            raw = unhexlify(data)
            cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
            return unpad(cipher.decrypt(raw[AES.block_size:]), AES.block_size)
        except Exception as e:
            print(f"[Error] Failed to decrypt data with AES: {e}")
            return b""
