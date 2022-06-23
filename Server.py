import json
import socket
from functools import lru_cache

route_paths = {}


class LIDServer:

    def __init__(self, host, port):
        self.host, self.port = host, port

        self.build_socket()
        self.listen_socket()

    def build_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    @lru_cache(typed=False, maxsize=256)
    def start(self):
        try:
            while True:
                client_connection, client_address = self.client_accept()
                try:
                    request = LID_Request(client_connection.recv(1024).decode()).parse()
                    r_type, r_code, r_content = self.path_execute(request['request']['path'])
                    self.sendResponse(client_connection, LID_Response().build_response([
                        'HTTP/2.0 ' + str(r_code) + ' ' + r_type.upper(),
                        r_content
                    ]))
                except:
                    self.sendResponse(client_connection, LID_Response().build_error_response(500, 'Internal server error'))
        except:
            print("SERVER ERROR")

    def listen_socket(self):
        self.server_socket.listen(1)

    def client_accept(self):
        return self.server_socket.accept()

    def close_socket(self):
        return self.server_socket.close()

    def setRoute(self, path):
        def decorator(func):
            global route_paths
            route_paths[path] = func

            def wrapper():
                pass

            return wrapper

        return decorator

    def sendResponse(self, client, response):
        client.sendall(response.encode())
        client.close()

    def path_execute(self, path):
        global route_paths
        if path in route_paths:
            return route_paths[path]()
        else:
            return ("Error", 404, "Page not found")


def response_ok(text):
    return ("ok", 200, text)


def response_error(code, text):
    return ("error", code, text)


def response_json(json_o):
    return ("ok", 200, json.dumps(json_o))


class LID_Request:

    def __init__(self, request):
        self.request = request

    def parse(self):
        params = self.request.split('\r\n')
        path = params[0].split(" ")
        report = {
            "request": {
                "type": path[0],
                "path": path[1],
                "version": path[2]
            },
            "headers": {}
        }
        for val, key in [r.split(': ') for r in params[1:-2]]:
            report['headers'][str(val).lower()] = key
        return report


class LID_Response:

    def __init__(self):
        pass

    def build_response(self, params):
        return "\n\n".join(params)

    def build_error_response(self, error_code, error_text):
        return self.build_response([
            "HTTP/2.0 " + str(error_code) + " ERROR",
            json.dumps({
                "error_code": error_code,
                "error": "[" + str(error_code) + "] " + error_text
            })
        ])
