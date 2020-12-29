import socket
from ServerBuilding import *

HOST = "127.0.0.1"
PORT = 8000

# note: byte strings are just a string of bytes. using b'', python automatically
#  encodes the typed string using ascii.:
#  b'string' == 'string'.encode('ascii'/'utf8')
#  b'string' != 'string'.encode('utf16')


RESPONSE = b'''\
HTTP/2 200 OK
Content-type: text/html
Content-length: 100

<h1 style="text-align: center;color: blue;">Hello!</h1>'''.replace(b"\n", b"\r\n")




with socket.socket() as server_sock:
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    server_sock.bind((HOST, PORT))
    server_sock.listen(1)
    print(f'listning to requests on {HOST} and {PORT}')

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f'listning to {client_addr}')
        try:
            soc_details = Request.get_socket_details(client_sock)
            print(f'method used:{soc_details.method}\n'
                  f'addr:{soc_details.path}\n')
            for key, value in soc_details.headers.items():
                print(f'{key}:{value}')
            with client_sock:
                serve_file(client_sock, path=soc_details.path)
        except:
            with client_sock:
                client_sock.sendall(BAD_REQUEST_RESPONSE)