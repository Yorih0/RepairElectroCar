import sqlite3
import hashlib
import os

def Create_Data_Table(folder, name_db, name, password):
    con = sqlite3.connect(f"{folder}/{name_db}.db")
    cursor = con.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL,
                    mail TEXT,
                    phone TEXT,
                    hashkey TEXT
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
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    cursor.execute("""INSERT INTO Users (role, login, password) VALUES (?, ?, ?)""",
                   ("admin", name, password_hash ))
    con.commit()
    con.close()

if __name__ == "__main__":
    print("Создание базы данных")
    name_db = input("Введите название базы данных: ")
    folder = "Data"

    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(os.path.join(folder, name_db + ".db")):
        print("Уже существует")
    else:
        name = input("Введите логин для админа: ")
        password = ""
        while len(password) < 6:
            password = input("Введите пароль для админа: ")
            if len(password) < 6:
                print("Слишком короткий пароль")
        
        Create_Data_Table(folder, name_db, name, password) 
