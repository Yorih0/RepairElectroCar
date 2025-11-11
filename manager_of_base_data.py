import sqlite3
import hashlib

def Create_Data_Table(tuple):
    con = sqlite3.connect(f"Data/{tuple.get("Name_of_base_data")}.db")
    cursor = con.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL,
                    mail TEXT,
                    phone TEXT,
                    hash TEXT
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Workers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    specialization TEXT,
                    experience INTEGER,
                    rating REAL,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Customers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    car_model TEXT,
                    car_vin TEXT,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS Orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    worker_id INTEGER,
                    status TEXT,
                    description TEXT,
                    created_at TEXT,
                    finished_at TEXT,
                    FOREIGN KEY (customer_id) REFERENCES Customers(id),
                    FOREIGN KEY (worker_id) REFERENCES Workers(id)
                    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS History_of_orders(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    status TEXT,
                    timestamp TEXT,
                    comment TEXT,
                    FOREIGN KEY (order_id) REFERENCES Orders(id)
                )""")
    con.commit()
    con.close()
    Add_admin(tuple)

def Add_admin(tuple):
    if tuple.get("Password") != tuple.get("Password_Repeat"):
        return ValueError("Пароли не совпадают")
    password_hash = hashlib.sha256(tuple.get("Password").encode("utf-8")).hexdigest()
    con = sqlite3.connect(f"Data/{tuple.get("Name_of_base_data")}.db")
    cursor = con.cursor()
    cursor.execute("""
        INSERT INTO Users (role, login, password)
        VALUES (?, ?, ?)
    """, (
        "admin",
        tuple.get("Login"),
        password_hash
    ))
    con.commit()
    con.close()

def Register_user(tuple, db_path="Data/Repa.db"):
    if tuple.get("Password") != tuple.get("Password_Repeat"):
        return {"status": "error", "message": "Пароли не совпадают"}
    password_hash = hashlib.sha256(tuple.get("Password").encode("utf-8")).hexdigest()
    con = sqlite3.connect(db_path)
    cursor = con.cursor()
    try:
        # Проверка уникальности логина
        cursor.execute("SELECT id FROM Users WHERE login = ?", (tuple.get("Login"),))
        if cursor.fetchone():
            return {"status": "error", "message": "Такой логин уже существует"}
        # Вставка нового пользователя
        cursor.execute("""
            INSERT INTO Users (role, login, password, mail, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "customer",
            tuple.get("Login"),
            password_hash,
            tuple.get("Mail"),
            tuple.get("Phone"),
        ))
        con.commit()
        return {"status": "success", "message": "Пользователь зарегистрирован"}
    except sqlite3.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        con.close()

def Login_user(tuple, db_path="Data/Repa.db"):
    con = sqlite3.connect(db_path)
    cursor = con.cursor()
    try:
        # Получаем пользователя по логину
        cursor.execute("SELECT id, password, role, mail, phone FROM Users WHERE login = ?", (tuple.get("Login"),))
        row = cursor.fetchone()
        if not row:
            return {"status": "error", "message": "Логин не найден"}
        user_id, stored_hash, role, mail, phone = row
        # Проверяем пароль
        password_hash = hashlib.sha256(tuple.get("Password").encode("utf-8")).hexdigest()
        if password_hash != stored_hash:
            return {"status": "error", "message": "Неверный пароль"}
        # Успешный вход
        return {
            "status": "success",
            "message": "Вход выполнен",
            "user": {
                "id": user_id,
                "role": role,
                "login": tuple.get("Login"),
            }
        }
    except sqlite3.Error as e:
        return {"status": "error", "message": str(e)}
    finally:
        con.close()