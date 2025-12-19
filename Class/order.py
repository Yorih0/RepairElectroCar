import sqlite3

class Order:
    def __init__(self, id=None, customer_id=None, worker_id=None,
                 status=None, description=None, created_at=None, finished_at=None):
        self.__id = id
        self.__customer_id = customer_id
        self.__worker_id = worker_id
        self.__status = status
        self.__description = description
        self.__created_at = created_at
        self.__finished_at = finished_at

    # ====== classmethods ======
    @classmethod
    def form_register(cls, row: dict):
        return cls(
            customer_id=row.get("customer_id"),
            worker_id=row.get("worker_id"),
            status=row.get("status"),
            description=row.get("description"),
            created_at=row.get("created_at"),
            finished_at=row.get("finished_at")
        )

    @classmethod
    def db(cls, row: dict):
        return cls(
            id=row.get("id"),
            customer_id=row.get("customer_id"),
            worker_id=row.get("worker_id"),
            status=row.get("status"),
            description=row.get("description"),
            created_at=row.get("created_at"),
            finished_at=row.get("finished_at")
        )

    @classmethod
    def by_id(cls, row: dict, file_db):
        order = Order.Find_order_by_atr("id", row.get("id"), file_db)
        if order:
            return cls(
                id=order.id,
                customer_id=order.customer_id,
                worker_id=order.worker_id,
                status=order.status,
                description=order.description,
                created_at=order.created_at,
                finished_at=order.finished_at
            )
        return None

    # ====== свойства ======
    @property
    def id(self): return getattr(self, "_Order__id", None)
    @id.setter
    def id(self, value):
        if value is not None: self.__id = value
        else: raise ValueError("id не может быть пустым")

    @property
    def customer_id(self): return getattr(self, "_Order__customer_id", None)
    @customer_id.setter
    def customer_id(self, value):
        if value is not None: self.__customer_id = value
        else: raise ValueError("customer_id не может быть пустым")

    @property
    def worker_id(self): return getattr(self, "_Order__worker_id", None)
    @worker_id.setter
    def worker_id(self, value):
        if value is not None: self.__worker_id = value
        else: raise ValueError("worker_id не может быть пустым")

    @property
    def status(self): return getattr(self, "_Order__status", None)
    @status.setter
    def status(self, value):
        if value and isinstance(value, str): self.__status = value
        else: raise ValueError("status должен быть строкой")

    @property
    def description(self): return getattr(self, "_Order__description", None)
    @description.setter
    def description(self, value):
        if value and isinstance(value, str): self.__description = value
        else: raise ValueError("description должен быть строкой")

    @property
    def created_at(self): return getattr(self, "_Order__created_at", None)
    @created_at.setter
    def created_at(self, value):
        if value: self.__created_at = value
        else: raise ValueError("created_at не может быть пустым")

    @property
    def finished_at(self): return getattr(self, "_Order__finished_at", None)
    @finished_at.setter
    def finished_at(self, value):
        if value: self.__finished_at = value
        else: raise ValueError("finished_at не может быть пустым")

    # ====== методы информации ======
    def Info(self):
        return {
            "status": self.status,
            "description": self.description
        }

    def Info_all(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
            "finished_at": self.finished_at
        }

    # ====== CRUD ======
    def Add_order(self, file_db):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        con = sqlite3.connect(file_db)
        cursor = con.cursor()
        try:
            con.execute("BEGIN TRANSACTION")
            if self.id:
                cursor.execute("""UPDATE Orders SET customer_id=?, worker_id=?, status=?, 
                                  description=?, created_at=?, finished_at=? WHERE id=?""",
                               (self.customer_id, self.worker_id, self.status,
                                self.description, self.created_at, self.finished_at, self.id))
            else:
                cursor.execute("""INSERT INTO Orders (customer_id, worker_id, status, description, created_at, finished_at) 
                                  VALUES (?, ?, ?, ?, ?, ?)""",
                               (self.customer_id, self.worker_id, self.status,
                                self.description, self.created_at, self.finished_at))
                self.id = cursor.lastrowid
            con.commit()
            result["status"] = "success"
            result["message"] = "Заказ сохранён"
            return result
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
        finally:
            con.close()

    def Remove_order(self, file_db):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        if not self.id:
            result["message"] = "ID заказа не задан"
            return result
        con = sqlite3.connect(file_db)
        cursor = con.cursor()
        try:
            con.execute("BEGIN TRANSACTION")
            cursor.execute("DELETE FROM Orders WHERE id = ?", (self.id,))
            con.commit()
            result["status"] = "success"
            result["message"] = "Заказ удалён"
            return result
        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result
        finally:
            con.close()

    # ====== поиск ======
    @staticmethod
    def Find_order_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(file_db)
            cursor = con.cursor()
            match attribute:
                case "id":
                    query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE id = ?"
                case "customer_id":
                    query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE customer_id = ?"
                case "worker_id":
                    query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE worker_id = ?"
                case "status":
                    query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE status = ?"
                case _:
                    return None
            cursor.execute(query, (value,))
            row = cursor.fetchone()
            if row is None:
                return None
            order_data = {
                "id": row[0],
                "customer_id": row[1],
                "worker_id": row[2],
                "status": row[3],
                "description": row[4],
                "created_at": row[5],
                "finished_at": row[6]
            }
            return Order.db(order_data)
        except sqlite3.Error as e:
            print(f"Ошибка при поиске заказа: {e}")
            return None
        finally:
            con.close()

    @staticmethod
    def Get_orders_by_user(user_id, role, file_db):
        try:
            con = sqlite3.connect(file_db)
            cursor = con.cursor()
            if role == "customer":
                query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE customer_id = ?"
            elif role == "worker":
                query = "SELECT id, customer_id, worker_id, status, description, created_at, finished_at FROM Orders WHERE worker_id = ?"
            else:
                return []
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [Order.db({
                "id": row[0],
                "customer_id": row[1],
                "worker_id": row[2],
                "status": row[3],
                "description": row[4],
                "created_at": row[5],
                "finished_at": row[6]
            }) for row in rows]
        except sqlite3.Error as e:
            print(f"Ошибка при получении заказов пользователя: {e}")
            return []
        finally:
            con.close()

    @staticmethod
    def Move_orders_to_history_by_user(user_id, role, file_db, comment="Заказ завершён"):
        result = {"status": "error", "message": "Неизвестная ошибка"}
        try:
            con = sqlite3.connect(file_db)
            cursor = con.cursor()
            con.execute("BEGIN TRANSACTION")

            if role == "customer":
                select_query = "SELECT id, status FROM Orders WHERE customer_id = ?"
            elif role == "worker":
                select_query = "SELECT id, status FROM Orders WHERE worker_id = ?"
            else:
                result["message"] = "Некорректная роль"
                return result

            cursor.execute(select_query, (user_id,))
            orders = cursor.fetchall()

            if not orders:
                con.rollback()
                result["message"] = "Нет заказов для переноса"
                return result

            for order_id, status in orders:
                cursor.execute("""
                    INSERT INTO History_of_orders (order_id, status, timestamp, comment)
                    VALUES (?, ?, datetime('now'), ?)
                """, (order_id, status, comment))
                cursor.execute("DELETE FROM Orders WHERE id = ?", (order_id,))

            con.commit()
            result["status"] = "success"
            result["message"] = f"Перенесено заказов: {len(orders)}"
            return result

        except sqlite3.Error as e:
            con.rollback()
            result["message"] = f"Ошибка базы данных: {str(e)}"
            return result

        finally:
            con.close()
