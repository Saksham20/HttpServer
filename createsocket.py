import socket
from threading import Thread
from queue import Queue
from ServerBuilding import HttpWorker
import warnings


# note: byte strings are just a string of bytes. using b'', python automatically
#  encodes the typed string using ascii.:
#  b'string' == 'string'.encode('ascii'/'utf8')
#  b'string' != 'string'.encode('utf16')

class HTTPServer:

    def __init__(self, host: str = "127.0.0.1",
                 port: int = 8000,
                 no_connections: int = 16,
                 concurrent: bool = True):
        self.port = port
        self.host = host
        self.no_connections = no_connections
        self._task_queue = Queue(maxsize=self.no_connections)
        self._http_worker = HttpWorker(self._task_queue, concurrent=concurrent)
        self._server_start = False
        self._mount = False

    def start_server(self):
        if not self._server_start:
            th = Thread(target=self._bind_socket, args=())
            th.start()
            self._server_start = True
        else:
            print('server already started')

    def _bind_socket(self):
        with socket.socket() as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(self.no_connections)
            print(f'listning to requests on {self.host} and {self.port}')
            count = 0
            while True:
                count += 1
                if self._task_queue.full():
                    warnings.warn(f'DDOS :\'( , serving {self.no_connections} connections!')
                    continue
                client_sock, client_addr = server_sock.accept()
                print(f'\nadding {client_addr} to queue\n')
                self._task_queue.put((client_sock, client_addr))

    def mount(self):
        if not self._mount:
            th = Thread(target=self._http_worker.start, args=())
            th.start()
            self._mount = True
        else:
            print('server already mounted')


if __name__ == '__main__':
    server = HTTPServer(concurrent=True)
    server.start_server()
    server.mount()
