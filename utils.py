from typing import Dict, NamedTuple
import socket
from pathlib import Path
import mimetypes

# note: constants accodding to PEP8 are defined by capital letters and are present outside any function.
#  its a better practice to encapsulate all the useful action oriented code inside a function. Stuff that
#  are at the module level are these constants only!
FILE_RESPONSE_TEMPLATE = """\
HTTP/1.1 200 OK
Content-type: {content_type}
Content-length: {content_length}

""".replace("\n", "\r\n")

BAD_REQUEST_RESPONSE = b'''\
HTTP/2 400 Bad Request
Content-type: text/html
Content-length: 11

Bad Request'''.replace(b"\n", b"\r\n")


class Request(NamedTuple):
    headers: Dict[str, bytes]
    method: str
    path: str
    body: str

    @classmethod
    def get_socket_details(cls, sock: socket.socket, buff: int = 16_256):
        soc_data = sock.recv(buff).decode('utf8')
        soc_data_list = soc_data.split('\r\n')
        assert len(soc_data_list) >= 0, 'socket has no message'
        try:
            method, path, _ = soc_data_list[0].split(' ')
        except ValueError as e:
            raise Exception('not a valid http request_line')

        try:
            body_start_index = soc_data_list.index('')+2
        except ValueError:
            body_start_index = len(soc_data_list)-1
        # get header info:
        headers = {}
        for soc_data_line in soc_data_list[1:body_start_index-2]:
            try:
                head_key, head_val = soc_data_line.split(': ')
            except ValueError as e:
                raise Exception('incorrect header format of http')
            headers[head_key] = head_val
        # get body info:
        body = ''
        if len(soc_data_list)>body_start_index:
            body = '\n'.join(soc_data_list[body_start_index:])[2:]
        return cls(headers=headers, method=method, path=path, body=body)


def serve_file(serv_sock: socket, path: str = 'index.html') -> None:
    base_path = Path(__file__).parent/'views'
    if path == '/' or path == '':
        path = 'index.html'
    full_path = base_path/path
    if not full_path.is_file():
        serv_sock.sendall(BAD_REQUEST_RESPONSE)
        return
    with open(full_path, 'rb') as f:
        header_in = {}
        content_type = mimetypes.guess_type(full_path)[0]
        header_in['content_type'] = 'application/octet-stream' if content_type is None else content_type
        header_in['content_length'] = full_path.stat().st_size
        header_out = FILE_RESPONSE_TEMPLATE.format(
            content_type=header_in['content_type'],
            content_length=header_in['content_length']
        )
        serv_sock.sendall(header_out.encode('ascii'))
        serv_sock.sendfile(f)
