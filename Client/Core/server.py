#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from os import path
from time import sleep
from colorama import Fore
from binascii import hexlify
from zlib import compress, decompress
from socket import socket, AF_INET, SOCK_STREAM
from Core.encryption import RSACipher, AESCipher

rsa = RSACipher()
BUFFER_SIZE = 1024 * 20

class ConnectServer:
    """ Connected to server """
    def __init__(self, host: str, port: int):
        while True:
            try:
                # Create socket & connection
                self.socket = socket(AF_INET, SOCK_STREAM)
                self.socket.connect((host, port))
                # Try to exchange encryption keys
                self.ExchangeEncryptionKeys()
            except Exception as error:
                print(f"{Fore.RED}[Client]{Fore.WHITE} Failed to exchange encryption keys with server: {error}{Fore.RESET}")
                self.socket.close()
                sleep(2)
            else:
                break

    """ Send encrypted command from client """
    def Send(self, data: str) -> None:
        try:
            encrypted = self.aes.Encrypt(data)
            self.socket.send(encrypted)
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to send data: {e}{Fore.RESET}")

    """ Get encrypted data from client """
    def Read(self) -> str:
        try:
            encrypted = self.socket.recv(BUFFER_SIZE)
            decrypted = self.aes.Decrypt(encrypted)
            return decrypted.decode("utf8")
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to read data: {e}{Fore.RESET}")
            return ""

    """ Disconnect client """
    def Disconnect(self):
        try:
            print(f"{Fore.GREEN}[Client <= Server]{Fore.WHITE} Disconnecting ...{Fore.RESET}")
            self.socket.close()
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to disconnect: {e}{Fore.RESET}")

    """ Send file to server """
    def SendFile(self, filename):
        try:
            print(f"{Fore.GREEN}[Client => Server]{Fore.WHITE} Sending file: {path.abspath(filename)}{Fore.RESET}")
            # Check if file exists
            if not path.exists(filename):
                return f"{Fore.GREEN}[Client => Server]{Fore.WHITE} File not found!{Fore.RESET}"
            # Read file content
            with open(filename, "rb") as file:
                data = file.read()
                encrypted = self.aes.Encrypt(data)
                compressed = compress(encrypted)
                size = len(compressed)
                self.Send(f"BEGIN_FILE_TRANSFER*{size}*{filename}")  # Send command, size, filename
                sleep(0.1)
                self.socket.sendall(compressed)
            sleep(0.1)
            self.Send("DONE_FILE_TRANSFER")
            return f"{Fore.GREEN}[Client => Server]{Fore.WHITE} File sent!{Fore.RESET}"
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to send file: {e}{Fore.RESET}")
            return f"{Fore.RED}[Error]{Fore.WHITE} Failed to send file: {filename}{Fore.RESET}"

    """ Receive file from server """
    def ReceiveFile(self):
        try:
            command = self.Read()
            if command.startswith("BEGIN_FILE_TRANSFER"):
                splt = command.split("*")
                size = int(splt[1])
                filename = path.basename(splt[2])
                print(f"{Fore.GREEN}[Client => Server]{Fore.WHITE} Receiving file: {filename}{Fore.RESET}")
                # Receive compressed and encrypted file bytes
                content = b""
                while True:
                    data = self.socket.recv(size)
                    if len(data) == 96:
                        break
                    if not data:
                        break
                    content += data
                # Decompress, Decrypt, and write bytes
                with open(filename, "wb") as file:
                    print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Loaded bytes: {len(content)}{Fore.RESET}")
                    decompressed = decompress(content)
                    print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Decompressed bytes: {len(decompressed)}{Fore.RESET}")
                    decrypted = self.aes.Decrypt(decompressed)
                    print(f" {Fore.LIGHTGREEN_EX}--- {Fore.LIGHTYELLOW_EX}Decrypted bytes: {len(decrypted)}{Fore.RESET}")
                    file.write(decrypted)
                print(f"{Fore.GREEN}[Client => Server]{Fore.WHITE} File {filename} saved on disk!{Fore.RESET}")
                return path.abspath(filename)
            else:
                print(f"{Fore.GREEN}[Client => Server]{Fore.WHITE} Error: {command}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to receive file: {e}{Fore.RESET}")

    """ Exchange encryption keys """
    def ExchangeEncryptionKeys(self):
        try:
            # Send client RSA public key to server
            if self.socket.recv(BUFFER_SIZE) == b"GET_CLIENT_RSA_PUBLIC_KEY":
                self.socket.send(rsa.public_key)
                print(f"{Fore.GREEN}[Client => Server]{Fore.WHITE} RSA public key sent to server:\n" +
                      f"{Fore.LIGHTWHITE_EX}{hexlify(rsa.public_key).decode()}{Fore.RESET}")
            # Receive RSA public key from server
            self.socket.send(b"GET_SERVER_RSA_PUBLIC_KEY")
            self.server_rsa_public_key = self.socket.recv(BUFFER_SIZE)
            print(f"{Fore.GREEN}[Client <= Server]{Fore.WHITE} RSA public key received from server:\n" +
                  f"{Fore.LIGHTWHITE_EX}{hexlify(self.server_rsa_public_key).decode()}{Fore.RESET}")
            # Receive AES key from server
            self.socket.send(b"GET_SERVER_AES_KEY")
            self.server_aes_key = rsa.Decrypt(self.socket.recv(BUFFER_SIZE))
            self.aes = AESCipher(self.server_aes_key)
            print(f"{Fore.GREEN}[Client <= Server]{Fore.WHITE} Encrypted AES key received from server:\n" +
                  f"{Fore.LIGHTWHITE_EX}{hexlify(self.server_aes_key).decode()}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}[Error]{Fore.WHITE} Failed to exchange encryption keys: {e}{Fore.RESET}")
            self.socket.close()
