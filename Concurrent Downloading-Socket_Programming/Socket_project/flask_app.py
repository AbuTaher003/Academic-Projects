from flask import Flask, render_template, request, Response, stream_with_context
import socket
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

FILE_SERVER_HOST = '127.0.0.1'
FILE_SERVER_PORT = 12346

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json() or request.form
    filename = (data.get('filename') or '').strip()
    if not filename:
        return ('Filename required', 400)
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return ('Invalid filename', 400)
    base_dir = os.path.join(os.path.dirname(__file__), 'sample_files')
    local_path = os.path.join(base_dir, filename)
    content_length = None
    if os.path.exists(local_path) and os.path.isfile(local_path):
        try:
            content_length = os.path.getsize(local_path)
        except Exception:
            content_length = None

    def generate():
        server_filename = os.path.join('sample_files', filename)
        with socket.create_connection((FILE_SERVER_HOST, FILE_SERVER_PORT)) as s:
            s.sendall(server_filename.encode())
            while True:
                chunk = s.recv(10)
                if not chunk:
                    break
                yield chunk 

    headers = {
        'Content-Disposition': f'attachment; filename="{os.path.basename(filename)}"'
    }
    if content_length is not None:
        headers['Content-Length'] = str(content_length)

    return Response(stream_with_context(generate()), headers=headers, mimetype='application/octet-stream')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5033, debug=True)