from typing import Dict, NamedTuple, BinaryIO
import socket
from pathlib import Path
import mimetypes
import socket

# note: constants accodding to PEP8 are defined by capital letters and are present outside any function.
#  its a better practice to encapsulate all the useful action oriented code inside a function. Stuff that
#  are at the module level are these constants only!
FILE_RESPONSE_TEMPLATE = "HTTP/1.1 {status_code}\n{header}\n\n{body}"""

BAD_REQUEST_RESPONSE = b'''\
HTTP/2 400 Bad Request
Content-type: text/html
Content-length: 11

Bad Request'''.replace(b"\n", b"\r\n")

TEMPLATES_ROOT = Path(__file__).parent/'views'


# TODO: create a response class that holds the default 404,200 etc coded responses, version
#  and the standard headers with the body/content/encoding fields? Find out what these are.
#  encoding  can be found from mimetypes. Also add logic for cURL: it should look for a
#  'expect: 100-continue' and then sock.send() the 100 continue in the response_line
class Request(NamedTuple):
    headers: Dict[str, bytes]
    method: str
    path: str
    body: str
    socket: socket.socket

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
            body_start_index = soc_data_list.index('') + 2
        except ValueError:
            body_start_index = len(soc_data_list) - 1
        # get header info:
        headers = {}
        for soc_data_line in soc_data_list[1:body_start_index - 2]:
            try:
                head_key, head_val = soc_data_line.split(': ')
            except ValueError as e:
                raise Exception('incorrect header format of http')
            headers[head_key] = head_val
        # get body info:
        body = ''
        if len(soc_data_list) > body_start_index:
            body = '\n'.join(soc_data_list[body_start_index:]).lstrip('\n')
        return cls(headers=headers, method=method, path=path, body=body, socket=sock)


class Response:
    generic = FILE_RESPONSE_TEMPLATE
    bad_response = BAD_REQUEST_RESPONSE

    def __init__(self, request: Request, response_status: str = "200 OK", header: dict = None):
        self.request = request
        self.response_status = response_status
        self.file_requested = self._get_file_path()
        self.header = {} if header is None else header
        self.header.update(self.generate_header())
        self.body = self.generate_body()

    def _get_file_path(self) -> Path:
        base_path = TEMPLATES_ROOT
        path = self.request.path.lstrip('/')
        if path == '':
            path = 'index.html'
        full_path = base_path/path
        if full_path.is_file():
            return full_path

    def generate_header(self) -> dict:
        header_in = {}
        if self.file_requested is not None:
            content_type, encoding = mimetypes.guess_type(self.file_requested)
            content_type = 'application/octet-stream' if content_type is None else content_type
            content_length = self.file_requested.stat().st_size
        else:
            content_type, encoding, content_length = 'application/octet-stream', None, 1024
        header_in.update(content_length=content_length, content_type=content_type)
        if encoding is not None:
            header_in.update(encoding=encoding)
        return header_in

    def generate_body(self) -> str:
        if self.file_requested is not None:
            with open(self.file_requested, 'r') as f:
                body = f.read(self.header['content_length'])
                return body
        else:
            return ''

    def send_response(self) -> None:
        if self.file_requested is None:
            self.request.socket.sendall(self.bad_response)
            return
        header_string = self.header.__str__().strip('{').strip('}').replace(', ','\n').replace('\'','')
        response = self.generic.format(status_code=self.response_status,
                                       header=header_string,
                                       body=self.body)
        response = response.replace('\n','\r\n')
        self.request.socket.sendall(response.encode('ascii'))
