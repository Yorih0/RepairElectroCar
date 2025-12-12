import sqlite3

class HistoryOfOrder:
    def __init__(self, data: dict):
        if data.get("id") is not None:
            self.__id = data.get("id")
        if data.get("order_id") is not None:
            self.__order_id = data.get("order_id")
        if data.get("status") is not None:
            self.__status = data.get("status")
        if data.get("timestamp") is not None:
            self.__timestamp = data.get("timestamp")
        if data.get("comment") is not None:
            self.__comment = data.get("comment")

    @property
    def id(self): return getattr(self, "_HistoryOfOrder__id", None)
    @id.setter
    def id(self, value):
        if value is not None: self.__id = value
        else: raise ValueError("id не может быть пустым")

    @property
    def order_id(self): return getattr(self, "_HistoryOfOrder__order_id", None)
    @order_id.setter
    def order_id(self, value):
        if value is not None: self.__order_id = value
        else: raise ValueError("order_id не может быть пустым")

    @property
    def status(self): return getattr(self, "_HistoryOfOrder__status", None)
    @status.setter
    def status(self, value):
        if value and isinstance(value, str): self.__status = value
        else: raise ValueError("status должен быть строкой")

    @property
    def timestamp(self): return getattr(self, "_HistoryOfOrder__timestamp", None)
    @timestamp.setter
    def timestamp(self, value):
        if value: self.__timestamp = value
        else: raise ValueError("timestamp не может быть пустым")

    @property
    def comment(self): return getattr(self, "_HistoryOfOrder__comment", None)
    @comment.setter
    def comment(self, value):
        if value and isinstance(value, str): self.__comment = value
        else: raise ValueError("comment должен быть строкой")

    def Info(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "status": self.status,
            "timestamp": self.timestamp,
            "comment": self.comment
        }

    # --- Методы работы с БД ---
    def Add_history(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            cursor.execute("""INSERT INTO History_of_orders (order_id, status, timestamp, comment) 
                              VALUES (?, ?, ?, ?)""",
                           (self.order_id, self.status, self.timestamp, self.comment))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении истории: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()

    def Remove_history(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            if self.id is None: raise ValueError("Невозможно удалить: id не задан")
            cursor.execute("DELETE FROM History_of_orders WHERE id = ?", (self.id,))
            con.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении истории: {e}")
            return False
        finally:
            if 'con' in locals(): con.close()

    @staticmethod
    def Find_history_by_order(order_id, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            cursor.execute("""SELECT id, order_id, status, timestamp, comment 
                              FROM History_of_orders WHERE order_id = ?""", (order_id,))
            rows = cursor.fetchall()
            if not rows: return []
            histories = []
            for row in rows:
                histories.append(HistoryOfOrder({
                    "id": row[0],
                    "order_id": row[1],
                    "status": row[2],
                    "timestamp": row[3],
                    "comment": row[4]
                }))
            return histories
        except sqlite3.Error as e:
            print(f"Ошибка при поиске истории: {e}")
            return []
        finally:
            if 'con' in locals(): con.close()
