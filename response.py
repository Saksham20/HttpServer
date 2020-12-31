import jinja2
from pathlib import Path
import mimetypes
from .request import Request
import requests
FILE_RESPONSE_TEMPLATE = "HTTP/1.1 {status_code}\n{header}\n\n{body}"""

BAD_REQUEST_RESPONSE = '''\
HTTP/2 400 Bad Request
Content-type: text/html
Content-length: {message_length}

{message}'''.replace("\n", "\r\n")

VIEWS_ROOT = Path(__file__).parent/'views'


class Response:
    generic = FILE_RESPONSE_TEMPLATE
    bad_response_message = 'Bad Request'
    bad_response = BAD_REQUEST_RESPONSE.format(
        message_length=len(bad_response_message),
        message=bad_response_message).encode('ascii')

    def __init__(self, request: Request, response_status: str = "200 OK", header: dict = None):
        self.request = request
        self.response_status = response_status
        self.resource_requested = self._get_file_path()
        self.body = self.generate_body()
        self.header = {} if header is None else header
        self.header.update(self.generate_header())


    def _get_file_path(self) -> str:
        base_path = VIEWS_ROOT
        if 'http' in self.request.path:
            return self.request.path
        path = self.request.path.lstrip('/')
        if path == '':
            path = 'index.html'
        for found_path in base_path.rglob(path):
            return str(found_path)

    def generate_header(self) -> dict:
        header_in = {}
        if self.resource_requested is not None:
            if 'http' in self.resource_requested:
                rs = requests.get(self.resource_requested)
                return rs.headers
            content_type, encoding = mimetypes.guess_type(self.resource_requested)
            content_type = 'text/html' if content_type is None else content_type
        else:
            content_type, encoding = 'text/html', None
        content_length = len(self.body)
        header_in.update(content_length=content_length, content_type=content_type)
        if encoding is not None:
            header_in.update(encoding=encoding)
        return header_in

    def generate_body(self) -> str:
        if self.resource_requested is not None:
            print(self.resource_requested)
            if Path(self.resource_requested).suffix=='.html':
                template_loader = jinja2.FileSystemLoader(searchpath=VIEWS_ROOT/'Templates')
                template_env = jinja2.Environment(loader=template_loader)
                template = template_env.get_template(Path(self.resource_requested).name)
                output_text = template.render(request=self.request)
            elif 'http' in self.resource_requested:
                output_text = requests.get(self.resource_requested).text
            else:
                with open(self.resource_requested,'r') as f:
                    output_text = f.read()
            return output_text
        else:
            return self.bad_response_message

    def send_response(self) -> None:
        if self.resource_requested is None:
            self.request.socket.sendall(self.bad_response)
            return
        header_string = self.header.__str__().strip('{').strip('}').replace(', ', '\n').replace('\'', '')
        response = self.generic.format(status_code=self.response_status,
                                       header=header_string,
                                       body=self.body)
        response = response.replace('\n', '\r\n')
        self.request.socket.sendall(response.encode('ascii'))
