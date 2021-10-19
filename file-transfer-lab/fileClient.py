#! /usr/bin/env python3


# Get library code from files in the parent directories
import socket, os, sys, re
sys.path.append("../lib")
sys.path.append("../stammer-proxy")
sys.path.append("../framed-echo")
import params
from framedSock import framedSend
from framedSock import framedReceive

# Have user choose whether or not to use proxy thing
print("Send a file with or without the proxy?")
print("\t1. With proxy")
print("\t2. Without proxy")
userChoice = input("Choice: ").strip()

if userChoice == str(1):
    port = "127.0.0.1:50000"
elif userChoice == str(2):
    port = "127.0.0.1:50001"
    
switchesVarDefaults = (
    (('-s', '--server'), 'server', port),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()
    
try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)
    
# Creating and connecting socket, from demo
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

# If no socket is returned, print error and leave
if s is None:
    print('could not open socket')
    sys.exit(1)
    
print("\nEnter path of file you want to send: ", end = '')
filePath = input()

# Get the contents of the file if it exists
try:
    fileData = open(filePath, "rb").read()
except FileNotFoundError:
    print("Bad file path, file does not exist")
    sys.exit(1)
    
if len(fileData) == 0:
    print("This file is empty")

# Determine the actual file name from the path provided
if "/" in filePath:
    actualFileName = re.split("/", filePath)[-1]
else:
    actualFileName = filePath
    
# The first thing sent is the name of the file: the server knows that
framedSend(s, actualFileName.encode(), debug)

# Send all the data contained in the file to the sever, but only 100 bytes at a time
while len(fileData) > 100:
    bytesChunk = fileData[:100]
    fileData = fileData[100:]
    framedSend(s, bytesChunk, debug)
# Tell the server that this is the end of the file
framedSend(s, fileData, debug)
framedSend(s, b"%%end")

# Zayra Padilla helped to guide me with some of the required logic for this lab when I got stuck
