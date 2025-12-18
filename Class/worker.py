import sqlite3

class Worker:
    def __init__(self, dict):
        self.__id = None
        self.__user_id = None
        self.__specialization = None
        self.__experience = None
        self.__rating = None

        if dict.get("id") is not None:
            self.__id = dict.get("id")
        if dict.get("user_id") is not None:
            self.__user_id = dict.get("user_id")
        if dict.get("specialization") is not None:
            self.__specialization = dict.get("specialization")
        if dict.get("experience") is not None:
            self.__experience = int(dict.get("experience"))
        if dict.get("rating") is not None:
            self.__rating = float(dict.get("rating"))

    @property
    def id(self): return getattr(self, "_Worker__id", None)
    @id.setter
    def id(self, value):
        if value is not None: self.__id = value
        else: raise ValueError("id не может быть пустым")

    @property
    def user_id(self): return getattr(self, "_Worker__user_id", None)
    @user_id.setter
    def user_id(self, value):
        if value is not None: self.__user_id = value
        else: raise ValueError("user_id не может быть пустым")

    @property
    def specialization(self): return getattr(self, "_Worker__specialization", None)
    @specialization.setter
    def specialization(self, value):
        if value and isinstance(value, str): self.__specialization = value
        else: raise ValueError("specialization должна быть строкой")

    @property
    def experience(self): return getattr(self, "_Worker__experience", None)
    @experience.setter
    def experience(self, value):
        if isinstance(value, int) and value >= 0: self.__experience = value
        else: raise ValueError("experience должен быть целым числом >= 0")

    @property
    def rating(self): return getattr(self, "_Worker__rating", None)
    @rating.setter
    def rating(self, value):
        if isinstance(value, (int, float)) and 0 <= value <= 5: self.__rating = float(value)
        else: raise ValueError("rating должен быть числом от 0 до 5")

    def Info(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "specialization": self.specialization,
            "experience": self.experience,
            "rating": self.rating
        }

    @staticmethod
    def Find_worker_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            match attribute:
                case "id":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE id = ?"
                case "user_id":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE user_id = ?"
                case "specialization":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE specialization = ?"
                case _:
                    return None
            cursor.execute(query, (value,))
            row = cursor.fetchone()
            if row is None: return None
            worker_data = {
                "id": row[0],
                "user_id": row[1],
                "specialization": row[2],
                "experience": row[3],
                "rating": row[4]
            }
            return Worker(worker_data)
        except sqlite3.Error as e:
            print(f"Ошибка при поиске работника: {e}")
            return None
        finally:
            if 'con' in locals(): con.close()

    def Add_worker(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            cursor.execute("SELECT id FROM Workers WHERE user_id = ?", (self.user_id,))
            existing_worker = cursor.fetchone()
            if existing_worker:
                cursor.execute("""UPDATE Workers SET specialization = ?, experience = ?, rating = ? 
                                  WHERE user_id = ?""",
                               (self.specialization, self.experience, self.rating, self.user_id))
            else:
                cursor.execute("""INSERT INTO Workers (user_id, specialization, experience, rating) 
                                  VALUES (?, ?, ?, ?)""",
                               (self.user_id, self.specialization, self.experience, self.rating))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении работника: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()

    def Remove_worker(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            if self.id is None: raise ValueError("Невозможно удалить: id не задан")
            cursor.execute("DELETE FROM Workers WHERE id = ?", (self.id,))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении работника: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()
    @staticmethod
    def Get_all_workers_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()

            match attribute:
                case "specialization":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE specialization = ?"
                case "user_id":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE user_id = ?"
                case "rating":
                    query = "SELECT id, user_id, specialization, experience, rating FROM Workers WHERE rating = ?"
                case _:
                    return []

            cursor.execute(query, (value,))
            rows = cursor.fetchall()

            workers = []
            for row in rows:
                worker_data = {
                    "id": row[0],
                    "user_id": row[1],
                    "specialization": row[2],
                    "experience": row[3],
                    "rating": row[4]
                }
                workers.append(Worker(worker_data))

            return workers

        except sqlite3.Error as e:
            print(f"Ошибка при получении работников: {e}")
            return []

        finally:
            if 'con' in locals():
                con.close()
    @staticmethod
    def Remove_all_workers_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(file_db)
            cursor = con.cursor()

            match attribute:
                case "specialization":
                    check_query = "SELECT COUNT(*) FROM Workers WHERE specialization = ?"
                    delete_query = "DELETE FROM Workers WHERE specialization = ?"
                case "user_id":
                    check_query = "SELECT COUNT(*) FROM Workers WHERE user_id = ?"
                    delete_query = "DELETE FROM Workers WHERE user_id = ?"
                case "rating":
                    check_query = "SELECT COUNT(*) FROM Workers WHERE rating = ?"
                    delete_query = "DELETE FROM Workers WHERE rating = ?"
                case _:
                    raise ValueError("Недопустимый атрибут для удаления")

            cursor.execute(check_query, (value,))
            count = cursor.fetchone()[0]

            if count == 0:
                print("Работники с таким параметром не найдены")
                return 0

            cursor.execute(delete_query, (value,))
            con.commit()

            return cursor.rowcount

        except (sqlite3.Error, ValueError) as e:
            print(f"Ошибка при удалении работников: {e}")
            return 0

        finally:
            if 'con' in locals():
                con.close()

