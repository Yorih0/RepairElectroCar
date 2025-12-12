import socket
import os
from systemData import SystemData   # фасад

ip = socket.gethostbyname(socket.gethostname())
port = 20000
HOST = (ip, port)

PAGE_MAIN = "main"
DATA_BASE = "Data/REP-1.db"
FOLDER = "html"

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
        
        data = Get_Form_Data(request.decode("utf-8"))
        print(f"Полученные данные {data}")
        
        system = SystemData(data, DATA_BASE)

        match data.get("action"):
            case "login":
                response = system.Login_user()
                user = response['user']
                Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", user, message=response['message'])

            case "register":
                response = system.Register_user()
                user = response['user']
                Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", user, message=response['message'])

            case "add_customer":
                ok = system.Add_customer()
                msg = "Автомобиль добавлен" if ok else "Ошибка добавления автомобиля"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "remove_customer":
                ok = system.Remove_customer()
                msg = "Автомобиль удалён" if ok else "Ошибка удаления автомобиля"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "add_worker":
                ok = system.Add_worker()
                msg = "Работник добавлен" if ok else "Ошибка добавления работника"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "remove_worker":
                ok = system.Remove_worker()
                msg = "Работник удалён" if ok else "Ошибка удаления работника"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "add_order":
                ok = system.Add_order()
                msg = "Заказ добавлен" if ok else "Ошибка добавления заказа"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "remove_order":
                ok = system.Remove_order()
                msg = "Заказ удалён" if ok else "Ошибка удаления заказа"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "add_history":
                ok = system.Add_history()
                msg = "История добавлена" if ok else "Ошибка добавления истории"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "remove_history":
                ok = system.Remove_history()
                msg = "История удалена" if ok else "Ошибка удаления истории"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None, message=msg)

            case "html":
                Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", None)
                    
            case "css":
                Sent_page(conn, FOLDER, data.get("name_page"), "css", None)
                
            case _:
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", None)
    
    Off_server(server)

def Sent_page(conn, folder, file_name, file_type, user, message=None):
    answer, data, type = Load_file(folder, file_name, file_type)
    
    if answer == "FileIsFound":
        if message and file_type == "html":
            toast_html = f"""
            <script>
              if (typeof showToast === 'function') {{
                  showToast("{message}", "info");
              }} else {{
                  document.body.insertAdjacentHTML('beforeend',
                    '<div class="toast info show"><span>{message}</span></div>');
              }}
            </script>
            """
            if "</body>" in data:
                data = data.replace("</body>", toast_html + "</body>")
            else:
                data += toast_html

        response = f"HTTP/1.1 200 {answer}\r\n"
        response += f"Content-Type: {type}\r\n"
        response += "Content-Length: {}\r\n".format(len(data.encode("utf-8")))
        if user is not None:
            response += f"Set-Cookie: hashkey={user.hashkey}\r\n"
        response += "\r\n" 
        response += data
    else:
        response = f"HTTP/1.1 404 {answer}\r\n\r\n"
    
    conn.sendall(response.encode("utf-8"))
    conn.close()

def Load_file(folder,file_name, file_type):
    try:
        if file_type == "html":
            file_path = os.path.join(folder, file_name + ".html")
            content_type = "text/html;charset=utf-8"
        elif file_type == "css":
            file_path = os.path.join(folder, "css", file_name + ".css")
            content_type = "text/css;charset=utf-8"
        else:
            return "UnsupportedType", "<h1>Unsupported file type</h1>", "text/plain"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return "FileIsFound", content, content_type
    except FileNotFoundError:
        return "FileNotFoundError", f"<h1>Файл {file_name} не найден</h1>", "text/html"

def Off_server(server):
    server.close()

def Restart_server(server):
    server.close()
    Run_server()

def Url_decode(value):
    result =""
    i = 0
    while i < len(value):
        if value[i] == "+":
            result+=" " 
            i+=1
            continue
        if value[i] == "%" and len(value)>i+2:
            try:
                result += chr(int(value[i+1:i+3], 16))
                i+=3
                continue
            except:
                result +=value[i:i+3]
                i+=3
                continue
        else:
            result+=value[i]
            i+=1
    return result

def Get_Form_Data(request):
    params = {}
    for line in request.split("\r\n"):
        if line.startswith("Cookie:"):
            cookie_str = line[len("Cookie:"):].strip()
            for pair in cookie_str.split(";"):
                if "=" in pair:
                    key, value = pair.strip().split("=", 1)
                    params[key] = Url_decode(value)

    if "GET /css/" in request:
        file_name = request.split("GET /css/")[1].split()[0].replace(".css", "")
        params["action"] = "css"
        params["name_page"] = file_name
        return params
    elif "GET /" in request:
        path = request.split("GET /")[1].split()[0]
        if "." in path:
            params["action"] = "html"
            params["name_page"] = "main"
        else:
            params["action"] = "html"
            params["name_page"] = path if path else "main"
        return params
    else:
        headers = request.split("\r\n\r\n", 1)
        if len(headers) > 1:
            body = headers[1]
            pairs = body.split("&")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key] = Url_decode(value)
        return params

if __name__ == "__main__":
    Run_server()
