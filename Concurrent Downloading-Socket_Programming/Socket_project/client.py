import socket

HOST = '127.0.0.1'
PORT = 9009

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

filename = input("Enter filename to download: ")
client_socket.sendall(filename.encode())

with open("downloaded_" + filename, 'wb') as f:
    while True:
        data = client_socket.recv(1000)   
        if not data:
            break
        f.write(data)

print("File downloaded successfully as downloaded_" + filename)
client_socket.close()
