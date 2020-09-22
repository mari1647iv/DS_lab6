#!/usr/bin/env python3

import socket
import tqdm
import os

host = 'localhost'  # The server's hostname or IP address
PORT = 8800        # The port used by the server
SEPARATOR = "<SEPARATOR>"
filename = "/home/marina/lab6/data.txt"
filesize = os.path.getsize(filename)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((host, PORT))
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())
    #s.send(b'Hello, world')
    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(4096)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    data = s.recv(1024)
    # close the socket
    s.close()

print('Received', repr(data))