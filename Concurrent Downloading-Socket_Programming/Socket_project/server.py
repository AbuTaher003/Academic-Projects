import socket
import threading
import time

def handle_client(conn, filename):
    try:
        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(10)
                if not chunk:
                    break
                conn.sendall(chunk)
                time.sleep(0.2)  
    except:
        conn.sendall(b"File not found.")
    conn.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12346))
server_socket.listen(5)

while True:
    conn, addr = server_socket.accept()
    filename = conn.recv(1024).decode()
    thread = threading.Thread(target=handle_client, args=(conn, filename))
    thread.start()
