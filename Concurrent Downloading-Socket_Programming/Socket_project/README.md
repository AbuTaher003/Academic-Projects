# Concurrent File Server (Python) + Web UI

This project demonstrates a TCP-based concurrent file server (one thread per client request) and a small web UI built with Flask that requests files from the file server and streams them to the browser.

Features:
- TCP file server that spawns a thread per request. The thread receives the filename as the first argument to the thread function.
- Server sends at most 1000 bytes per send and sleeps 200 ms after each flush.
- CLI client to download files from the server.
- Flask web UI (HTML/CSS/JS) to request files and download them in the browser.

Quick start
1. Start the file server:

```bash
cd /Users/abutaher/Desktop/Socket_project
python3 server.py
```

2. Start the web UI (Flask):

```bash
cd /Users/abutaher/Desktop/Socket_project
python3 flask_app.py
```

Open http://127.0.0.1:5000 in your browser and request `hello.txt` or `bigfile.txt`.

CLI client

```bash
python3 client.py hello.txt
```

Notes
- Server listens on `127.0.0.1:9009`.
- Files to serve are in `sample_files/`.
