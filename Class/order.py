import sqlite3

class Order:
    def __init__(self, dict):
        self.id = None
        self.customer_id = None
        self.worker_id = None

        if dict.get("id") is not None: 
            self.__id = dict.get("id")
        if dict.get("customer_id") is not None: 
            self.__customer_id = dict.get("customer_id")
        if dict.get("worker_id") is not None: 
            self.__worker_id = dict.get("worker_id")
        if dict.get("status") is not None: 
            self.__status = dict.get("status")
        if dict.get("description") is not None: 
            self.__description = dict.get("description")
        if dict.get("created_at") is not None: 
            self.__created_at = dict.get("created_at")
        if dict.get("finished_at") is not None: 
            self.__finished_at = dict.get("finished_at")

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

    def Info(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "description": self.description,
            "created_at": self.created_at,
            "finished_at": self.finished_at
        }

    @staticmethod
    def Find_order_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
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
            if row is None: return None
            order_data = {
                "id": row[0],
                "customer_id": row[1],
                "worker_id": row[2],
                "status": row[3],
                "description": row[4],
                "created_at": row[5],
                "finished_at": row[6]
            }
            return Order(order_data)
        except sqlite3.Error as e:
            print(f"Ошибка при поиске заказа: {e}")
            return None
        finally:
            if 'con' in locals(): con.close()

    def Add_order(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            if self.id:
                cursor.execute("""UPDATE Orders SET customer_id = ?, worker_id = ?, status = ?, 
                                  description = ?, created_at = ?, finished_at = ? WHERE id = ?""",
                               (self.customer_id, self.worker_id, self.status, self.description,
                                self.created_at, self.finished_at, self.id))
            else:
                cursor.execute("""INSERT INTO Orders (customer_id, worker_id, status, description, created_at, finished_at) 
                                  VALUES (?, ?, ?, ?, ?, ?)""",
                               (self.customer_id, self.worker_id, self.status, self.description,
                                self.created_at, self.finished_at))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении/обновлении заказа: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()

    def Remove_order(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            if self.id is None: raise ValueError("Невозможно удалить: id не задан")
            cursor.execute("DELETE FROM Orders WHERE id = ?", (self.id,))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заказа: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()
    @staticmethod
    def Get_orders_by_user(user_id, role, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()

            if role == "customer":
                query = """SELECT id, customer_id, worker_id, status, description, created_at, finished_at
                        FROM Orders WHERE customer_id = ?"""
            elif role == "worker":
                query = """SELECT id, customer_id, worker_id, status, description, created_at, finished_at
                        FROM Orders WHERE worker_id = ?"""
            else:
                return []

            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

            orders = []
            for row in rows:
                orders.append(Order({
                    "id": row[0],
                    "customer_id": row[1],
                    "worker_id": row[2],
                    "status": row[3],
                    "description": row[4],
                    "created_at": row[5],
                    "finished_at": row[6]
                }))

            return orders

        except sqlite3.Error as e:
            print(f"Ошибка при получении заказов пользователя: {e}")
            return []

        finally:
            if 'con' in locals():
                con.close()
                
    @staticmethod
    def Move_orders_to_history_by_user(user_id, role, file_db, comment="Заказ завершён"):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            con.execute("BEGIN TRANSACTION")

            if role == "customer":
                select_query = """SELECT id, status FROM Orders WHERE customer_id = ?"""
            elif role == "worker":
                select_query = """SELECT id, status FROM Orders WHERE worker_id = ?"""
            else:
                return 0

            cursor.execute(select_query, (user_id,))
            orders = cursor.fetchall()

            if not orders:
                con.rollback()
                return 0

            for order_id, status in orders:
                cursor.execute("""
                    INSERT INTO History_of_orders (order_id, status, timestamp, comment)
                    VALUES (?, ?, datetime('now'), ?)
                """, (order_id, status, comment))

                cursor.execute("DELETE FROM Orders WHERE id = ?", (order_id,))

            con.commit()
            return len(orders)

        except sqlite3.Error as e:
            con.rollback()
            print(f"Ошибка при переносе заказов в историю: {e}")
            return 0

        finally:
            if 'con' in locals():
                con.close()
