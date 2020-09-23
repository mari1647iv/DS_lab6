import socket
from threading import Thread
import tqdm
import os
from time import sleep

SEPARATOR = "<SEPARATOR>"
clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data.encode()
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data.encode()
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            data = self.sock.recv(4096).decode()
            filename, filesize = data.split(SEPARATOR)
            buf1, buf2 = filename.split('.')
            filename = buf1+"_copy."+buf2
            filename = os.path.basename(filename)
            filesize = int(filesize)
            f = open(filename, "w")
            with tqdm.tqdm(f"Receiving {buf1+'.'+buf2}", total=filesize, unit="B", unit_scale=True) as pbar:
                while pbar.n != filesize:
                    bytes_read = self.sock.recv(4096).decode()
                    if not bytes_read:
                        pbar.close()
                        f.close()
                        break
                    f.write(bytes_read)
                    pbar.update(len(bytes_read))
                    pbar.refresh()
            pbar.close()
            f.close()
            if data:
                self._clear_echo(data)
                self._broadcast(data)
            else:
                # if we got no data – client has disconnected
                self._close()
                # finish the thread
                return

def main():
    print('Press Ctrl+C to exit')
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    print('Listening..')
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()

if __name__ == "__main__":
    main()
