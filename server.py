import socket
import os

ip = socket.gethostbyname(socket.gethostname())
port = 20000
HOST = (ip, port)
PAGE_SETTING = "setting"
PAGE_MAIN = "main"
PAGE_LOGIN = "login"
PAGE_REGISTER ="register"

def Run_server():
    print("Запуск сервера")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(HOST)
    server.listen()
    print(f"Сервер слушает на http://{ip}:{port}")

    while True:
        conn, addr = server.accept()
        print("Соединение:", addr)
        request = b""
        while True:
            chunk = conn.recv(1024)
            request += chunk
            if b"\r\n\r\n" in request or not chunk:
                break

        get_data = Get_Form_Data(request.decode("utf-8"))
        print(get_data)
        action = get_data.get("action")
        match action:
            case "main":
                print("Отправка данных гланой страницы")
                Sent_page(conn,PAGE_MAIN,"html")
            case "login":
                print("Отправка данных страницы входа")
                Sent_page(conn,PAGE_LOGIN,"html")
            case "register":
                print("Отправка данных страницы регистрации")
                Sent_page(conn,PAGE_REGISTER,"html")
            case "off":
                print("Выключение сервера")
                Off_server(server)
                break
            case "reload":
                print("Перезагрузка сервера")
                Restart_server(server)
            case "css":
                print("Отправка стилей")
                Sent_page(conn,get_data.get("name_page"),"css")
            case _:
                print("Отправка главной страницы")
                Sent_page(conn,PAGE_SETTING,"html")
    Off_server(server)

def Off_server(server):
    server.close()

def Restart_server(server):
    server.close()
    Run_server()

def Load_file(file_name, file_type):
    try:
        if file_type == "html":
            file_path = os.path.join("html", file_name + ".html")
            content_type = "text/html;charset=utf-8"
        elif file_type == "css":
            file_path = os.path.join("html", "css", file_name + ".css")
            content_type = "text/css;charset=utf-8"
        else:
            return "UnsupportedType", "<h1>Unsupported file type</h1>", "text/plain"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return "FileIsFound", content, content_type
    except FileNotFoundError:
        return "FileNotFoundError", "<h1>Error</h1>", "text/html"

def Sent_page(conn,file_name,file_type):
    answer,data,type = Load_file(file_name,file_type)
    if(answer=="FileIsFound"):
            response = f"HTTP/1.1 200 {answer}\r\n"
            response+=f"Content-Type: {type}\r\n"
            response+="Content-Length: {}\r\n".format(len(data.encode("utf-8")))
            response+="\r\n"
            response+=data
    else:
        response = f"HTTP/1.1 404 {answer}\r\n\r\n"
    conn.sendall(response.encode("utf-8"))
    conn.close()
    
def url_decode(value):
    result = ""
    i = 0
    while i < len(value):
        if value[i] == "+":
            result += " "
            i += 1
        elif value[i] == "%" and i + 2 < len(value):
            hex_code = value[i+1:i+3]
            try:
                result += chr(int(hex_code, 16))
                i += 3
            except ValueError:
                result += value[i]
                i += 1
        else:
            result += value[i]
            i += 1
    return result

def Get_Form_Data(request):
    if "GET /css/" in request:
        file_name = request.split("GET /css/")[1].split()[0].replace(".css", "")
        params = {"action": "css", "name_page": file_name}
        return params
    headers = request.split("\r\n\r\n", 1)
    if len(headers) > 1:
        body = headers[1]
        pairs = body.split("&")
        params = {}
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                params[key] = url_decode(value)
        return params
    return []



if __name__ == "__main__":
    Run_server()