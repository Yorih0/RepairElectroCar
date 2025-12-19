import sqlite3
import hashlib
import os

class User:
    def __init__(self, id=None, role=None, login=None, password=None, password_r = None,mail=None, phone=None, hashkey=None):
        self.__id = id 
        self.__role = role 
        self.__login = login 
        self.__password = password
        self.__password_r = password_r
        self.__mail = mail 
        self.__phone = phone 
        self.__hashkey = hashkey

    @classmethod 
    def form_login(cls,row:dict):
        return cls(
            login = row.get("login"),
            password = hashlib.sha256(row.get("password").encode("utf-8")).hexdigest()
        )
    @classmethod 
    def form_register(cls,row:dict):
        return cls(
            login = row.get("login"),
            password = hashlib.sha256(row.get("password").encode("utf-8")).hexdigest(),
            password_r = hashlib.sha256(row.get("password_r").encode("utf-8")).hexdigest(),
            mail = row.get("mail"),
            phone = row.get("phone")
        )
    @classmethod
    def db(cls,row:dict):
        return cls(
            id = row.get("id"),
            role = row.get("role"),
            login = row.get("login"),
            password = row.get("password"),
            mail = row.get("mail"),
            phone = row.get("phone"),
            hashkey = row.get("hashkey")
        )
    @classmethod
    def by_hashkey(cls,row:dict,file_db):
        user = User.Find_user_by_atr("hashkey",row.get("hashkey"),file_db)
        if not user:
            return None
        return cls(
            id = user.id,
            role = user.role,
            login = user.login,
            password = user.password,
            mail = user.mail,
            phone = user.phone,
            hashkey = user.hashkey
        )

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
        self.__role = value

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
    @password.setter
    def password(self, value):
        self.__password = value
    
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
        return {
            "role": self.role,
            "login": self.login,
            "mail": self.mail,
            "phone": self.phone
        }
    def Info_all(self):
        return {
            "id":self.id,
            "role": self.role,
            "login": self.login,
            "password":self.password,
            "mail": self.mail,
            "phone": self.phone,
            "hashkey":self.hashkey
        }

    def Create_user(self, file_db):
        result = {
            "status": "error",
            "message": "Неизвестная ошибка"
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
            return result
            
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
            
        finally:
            con.close()

    def Find_user(self, file_db):
        con = sqlite3.connect(f"{file_db}")
        cursor = con.cursor()
        
        try:
            cursor.execute("SELECT id, role,login,password, mail, phone,hashkey FROM Users WHERE login = ?", (self.login,))
            row = cursor.fetchone()
            
            result = {
                "status": "error",
                "message": "Логин не найден или неверный пароль"
            }
            
            if not row:
                return result
                
            password_db = row[3]

            if self.password != password_db:
                result['message'] = "Неверный пароль"
                return result

            self.id = row[0]
            self.role = row[1]
            self.login = row[2]
            self.password = row[3]
            self.mail = row[4]
            self.phone = row[5]
            self.hashkey = row[6]
            
            result["status"] = "success"
            result["message"] = "Вход выполнен"
            return result
            
        except sqlite3.Error as e:
            result = {
                "status": "error",
                "message": str(e),
            }
            return result
            
        finally:
            con.close()

    def Delete_user(self, file_db):
        result = {
            "status": "error",
            "message": "Неизвестная ошибка"
        }

        if not self.id:
            result["message"] = "ID пользователя не задан"
            return result

        con = sqlite3.connect(f"{file_db}")
        cursor = con.cursor()

        try:
            con.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM Users WHERE id = ?", (self.id,))
            con.commit()

            result["status"] = "success"
            result["message"] = "Пользователь удалён"
            return result

        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result

        finally:
            con.close()

    def Update_user(self, file_db):
        result = {
            "status": "error",
            "message": "Неизвестная ошибка"
        }

        if not self.id:
            result["message"] = "ID пользователя не задан"
            return result

        con = sqlite3.connect(f"{file_db}")
        cursor = con.cursor()

        try:
            con.execute("BEGIN TRANSACTION")

            cursor.execute("SELECT id FROM Users WHERE login = ? AND id != ?", (self.login, self.id))
            if cursor.fetchone():
                result["message"] = "Такой логин уже существует"
                con.rollback()
                return result

            cursor.execute("SELECT id FROM Users WHERE mail = ? AND id != ?", (self.mail, self.id))
            if cursor.fetchone():
                result["message"] = "Такая почта уже зарегистрирована"
                con.rollback()
                return result

            cursor.execute("SELECT id FROM Users WHERE phone = ? AND id != ?", (self.phone, self.id))
            if cursor.fetchone():
                result["message"] = "Такой телефон уже зарегистрирован"
                con.rollback()
                return result

            cursor.execute("""
                UPDATE Users 
                SET role = ?, login = ?, password = ?, mail = ?, phone = ?, hashkey = ?
                WHERE id = ?
            """, (self.role, self.login, self.password, self.mail, self.phone, self.hashkey, self.id))

            con.commit()
            result["status"] = "success"
            result["message"] = "Данные пользователя обновлены"
            return result

        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
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
            user = User.db(user_data)
            return user
            
        except sqlite3.Error as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None
            
        finally:
            if 'con' in locals():
                con.close()