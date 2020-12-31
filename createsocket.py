import socket
from threading import Thread

from ServerBuilding import *


# note: byte strings are just a string of bytes. using b'', python automatically
#  encodes the typed string using ascii.:
#  b'string' == 'string'.encode('ascii'/'utf8')
#  b'string' != 'string'.encode('utf16')

class HTTPServer:

    def __init__(self, host: str = "127.0.0.1", port: int = 8000, no_connections: int = 16):
        self.port = port
        self.host = host
        self.no_connections = no_connections

    def start_server(self):
        with socket.socket() as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(self.no_connections)
            print(f'listning to requests on {self.host} and {self.port}')
            thread_list = []
            count = 0
            while True:
                count += 1
                client_sock, client_addr = server_sock.accept()
                print(f'\nlistning to {client_addr}\n')
                thread_loop = Thread(target=self._serve_file,
                                     args=(client_sock,))
                thread_loop.start()
                thread_list.append(thread_loop)
                print(f'\ndeployed thread {count}\n{client_addr}\n')

    def _serve_file(self, client_sock):
        try:
            soc_request = Request.get_socket_details(client_sock)
            if "100-continue" in soc_request.headers.get("expect", ""):
                client_sock.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")
                return
            print(f'method used:{soc_request.method}\n'
                  f'addr:{soc_request.path}\n')
        except:
            with client_sock:
                client_sock.sendall(Response.bad_response)
                return
        try:
            soc_response = Response(soc_request)
            soc_response.send_response()
            print(f'\nresponse sent len:{len(soc_response.body)}, '
                  f'message:{soc_response.body[:10]}\nheader: {soc_response.header}')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    server = HTTPServer()
    server.start_server()
