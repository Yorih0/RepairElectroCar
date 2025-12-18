import socket
import os
from Class.systemData import SystemData
from urllib.parse import parse_qs, unquote_plus
import json

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
            print(f"Полученные данные {data}")
            
            if data.get("action") in ["css", "js"]:
                Sent_page(conn, FOLDER, data.get("name_page"), data.get("action"), None)
                continue
                
            people = SystemData(data, DATA_BASE)
            print("Данные пользователя")
            print(people.User.Info())
            
            match data.get("action"):
                case "login":
                    response = people.Login_user()
                    if response['status'] == 'success':
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                people, message=response['message'], set_cookie=True)
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                people, message=response['message'])

                case "register":
                    response = people.Register_user()
                    if response['status'] == 'success':
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                people, message=response['message'], set_cookie=True)
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", 
                                people, message=response['message'])

                case "add_customer":
                    ok = people.Add_customer()
                    msg = "Автомобиль добавлен" if ok else "Ошибка добавления автомобиля"
                    Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg,Type_message="warning")

                case "remove_customer":
                    ok = people.Remove_customer()
                    msg = "Автомобиль удалён" if ok else "Ошибка удаления автомобиля"
                    Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg,Type_message="warning")

                # case "add_worker":
                #     ok = people.Add_worker()
                #     msg = "Работник добавлен" if ok else "Ошибка добавления работника"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                # case "remove_worker":
                #     ok = people.Remove_worker()
                #     msg = "Работник удалён" if ok else "Ошибка удаления работника"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                # case "add_order":
                #     ok = people.Add_order()
                #     msg = "Заказ добавлен" if ok else "Ошибка добавления заказа"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                # case "remove_order":
                #     ok = people.Remove_order()
                #     msg = "Заказ удалён" if ok else "Ошибка удаления заказа"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                # case "add_history":
                #     ok = people.Add_history()
                #     msg = "История добавлена" if ok else "Ошибка добавления истории"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                # case "remove_history":
                #     ok = people.Remove_history()
                #     msg = "История удалена" if ok else "Ошибка удаления истории"
                #     Sent_page(conn, FOLDER, PAGE_MAIN, "html", people, message=msg)

                case "html":
                    if(data.get("name_page")=="profile"):
                        user_info = people.User.Info()
                        list_car = people.All_car_user()
                        cars_info = {}
                        car_id = 0
                        for car in list_car:
                            cars_info[car_id] = {
                                "id": car_id + 1,
                                "model": getattr(car, "car_model", "Неизвестно"),
                                "vin": getattr(car, "car_vin", "-")
                            }
                        # orders = Order.Get_orders_by_user(user_info.get("id"), user_info.get("role"), DATA_BASE)
                        # orders_data = [order.Info() for order in orders]
                        print("User_info")
                        print(user_info)
                        print(cars_info)
                        js_data = f"""
                        <script>
                            const USER_DATA = {json.dumps(user_info)};
                            const Car_DATA = {json.dumps(cars_info)};

                            // Отрисовка информации о пользователе
                            const userDetails = document.getElementById("user-details");
                            for (const key in USER_DATA) {{
                                const li = document.createElement("li");
                                li.textContent = `${{key}}: ${{USER_DATA[key] !== null && USER_DATA[key] !== undefined ? USER_DATA[key] : '-'}}`;
                                userDetails.appendChild(li);
                            }}

                            // Отрисовка таблицы автомобилей
                            const carsTableBody = document.getElementById("cars-table").querySelector("tbody");
                            carsTableBody.innerHTML = ''; // очищаем тело таблицы

                            if (Object.keys(Car_DATA).length === 0) {{
                                const tr = document.createElement("tr");
                                const td = document.createElement("td");
                                td.colSpan = 5;
                                td.textContent = "У вас пока нет автомобилей";
                                td.style.textAlign = "center";
                                tr.appendChild(td);
                                carsTableBody.appendChild(tr);
                            }} else {{
                                for (const carId in Car_DATA) {{
                                    const car = Car_DATA[carId];
                                    const tr = document.createElement("tr");

                                    const tdId = document.createElement("td");
                                    tdId.textContent = car.id || "";
                                    tr.appendChild(tdId);

                                    const tdModel = document.createElement("td");
                                    tdModel.textContent = car.model || "";
                                    tr.appendChild(tdModel);

                                    const tdYear = document.createElement("td");
                                    tdYear.textContent = car.vin || "";
                                    tr.appendChild(tdYear);

                                    carsTableBody.appendChild(tr);
                                }}
                            }}
                        </script>
                        """
                        # const USER_ORDERS = {json.dumps(orders_data)};
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", people, extra_script=js_data)
                    else:
                        Sent_page(conn, FOLDER, data.get("name_page", PAGE_MAIN), "html", people)
                    
                case _:
                    Sent_page(conn, FOLDER, PAGE_MAIN, "html", people)
        finally:
            conn.close()

def Sent_page(conn, folder, file_name, file_type, people, message=None, Type_message="info",set_cookie=False,extra_script=""):
    answer, data, type = Load_file(folder, file_name, file_type)
    
    if answer == "FileIsFound":
        if message and file_type == "html":
            safe_message = message.replace('"', '\\"').replace("'", "\\'")
            toast_html = f"""
            <script>
              if (typeof showToast === 'function') {{
                  showToast("{safe_message}", {Type_message});
              }} else {{
                  document.body.insertAdjacentHTML('beforeend',
                    '<div class="toast info show"><span>{safe_message}</span></div>');
              }}
            </script>
            """
            if "</body>" in data:
                data = data.replace("</body>", toast_html + extra_script+"</body>")
            else:
                data += toast_html+extra_script
        else:
            data +=extra_script

        response = f"HTTP/1.1 200 {answer}\r\n"
        response += f"Content-Type: {type}\r\n"
        response += "Content-Length: {}\r\n".format(len(data.encode("utf-8")))
        
        if set_cookie and people and hasattr(people, "User"):
            user_info = people.User.Info()
            hashkey = user_info.get('hashkey')
            if hashkey and hashkey != 'None' and hashkey != 'xxx':
                response += f"Set-Cookie: hashkey={hashkey}; Path=/;\r\n"
        
        response += "\r\n" 
        response += data
    else:
        response = f"HTTP/1.1 404 {answer}\r\n\r\n"
    
    conn.sendall(response.encode("utf-8"))
    # conn.close()

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

    for line in headers.split("\r\n"):
        if line.startswith("Cookie:"):
            cookie_str = line[len("Cookie:"):].strip()
            for pair in cookie_str.split(";"):
                if "=" in pair:
                    key, value = pair.strip().split("=", 1)
                    decoded_value = unquote_plus(value)
                    if decoded_value != 'None':
                        params[key] = decoded_value

    if body:
        parsed = parse_qs(body, keep_blank_values=True)
        for key, value in parsed.items():
            params[key] = value[0]  

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
        if '?' in path:
            path = path.split('?')[0]
        if path == "" or path.endswith(".html"):
            name = "main" if path == "" else path.replace(".html", "")
            params["action"] = "html"
            params["name_page"] = name
        elif '.' not in path: 
            params["action"] = "html"
            params["name_page"] = path or "main"

    return params


if __name__ == "__main__":
    Run_server()