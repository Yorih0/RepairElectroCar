import socket

ip = socket.gethostbyname(socket.gethostname())
port = 20000
HOST = (ip, port)

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(HOST)
print("Connected to ",HOST)

message = client.recv(1024)
print(message.decode("UTF-8"))