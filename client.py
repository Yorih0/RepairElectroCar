# import socket
# import os
# # ip = socket.gethostbyname(socket.gethostname())
# # port = 20000
# # HOST = (ip, port)

# # client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# # client.connect(HOST)
# # print("Connected to ",HOST)

# # message = client.recv(1024)
# # print(message.decode("UTF-8"))
# def Load_file(folder,file_name, file_type):
#     try:
#         if file_type == "html":
#             file_path = os.path.join(folder, file_name + ".html")
#             content_type = "text/html;charset=utf-8"
#         elif file_type == "css":
#             file_path = os.path.join(folder, "css", file_name + ".css")
#             content_type = "text/css;charset=utf-8"
#         else:
#             return "UnsupportedType", "<h1>Unsupported file type</h1>", "text/plain"

#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
#         return "FileIsFound", content, content_type
#     except FileNotFoundError:
#         return "FileNotFoundError", f"<h1>Error{folder}</h1>", "text/html"
# FOLDER ="html_f"
# print(Load_file(FOLDER,"Main","html"))
