import sqlite3

class Worker:
    def __init__(self, id=None, user_id=None, specialization=None, experience=None, rating=None):
        self.__id = id
        self.__user_id = user_id
        self.__specialization = specialization
        self.__experience = experience
        self.__rating = rating

    # ====== classmethods ======
    @classmethod
    def form_register(cls, row: dict):
        return cls(
            user_id=row.get("user_id"),
            specialization=row.get("specialization"),
            experience=int(row.get("experience", 0)),
            rating=float(row.get("rating", 0))
        )

    @classmethod
    def db(cls, row: dict):
        return cls(
            id=row.get("id"),
            user_id=row.get("user_id"),
            specialization=row.get("specialization"),
            experience=row.get("experience"),
            rating=row.get("rating")
        )

    @classmethod
    def by_id(cls, row: dict, file_db):
        worker = Worker.Find_worker_by_atr("id", row.get("id"), file_db)
        if worker:
            return cls(
                id=worker.id,
                user_id=worker.user_id,
                specialization=worker.specialization,
                experience=worker.experience,
                rating=worker.rating
            )
        return None

    # ====== свойства ======
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

    # ====== методы информации ======
    def Info(self):
        return {
            "specialization": self.specialization,
            "experience": self.experience,
            "rating": self.rating
        }

    def Info_all(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "specialization": self.specialization,
            "experience": self.experience,
            "rating": self.rating
        }

    # ====== CRUD ======
    def Add_worker(self, file_db):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        con = sqlite3.connect(file_db)
        cursor = con.cursor()
        try:
            con.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT id FROM Workers WHERE user_id = ?", (self.user_id,))
            existing_worker = cursor.fetchone()
            if existing_worker:
                cursor.execute("""UPDATE Workers SET specialization=?, experience=?, rating=? 
                                  WHERE user_id=?""",
                               (self.specialization, self.experience, self.rating, self.user_id))
                self.id = existing_worker[0]
            else:
                cursor.execute("""INSERT INTO Workers (user_id, specialization, experience, rating) 
                                  VALUES (?, ?, ?, ?)""",
                               (self.user_id, self.specialization, self.experience, self.rating))
                self.id = cursor.lastrowid
            con.commit()
            result["status"] = "success"
            result["message"] = "Работник сохранён"
            return result
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
        finally:
            con.close()

    def Remove_worker(self, file_db):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        if not self.id:
            result["message"] = "ID работника не задан"
            return result
        con = sqlite3.connect(file_db)
        cursor = con.cursor()
        try:
            con.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM Workers WHERE id = ?", (self.id,))
            con.commit()
            result["status"] = "success"
            result["message"] = "Работник удалён"
            return result
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
        finally:
            con.close()

    # ====== поиск ======
    @staticmethod
    def Find_worker_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(file_db)
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
            if row is None:
                return None
            worker_data = {
                "id": row[0],
                "user_id": row[1],
                "specialization": row[2],
                "experience": row[3],
                "rating": row[4]
            }
            return Worker.db(worker_data)
        except sqlite3.Error as e:
            print(f"Ошибка при поиске работника: {e}")
            return None
        finally:
            con.close()

    @staticmethod
    def Get_all_workers_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(file_db)
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
            return [Worker.db({
                "id": row[0],
                "user_id": row[1],
                "specialization": row[2],
                "experience": row[3],
                "rating": row[4]
            }) for row in rows]
        except sqlite3.Error as e:
            print(f"Ошибка при получении работников: {e}")
            return []
        finally:
            con.close()

    @staticmethod
    def Remove_all_workers_by_atr(attribute, value, file_db):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        try:
            con = sqlite3.connect(file_db)
            cursor = con.cursor()
            match attribute:
                case "specialization":
                    delete_query = "DELETE FROM Workers WHERE specialization = ?"
                case "user_id":
                    delete_query = "DELETE FROM Workers WHERE user_id = ?"
                case "rating":
                    delete_query = "DELETE FROM Workers WHERE rating = ?"
                case _:
                    result["message"] = "Недопустимый атрибут для удаления"
                    return result
            cursor.execute(delete_query, (value,))
            deleted = cursor.rowcount
            con.commit()
            result["status"] = "success"
            result["message"] = f"Удалено работников: {deleted}"
            return result
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
        finally:
            con.close()
