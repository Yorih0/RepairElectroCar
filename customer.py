import sqlite3

class Customer:
    def __init__(self, dict):
        if dict.get("id") is not None:
            self.__id = dict.get("id")
        if dict.get("user_id") is not None:
            self.__user_id = dict.get("user_id")
        if dict.get("car_model") is not None:
            self.__car_model = dict.get("car_model")
        if dict.get("car_vin") is not None:
            self.__car_vin = dict.get("car_vin")

    @property
    def id(self): return getattr(self, "_Customer__id", None)

    @id.setter
    def id(self, value):
        if value is not None:
            self.__id = value
        else:
            raise ValueError("id не может быть пустым")

    @property
    def user_id(self): return getattr(self, "_Customer__user_id", None)

    @user_id.setter
    def user_id(self, value):
        if value is not None:
            self.__user_id = value
        else:
            raise ValueError("user_id не может быть пустым")

    @property
    def car_model(self): return getattr(self, "_Customer__car_model", None)

    @car_model.setter
    def car_model(self, value):
        if value and isinstance(value, str):
            self.__car_model = value
        else:
            raise ValueError("car_model должен быть строкой")

    @property
    def car_vin(self): return getattr(self, "_Customer__car_vin", None)

    @car_vin.setter
    def car_vin(self, value):
        if value and isinstance(value, str):
            self.__car_vin = value
        else:
            raise ValueError("car_vin должен быть строкой")

    def Info(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "car_model": self.car_model,
            "car_vin": self.car_vin
        }

    @staticmethod
    def Find_car_by_atr(attribute, value, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()
            
            match attribute:
                case "id":
                    query = "SELECT id, user_id, car_model, car_vin FROM Customers WHERE id = ?"
                case "user_id":
                    query = "SELECT id, user_id, car_model, car_vin FROM Customers WHERE user_id = ?"
                case "car_model":
                    query = "SELECT id, user_id, car_model, car_vin FROM Customers WHERE car_model = ?"
                case "car_vin":
                    query = "SELECT id, user_id, car_model, car_vin FROM Customers WHERE car_vin = ?"
                case _:
                    return None                    
            cursor.execute(query, (value,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            user_data = {
                "id": row[0],
                "user_id": row[1],
                "car_model": row[2],
                "car_vin": row[3],
            }
            customer = Customer(user_data)
            return customer
            
        except sqlite3.Error as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None
            
        finally:
            if 'con' in locals():
                con.close()

    def Add_car(self, user, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()

            cursor.execute("SELECT id FROM Customers WHERE user_id = ?", (user.id,))
            existing_car = cursor.fetchone()
            
            if existing_car:
                cursor.execute("""UPDATE Customers SET car_model = ?, car_vin = ? 
                                WHERE user_id = ?""",(self.car_model, self.car_vin, user.id))
            else:
                cursor.execute("""INSERT INTO Customers (user_id, car_model, car_vin) 
                                VALUES (?, ?, ?)""",(user.id,self.car_model, self.car_vin))
            
            con.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении автомобиля: {e}")
            return False
            
        finally:
            if 'con' in locals():
                con.close()

    def Remove_car(self, file_db):
        try:
            con = sqlite3.connect(f"{file_db}")
            cursor = con.cursor()

            if self.id is None:
                raise ValueError("Невозможно удалить: id не задан")

            cursor.execute("DELETE FROM Customers WHERE id = ?", (self.id,))
            con.commit()

            return True

        except sqlite3.Error as e:
            print(f"Ошибка при удалении автомобиля: {e}")
            return False

        finally:
            if 'con' in locals():
                con.close()
