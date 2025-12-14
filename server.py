import socket
import os
from systemData import SystemData
from urllib.parse import parse_qs, unquote_plus

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
        
        # Для статических файлов (css, js) не создаем SystemData
        if data.get("action") in ["css", "js"]:
            Sent_page(conn, FOLDER, data.get("name_page"), data.get("action"), None)
            continue
            
        # Для остальных запросов создаем SystemData
        system = SystemData(data, DATA_BASE)
        print("Данные пользователя")
        print(system.User.Info())
        
        match data.get("action"):
            case "login":
                response = system.Login_user()#тут ошибка
                # system.User = response 
                # После успешного входа устанавливаем куки
                if response['status'] == 'success':
                    Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                             system, message=response['message'], set_cookie=True)
                else:
                    Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                             system, message=response['message'])

            case "register":
                response = system.Register_user()
                # user = response['user']
                # После успешной регистрации устанавливаем куки
                if response['status'] == 'success':
                    Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                             system, message=response['message'], set_cookie=True)
                else:
                    Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                             system, message=response['message'])

            case "add_customer":
                ok = system.Add_customer()
                msg = "Автомобиль добавлен" if ok else "Ошибка добавления автомобиля"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "remove_customer":
                ok = system.Remove_customer()
                msg = "Автомобиль удалён" if ok else "Ошибка удаления автомобиля"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "add_worker":
                ok = system.Add_worker()
                msg = "Работник добавлен" if ok else "Ошибка добавления работника"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "remove_worker":
                ok = system.Remove_worker()
                msg = "Работник удалён" if ok else "Ошибка удаления работника"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "add_order":
                ok = system.Add_order()
                msg = "Заказ добавлен" if ok else "Ошибка добавления заказа"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "remove_order":
                ok = system.Remove_order()
                msg = "Заказ удалён" if ok else "Ошибка удаления заказа"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "add_history":
                ok = system.Add_history()
                msg = "История добавлена" if ok else "Ошибка добавления истории"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "remove_history":
                ok = system.Remove_history()
                msg = "История удалена" if ok else "Ошибка удаления истории"
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system, message=msg)

            case "html":
                Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", system)
                
            case _:
                Sent_page(conn, FOLDER, PAGE_MAIN, "html", system)
    
    Off_server(server)

def Sent_page(conn, folder, file_name, file_type, system, message=None, set_cookie=False):
    answer, data, type = Load_file(folder, file_name, file_type)
    
    if answer == "FileIsFound":
        if message and file_type == "html":
            # Экранируем сообщение для JavaScript
            safe_message = message.replace('"', '\\"').replace("'", "\\'")
            toast_html = f"""
            <script>
              if (typeof showToast === 'function') {{
                  showToast("{safe_message}", "info");
              }} else {{
                  document.body.insertAdjacentHTML('beforeend',
                    '<div class="toast info show"><span>{safe_message}</span></div>');
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
        
        # Устанавливаем куки только если нужно и если есть валидный hashkey
        if set_cookie and system and hasattr(system, "User"):
            user_info = system.User.Info()
            hashkey = user_info.get('hashkey')
            print("=====================")
            print(hashkey)
            print("=====================")
            if hashkey and hashkey != 'None' and hashkey != 'xxx':
                response += f"Set-Cookie: hashkey={hashkey}; Path=/;\r\n"
        
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
        elif file_type == "js":
            file_path = os.path.join(folder, "js", file_name + ".js")
            content_type = "application/javascript; charset=utf-8"
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

def Get_Form_Data(request):
    params = {}
    headers, _, body = request.partition("\r\n\r\n")

    # Парсим Cookie
    for line in headers.split("\r\n"):
        if line.startswith("Cookie:"):
            cookie_str = line[len("Cookie:"):].strip()
            for pair in cookie_str.split(";"):
                if "=" in pair:
                    key, value = pair.strip().split("=", 1)
                    decoded_value = unquote_plus(value)
                    # Игнорируем значение 'None' как строку
                    if decoded_value != 'None':
                        params[key] = decoded_value

    # Если есть тело (POST)
    if body:
        parsed = parse_qs(body, keep_blank_values=True)
        for key, value in parsed.items():
            params[key] = value[0]  # берём первое значение

    # Если GET запрос
    if "GET /js/" in headers:
        file_name = headers.split("GET /js/")[1].split()[0].replace(".js", "")
        params["action"] = "js"
        params["name_page"] = file_name
    elif "GET /css/" in headers:
        file_name = headers.split("GET /css/")[1].split()[0].replace(".css", "")
        params["action"] = "css"
        params["name_page"] = file_name
    elif "GET /" in headers:
        path = headers.split("GET /")[1].split()[0]
        # Убираем параметры запроса если есть
        if '?' in path:
            path = path.split('?')[0]
        # Определяем имя страницы
        if path == "" or path.endswith(".html"):
            name = "main" if path == "" else path.replace(".html", "")
            params["action"] = "html"
            params["name_page"] = name
        elif '.' not in path:  # Если нет расширения, считаем это html страницей
            params["action"] = "html"
            params["name_page"] = path or "main"

    return params


if __name__ == "__main__":
    Run_server()