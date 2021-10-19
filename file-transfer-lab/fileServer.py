#! /usr/bin/env python3 

# Get library code from files in the parent directories
import os, sys, socket, re
sys.path.append("../lib")
sys.path.append("../stammer-proxy")
sys.path.append("../framed-echo")
import params
from framedSock import framedSend
from framedSock import framedReceive

# This is where our sent file will be dumped
os.chdir("File Drop")

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()
    
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)

# Continuously ask for files
while True:
    print("listening on:", bindAddr)
    s, addr = lsock.accept()
    
    # Fork so we can keep receiving files even after a connection is made
    rc = os.fork()
    if rc == 0:
        # at this point, a connection was successful
        print("connection rec'd from", addr)
        
        try:
            # First thing sent was the name of the file, open it
            nameOfReceivingFile = framedReceive(s, debug)
            
            # But if the file already exists, do nothing
            if os.path.exists(nameOfReceivingFile):
                print("File already exists")
                sys.exit(0)
            
            newFile = open(nameOfReceivingFile, "wb")
            
            # Continuously write to the file
            while True:
                payload = framedReceive(s, debug)
                if debug: print("rec'd: ", payload)
                if not payload:
                    break
                # If we reach the end of the file then everything has been written!
                if b"%%end" in payload:
                    newFile.close()
                    sys.exit(0)
                # Write everything received to the new file
                else:
                    newFile.write(payload)
        except:
            sys.exit(1)
            
# Zayra Padilla helped to guide me with some of the required logic for this lab when I got stuck
