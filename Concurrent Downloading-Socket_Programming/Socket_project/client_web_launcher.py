#!/usr/bin/env python3

import socket, threading, socketserver, subprocess, os, sys
from urllib.parse import unquote

PROJECT_ROOT = os.path.dirname(__file__)
TCP_CLIENT_PORT = 9009 
TCP_SERVER_PORT = 12346  
WEB_PORT = 5002


class ThreadedTCPProxy(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def proxy_handler_factory(remote_host, remote_port):
    class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            try:
                remote = socket.create_connection((remote_host, remote_port))
            except Exception:
                self.request.close(); return

            def forward(src, dst):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data: break
                        dst.sendall(data)
                except Exception:
                    pass
            t1 = threading.Thread(target=forward, args=(self.request, remote), daemon=True)
            t2 = threading.Thread(target=forward, args=(remote, self.request), daemon=True)
            t1.start(); t2.start(); t1.join(); t2.join()
            try:
                remote.close()
            except: pass
    return Handler


def start_proxy(listen_port, remote_port):
    server = ThreadedTCPProxy(('127.0.0.1', listen_port), proxy_handler_factory('127.0.0.1', remote_port))
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


def start_flask():
    try:
        from flask import Flask, request, render_template_string
    except Exception:
        print('Flask not installed. Install with: python3 -m pip install --user flask')
        sys.exit(1)

    app = Flask(__name__)

    INDEX = '''
    <!doctype html>
    <title>Run client.py via web</title>
    <h3>Run unmodified client.py through web</h3>
    <form action="/run" method="post">
      <label>Filename (inside sample_files/):</label>
      <input name="filename" placeholder="hello.txt" />
      <button type="submit">Run</button>
    </form>
    <p>Or open <a href="/run?filename=hello.txt">/run?filename=hello.txt</a></p>
    '''

    @app.route('/')
    def index():
        return render_template_string(INDEX)

    @app.route('/run', methods=['GET', 'POST'])
    def run():
        if request.method == 'POST':
            fn = request.form.get('filename','').strip()
        else:
            fn = request.args.get('filename','').strip()
        fn = unquote(fn)
        if not fn:
            return ('filename required', 400)

        proc = subprocess.run(['python3', 'client.py'], cwd=PROJECT_ROOT,
                              input=(fn + '\n'), capture_output=True, text=True, timeout=60)
        out = proc.stdout + '\n' + proc.stderr
        return '<pre>' + out.replace('&','&amp;').replace('<','&lt;') + '</pre>'

    url = f'http://127.0.0.1:{WEB_PORT}/'
    print(f'Web UI available at: {url}')
    app.run(host='0.0.0.0', port=WEB_PORT)


def main():
    print(f'Starting TCP proxy 127.0.0.1:{TCP_CLIENT_PORT} -> 127.0.0.1:{TCP_SERVER_PORT}')
    proxy = start_proxy(TCP_CLIENT_PORT, TCP_SERVER_PORT)

    start_flask()


if __name__ == '__main__':
    main()
