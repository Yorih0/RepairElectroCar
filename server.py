#Библиотеки
import socket
import os
#Классы
from User import User
from manager_of_base_data import *
#Глобальные переменные
ip = socket.gethostbyname(socket.gethostname())
port = 20000
HOST = (ip, port)
#Переменные для хранение названия файлов
PAGE_SETTING = "setting"
PAGE_MAIN = "main"
PAGE_ADMIN = "admin_data"
PAGE_LOGIN = "login"
DATA_BASE = "REPA.db"
#Запуск сервера тоесть главная функция в ней все обрабатываться и выдаеться 
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
        get_data = Get_Form_Data(request.decode("utf-8"))
        print(get_data)
        action = get_data.get("action")
        #Обработка действий
        match action:
            case "html":
                print("Отправка html",get_data.get("name_page"))
                Sent_page(conn,get_data.get("name_page"),"html")
            case "css":
                print("Отправка css")
                Sent_page(conn,get_data.get("name_page"),"css")
            case "cretor_of_base_data":
                print("Создание базы данных")
                Create_Data_Table(get_data)
            # case "create_worker":
            #     print("Добавление работника")
            #     Add_worker(get_data,DATA_BASE)
            # case "create_customer":
            #     print("Добавление заказчика")
            #     Add_customer(get_data,DATA_BASE)
            case "login":
                print("Вход")
                data = Login_user(get_data)
                print(data)
                if(data.get("status") == "success"):
                    match data["user"]["role"]:
                        case "customer":
                            Sent_page(conn,PAGE_MAIN,"html")
                        case "admin":
                            Sent_page(conn,PAGE_ADMIN,"html")
                        case "worker":
                            Sent_page(conn,PAGE_SETTING,"html")
                else:  
                    print("Неверно")
            case "registed":
                print("Регистрация пользователя")
                Register_user(get_data)
            case _:
                print("Отправка главной страницы")
                Sent_page(conn,PAGE_SETTING,"html")
    Off_server(server)
#Выклюние сервера - Работает
def Off_server(server):
    server.close()
#Перезагрузка сервера - Неработет
def Restart_server(server):
    server.close()
    Run_server()
#Чтение фала из дериктории
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
#Отправка страницы пользовтелям как html так и css
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
#Обработка строки на Декодирование строки преобразовывыет шеснацеричные коды в символы (+ = Пробел) (%40 = @)  и тд
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
#Обработка post запросов и выдача картежа(Ключ:значение)
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
                params[key] = Url_decode(value)
        return params
    return []


if __name__ == "__main__":
    Run_server()