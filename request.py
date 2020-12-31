from typing import Dict, NamedTuple, BinaryIO
import socket


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
