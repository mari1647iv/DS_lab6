#!/usr/bin/env python3

import socket
import tqdm
import os
import sys

filename = sys.argv[1]
host = sys.argv[2]  # The server's hostname or IP address
port = int(sys.argv[3])        # The port used by the server
SEPARATOR = "<SEPARATOR>"
filesize = os.path.getsize(filename)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, port))
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    #s.send(b'Hello, world')
    # start sending the file
    f = open(filename, "r")
    with tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024) as pbar:
        while pbar.n != filesize:
            bytes_read = f.read(4096)
            if not bytes_read:
                pbar.close()
                f.close()
                break
            s.sendall(bytes_read.encode())
            pbar.update(len(bytes_read))
            bytes_read = False
    pbar.close()
    f.close()
    data = s.recv(1024).decode()
    data = s.recv(1024).decode()
    # close the socket
    s.close()

print(data, ' (Received)')
