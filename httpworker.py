from .request import Request
from .response import Response
from queue import Queue
from threading import Thread


class HttpWorker:

    def __init__(self, queue: Queue, concurrent=True):
        self._queue = queue
        self._run = True
        self.concurrent = concurrent

    def start(self):
        while self._run:
            if not self._queue.empty():
                print(f'worker processing queue of length:{self._queue.qsize()}')
                client_socket, client_add = self._queue.get()
                if self.concurrent:
                    thread_loop = Thread(target=self._serve_file,
                                         args=(client_socket,))
                    thread_loop.start()
                else:
                    self._serve_file(client_socket)


    def stop(self):
        self._run = False

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
