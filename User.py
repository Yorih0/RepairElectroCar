import sqlite3
class User:
    def __init__(self,tuple):
        self.__login = tuple.get("Login")
        self.__password = tuple.get("Password")
        self.__mail = tuple.get("Mail")
        self.__phone = tuple.get("Phone")
        # self.__hashkey = tuple.get("hashkey")

    def Info(self):
        # print("Зарегистрировать:",self.__registred)
        print("Имя:", self.__login)
        print("Пароль:", self.__password)
        print("Почта:", self.__mail)
        print("Телефон:", self.__phone)
        # print("Ключ:",self.__hashkey)
    
    def FindUserByLogin(login):
        con = sqlite3.connect("Data/Data.db")
        cursor = con.cursor()

        cursor.execute("SELECT login, password, mail, phone, hashkey FROM user WHERE login = ?", (login,))
        row = cursor.fetchone()
        con.close()

        if row:
            return User(True, *row)
        else:
            print("Пользователь не найден.")
            return None

    def Save(self):
        con = sqlite3.connect("Data/Data.db")
        cursor = con.cursor()

        # cursor.execute("""
        #     INSERT INTO user (login, password, mail, phone, hashkey)
        #     VALUES (?, ?, ?, ?, ?)
        # """, (self.__login, self.__password, self.__mail, self.__phone, self.__hashkey))
        cursor.execute("""
            INSERT INTO user (login, password, mail, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (self.__login, self.__password, self.__mail, self.__phone))

        con.commit()
        con.close()
        print("Пользователь сохранён.")    