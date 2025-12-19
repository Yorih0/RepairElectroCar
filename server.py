import socket
import os
from urllib.parse import parse_qs, unquote_plus
import json
from Class.systemData import SystemData
from Class.user import User 

ip = socket.gethostbyname(socket.gethostname())
port = 20000
HOST = (ip, port)

PAGE_MAIN = "main"
FILE_DB = "Data/REP-1.db"
FOLDER = "html"

def Run_server():
    print("Запуск сервера")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(HOST)
    server.listen()
    print(f"Сервер слушает на http://{ip}:{port}")
    
    while True:
        try:
            conn, addr = server.accept()
            print("Соединение:", addr)
            request = b""
            while True:
                chunk = conn.recv(1024)
                request += chunk
                if b"\r\n\r\n" in request or not chunk:
                    break
            
            data = Get_Form_Data(request.decode("utf-8"))
            print(f"Полученные данные: {data}")
            
            if data.get("action") in ["css", "js"]:
                Sent_page(conn, FOLDER, data.get("name_page"), data.get("action"), None)
                continue
                
            people = SystemData(FILE_DB)
            
            # Проверяем hashkey из куки
            hashkey = data.get("hashkey")
            current_user = None
            
            if hashkey:
                user = User.Find_user_by_atr("hashkey", hashkey, FILE_DB)
                if user:
                    current_user = user
                    people.current_user = user
            
            match data.get("action"):
                case "login":
                    result, user = people.find_user(
                        login=data.get("login", ""),
                        password=data.get("password", "")
                    )
                    
                    if result["status"] == "success":
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                 user.hashkey, set_cookie=True, message=result["message"])
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                 None, message=result["message"])

                case "register":
                    result, user = people.create_user(
                        login=data.get("login", ""),
                        password=data.get("password", ""),
                        password_r=data.get("password_r", ""),
                        mail=data.get("mail", ""),
                        phone=data.get("phone", "")
                    )
                    
                    if result["status"] == "success":
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html",
                                 user.hashkey, set_cookie=True, message=result["message"])
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html",
                                 None, message=result["message"])

                case "html":
                    if data.get("name_page") == "profile":
                        if not current_user:
                            Sent_page(conn, FOLDER, "login", "html", None, 
                                     message="Требуется авторизация", Type_message="error")
                            continue
                            
                        user_info = current_user.Info()
                        list_car = people.get_cars_by_user(current_user.id)
                        list_order = people.get_orders_by_user(current_user.id)
                        cars_info = {}
                        order_info = {}
                        for i, car in enumerate(list_car):
                            cars_info[i] = {
                                "id": i + 1,
                                "model": car.car_model if car.car_model else "Неизвестно",
                                "vin": car.car_vin if car.car_vin else "-"
                            }
                        for i, car in enumerate(list_car):
                            order_info[i] = {
                                
                            }
                        js_data = f"""
                        <script>
                            const USER_DATA = {json.dumps(user_info)};
                            const Car_DATA = {json.dumps(cars_info)};

                            // Отрисовка информации о пользователе
                            const userDetails = document.getElementById("user-details");
                            if (userDetails) {{
                                userDetails.innerHTML = '';
                                for (const [key, value] of Object.entries(USER_DATA)) {{
                                    const li = document.createElement("li");
                                    li.textContent = `${{key}}: ${{value !== null && value !== undefined ? value : '-'}}`;
                                    userDetails.appendChild(li);
                                }}
                            }}

                            // Отрисовка таблицы автомобилей
                            const carsTableBody = document.getElementById("cars-table")?.querySelector("tbody");
                            if (carsTableBody) {{
                                carsTableBody.innerHTML = '';
                                if (Object.keys(Car_DATA).length === 0) {{
                                    const tr = document.createElement("tr");
                                    const td = document.createElement("td");
                                    td.colSpan = 3;
                                    td.textContent = "У вас пока нет автомобилей";
                                    td.style.textAlign = "center";
                                    tr.appendChild(td);
                                    carsTableBody.appendChild(tr);
                                }} else {{
                                    for (const carId in Car_DATA) {{
                                        const car = Car_DATA[carId];
                                        const tr = document.createElement("tr");

                                        const tdId = document.createElement("td");
                                        tdId.textContent = car.id;
                                        tr.appendChild(tdId);

                                        const tdModel = document.createElement("td");
                                        tdModel.textContent = car.model;
                                        tr.appendChild(tdModel);

                                        const tdVin = document.createElement("td");
                                        tdVin.textContent = car.vin;
                                        tr.appendChild(tdVin);

                                        carsTableBody.appendChild(tr);
                                    }}
                                }}
                            }}
                        </script>
                        """
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                 hashkey, extra_script=js_data)
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", hashkey)
                    
                case _:
                    Sent_page(conn, FOLDER, PAGE_MAIN, "html", hashkey)
                    
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")
            try:
                error_message = f"Внутренняя ошибка сервера: {str(e)}"
                Sent_page(conn, FOLDER, "error", "html", None, message=error_message, Type_message="error")
            except:
                pass
        finally:
            conn.close()

def Sent_page(conn, folder, file_name, file_type, hashkey=None, set_cookie=False, 
              message=None, Type_message="info", extra_script=""):
    
    answer, data, content_type = Load_file(folder, file_name, file_type)
    
    if answer == "FileIsFound":
        if message and file_type == "html":
            safe_message = message.replace('"', '\\"').replace("'", "\\'")
            toast_html = f"""
            <script>
              if (typeof showToast === 'function') {{
                  showToast("{safe_message}", "{Type_message}");
              }} else {{
                  document.body.insertAdjacentHTML('beforeend',
                    '<div class="toast {Type_message} show"><span>{safe_message}</span></div>');
              }}
            </script>
            """
            if "</body>" in data:
                data = data.replace("</body>", toast_html + extra_script + "</body>")
            else:
                data += toast_html + extra_script
        else:
            data += extra_script

        response = f"HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: {content_type}\r\n"
        response += f"Content-Length: {len(data.encode('utf-8'))}\r\n"
        
        if set_cookie and hashkey:
            response += f"Set-Cookie: hashkey={hashkey}; Path=/;\r\n"
        
        response += "\r\n" + data
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\nFile not found"
    
    conn.sendall(response.encode("utf-8"))

def Load_file(folder, file_name, file_type):
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

def Get_Form_Data(request):
    params = {}
    headers, _, body = request.partition("\r\n\r\n")

    for line in headers.split("\r\n"):
        if line.startswith("Cookie:"):
            cookie_str = line[len("Cookie:"):].strip()
            for pair in cookie_str.split(";"):
                if "=" in pair:
                    key, value = pair.strip().split("=", 1)
                    decoded_value = unquote_plus(value)
                    if decoded_value.lower() != 'none':
                        params[key] = decoded_value

    if body:
        parsed = parse_qs(body, keep_blank_values=True)
        for key, value in parsed.items():
            params[key] = value[0] if value else ""

    if "GET" in headers:
        parts = headers.split(" ")[1]
        if "?" in parts:
            path, query = parts.split("?", 1)
            query_params = parse_qs(query)
            for key, value in query_params.items():
                params[key] = value[0] if value else ""
        else:
            path = parts
        
        if path.startswith("/js/"):
            file_name = path[4:].replace(".js", "")
            params["action"] = "js"
            params["name_page"] = file_name
        elif path.startswith("/css/"):
            file_name = path[5:].replace(".css", "")
            params["action"] = "css"
            params["name_page"] = file_name
        elif path.endswith(".html") or path == "/" or "/" not in path:
            if path == "/":
                name = "main"
            elif path.endswith(".html"):
                name = path[1:].replace(".html", "")
            else:
                name = path[1:] if path.startswith("/") else path
                if not name:
                    name = "main"
            
            params["action"] = "html"
            params["name_page"] = name

    return params


if __name__ == "__main__":
    Run_server()