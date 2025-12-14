import sqlite3
import hashlib
import os

class User:
    def __init__(self, dict, file_db=None, from_db=False):
        # Инициализируем все атрибуты как None
        self.__id = None
        self.__role = None
        self.__login = None
        self.__password = None
        self.__mail = None
        self.__phone = None
        self.__hashkey = None
        
        # Обработка hashkey с file_db
        if dict.get("hashkey") and (file_db is not None):
            hashkey_value = dict.get("hashkey")
            # Проверяем, что hashkey не 'None' и не пустая строка
            if hashkey_value and hashkey_value != 'None' and hashkey_value != '':
                user = User.Find_user_by_atr("hashkey", hashkey_value, file_db)
                # Правильная проверка на None
                if user is not None:
                    # Копируем все атрибуты из найденного пользователя
                    self.__id = user.id
                    self.__role = user.role
                    self.__login = user.login
                    self.__password = user.password
                    self.__mail = user.mail
                    self.__phone = user.phone
                    self.__hashkey = user.hashkey
                    # Возвращаемся - объект полностью инициализирован
                    return
        
        # Устанавливаем значения из словаря (этот код выполняется только если пользователь не найден по hashkey)
        if dict.get("id") is not None:
            self.__id = dict.get("id")

        if dict.get("role") is not None:
            self.__role = dict.get("role")

        if dict.get("login") is not None:
            self.__login = dict.get("login")
        
        if dict.get("password") is not None:
            if from_db:
                self.__password = dict.get("password")
            else:
                self.__password = hashlib.sha256(dict.get("password").encode("utf-8")).hexdigest()
        
        if dict.get("password_repeat") is not None:
            password_repeat = dict.get("password_repeat")
            self.__password_r = hashlib.sha256(password_repeat.encode("utf-8")).hexdigest() 
        
        if dict.get("mail") is not None:
            self.__mail = dict.get("mail")
        
        if dict.get("phone") is not None:
            self.__phone = dict.get("phone")
        
        # Устанавливаем hashkey только если его еще нет
        if dict.get("hashkey") is not None and self.__hashkey is None:
            hashkey_value = dict.get("hashkey")
            if hashkey_value != 'None' and hashkey_value != '':
                self.__hashkey = hashkey_value    

    @property
    def id(self):
        return getattr(self, "_User__id", None)
    @id.setter
    def id(self,value):
        self.__id = value

    @property
    def role(self):
        return getattr(self, "_User__role", None)

    @role.setter
    def role(self, value):
        if value and isinstance(value, str):
            self.__role = value
        else:
            raise ValueError("Роль должна быть строкой")

    @property
    def login(self):
        return getattr(self, "_User__login", None)

    @login.setter
    def login(self, value):
        if value and isinstance(value, str):
            self.__login = value
        else:
            raise ValueError("Логин должен быть непустой строкой")

    @property
    def password(self):
        return getattr(self, "_User__password", None)

    @property
    def password_r(self):
        return getattr(self, "_User__password_r", None)

    @property
    def mail(self):
        return getattr(self, "_User__mail", None)

    @mail.setter
    def mail(self, value):
        if value and "@" in value:
            self.__mail = value
        else:
            raise ValueError("Некорректный email")

    @property
    def phone(self):
        return getattr(self, "_User__phone", None)

    @phone.setter
    def phone(self, value):
        if value:
            digits = ''.join(filter(str.isdigit, str(value)))
            if digits:
                self.__phone = value
            else:
                raise ValueError("Телефон должен содержать цифры")
        else:
            raise ValueError("Телефон не может быть пустым")

    @property
    def hashkey(self):
        return getattr(self, "_User__hashkey", None)
    @hashkey.setter
    def hashkey(self, value):
        self.__hashkey = value

    def Info(self):
        info = {
            "id": self.id,
            "role": self.role,
            "login": self.login,
            "password": self.password,
            "mail": self.mail,
            "phone": self.phone,
            "hashkey": self.hashkey,
        }
        return info


    def Register_user(self, file_db):
        result = {
            "status": "error",
            "message": "Неизвестная ошибка",
            "user": None
        }
        if self.password != self.password_r:
            result['message'] = "Пароли не совпадают"
            return result

        con = sqlite3.connect(f"{file_db}")
        cursor = con.cursor()
        
        try:
            con.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT id FROM Users WHERE login = ?", (self.login,))
            if cursor.fetchone():
                result['message'] = "Такой логин уже существует"
                con.rollback()
                return result
            
            cursor.execute("SELECT id FROM Users WHERE mail = ?", (self.mail,))
            if cursor.fetchone():
                result['message'] = "Такая почта уже зарегистрирована"
                con.rollback()
                return result 
                
            cursor.execute("SELECT id FROM Users WHERE phone = ?", (self.phone,))
            if cursor.fetchone():
                result['message'] = "Такой телефон уже зарегистрирован"
                con.rollback()
                return result
            
            random_bytes = os.urandom(16)
            self.hashkey = hashlib.sha256(random_bytes).hexdigest()

            cursor.execute("""INSERT INTO Users (role, login, password, mail, phone, hashkey) 
                  VALUES (?, ?, ?, ?, ?, ?)""",
               ("customers", self.login, self.password, self.mail, 
                self.phone, self.hashkey))
            
            self.id = cursor.lastrowid
            con.commit()

            result["status"] = "success"
            result["message"] = "Пользователь успешно зарегистрированы"
            result["user"] = self
            return result
            
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
            
        finally:
            con.close()

    def Login_user(self, file_db):
        con = sqlite3.connect(f"{file_db}")
        cursor = con.cursor()
        
        try:
            cursor.execute("SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE login = ?", (self.login,))
            row = cursor.fetchone()
            
            result = {
                "status": "error",
                "message": "Логин не найден или неверный пароль",
                "user": None
            }
            
            if not row:
                return result
                
            password_db = row[3]

            if self.password != password_db:
                result['message'] = "Неверный пароль"
                return result
            
            print(row)
            user_data = {
                "id": row[0],
                "role": row[1],
                "login": row[2],
                "password": row[3],
                "mail": row[4],
                "phone": row[5],
                "hashkey": row[6]
            }
            print(user_data)
            user = User(user_data,from_db=True)
            result["status"] = "success"
            result["message"] = "Вход выполнен"
            result["user"] = user
            return result
            
        except sqlite3.Error as e:
            result = {
                "status": "error",
                "message": str(e),
                "user": None
            }
            return result
            
        finally:
            con.close()

    @staticmethod
    def Find_user_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()

            match attribute:
                case "hashkey":
                    query = "SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE hashkey = ?"
                case "login":
                    query = "SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE login = ?"
                case "password":
                    query = "SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE password = ?"
                case "mail":
                    query = "SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE mail = ?"
                case "phone":
                    query = "SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE phone = ?"
                case _:
                    return None
            
            cursor.execute(query, (value,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            user_data = {
                "id": row[0],
                "role":row[1],
                "login": row[2],
                "password": row[3],
                "mail": row[4],
                "phone": row[5],
                "hashkey": row[6]
            }
            user = User(user_data,from_db=True)
            return user
            
        except sqlite3.Error as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None
            
        finally:
            if 'con' in locals():
                con.close()