import httpd
import sys


class AsyncWSGIServer(httpd.AsyncHTTPServer):

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application

    def handle_accepted(self, sock, addr):
        print("___WSGI____handle_accepted")
        print("Incoming connection from"+str(addr))
        AsyncWSGIRequestHandler(sock)


class AsyncWSGIRequestHandler(httpd.AsyncHTTPRequestHandler):

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = self._get_data()
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        # Required CGI variables
        env['REQUEST_METHOD'] = self.method  # GET
        env['PATH_INFO'] = self.uri  # /hello
        env['SERVER_NAME'] = self.response_headers['Server']  # localhost
        env['SERVER_PORT'] = 9000  # 9000
        return env

    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', self.date_time_string()),
            ('Server', 'WSGIServer'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        return self.finish_response

    def handle_request(self):
        environ = self.get_environ()
        app = server.get_app()
        result = app(environ, self.start_response)
        self.finish_response(result)

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set

            self.push(self.get_bytes("HTTP/1.1 " + str(status)))
            self.add_terminator()

            for header in response_headers:
                self.send_header(header[0], header[1])
            self.add_terminator()

            self.push(self.get_bytes(result))
        finally:
            self.handle_close()



SERVER_ADDRESS = (HOST, PORT) = "127.0.0.1", 9000

def make_server(application):
    server = AsyncWSGIServer()
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    server = make_server(application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    server.serve_forever()
