import os
import time
import traceback

from framework.http import HttpStatus, ContentType


class HttpResponse:
    def __init__(self, content_type, http_version: str, status, html: bytes):
        self.content_type = str(content_type)
        self.http_version = http_version
        self.status = status
        self.html = html if html is not None else b""
        self._data: bytes = bytes()

    def data(self):
        self._data = self._build_response()
        return self._data

    def _build_response(self, receive_time=None):
        response = f"{self.http_version.strip()} {self.status.value} {self.status.name}\r\n".encode()
        response += f"{self.content_type}\r\n".encode()
        response += self.build_header("Content-Length", len(self.html))
        if receive_time is not None:
            response += self.build_header("Server-Timing", str(time.time() - receive_time))
        response += '\r\n'.encode()
        response += self.html
        return response

    @staticmethod
    def build_header(header, value):
        return f"{header}: {value}\r\n".encode()

    @staticmethod
    def build_from_route(request, route, path_variables: dict):
        try:
            response = HttpResponse.build_empty_status_response(request, HttpStatus.OK, b"")
            res = route.execute(request.clone(), response, path_variables)
            return HttpResponse(route.content_type(), response.http_version, response.status, str(res).encode() if type(res) is not bytes else res)
        except Exception as e:
            print(traceback.format_exc())
            return HttpResponse(ContentType.text, request.http_version, HttpStatus.INTERNAL_SERVER_ERROR, bytes())

    @staticmethod
    def build_empty_status_response(request, status: HttpStatus, additional_info: bytes):
        if additional_info is None:
            additional_info = ""
        return HttpResponse(ContentType.html, request.http_version, status, additional_info)

    @staticmethod
    def build_from_file(request, path: str):
        try:
            if not os.path.isfile(path):
                return HttpResponse(ContentType.text, request.http_version, HttpStatus.NOT_FOUND, bytes())
            else:
                extension = os.path.splitext(path)[1][1::]
                content_type = ContentType[extension]
                html: bytes
                with open(path, 'rb') as file:
                    html = file.read() + b"\r\n\r\n"
                return HttpResponse(content_type, request.http_version, HttpStatus.OK, html)
        except Exception:
            return HttpResponse(ContentType.text, request.http_version, HttpStatus.INTERNAL_SERVER_ERROR, bytes())
