from typing import Dict, NamedTuple, BinaryIO
import socket
from pathlib import Path
import mimetypes
from .request import Request

FILE_RESPONSE_TEMPLATE = "HTTP/1.1 {status_code}\n{header}\n\n{body}"""

BAD_REQUEST_RESPONSE = b'''\
HTTP/2 400 Bad Request
Content-type: text/html
Content-length: 11

Bad Request'''.replace(b"\n", b"\r\n")

TEMPLATES_ROOT = Path(__file__).parent/'views'

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