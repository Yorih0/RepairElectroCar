from user import User
from customer import Customer
from worker import Worker
from order import Order
from historyOfOrder import HistoryOfOrder


class SystemData:
    def __init__(self, dict, file_db):
        try:
            self.__user = User(dict,file_db)
            # self.__customer = Customer(dict,file_db)
            # self.__worker = Worker(dict,file_db)
            # self.__order = Order(dict,file_db)
            # self.__historyOfOrder = HistoryOfOrder(dict,file_db)
            self.__file_db = file_db
        except ImportError as e:
            raise ImportError(f"Ошибка импорта модулей: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка инициализации SystemData: {e}")

    @property
    def User(self): return self.__user
    @User.setter
    def User(self, value):
        if isinstance(value, User): self.__user = value
        else: raise ValueError("User должен быть экземпляром класса User")

    @property
    def Customer(self): return self.__customer
    @Customer.setter
    def Customer(self, value):
        if isinstance(value, Customer): self.__customer = value
        else: raise ValueError("Customer должен быть экземпляром класса Customer")

    @property
    def Worker(self): return self.__worker
    @Worker.setter
    def Worker(self, value):
        if isinstance(value, Worker): self.__worker = value
        else: raise ValueError("Worker должен быть экземпляром класса Worker")

    @property
    def Order(self): return self.__order
    @Order.setter
    def Order(self, value):
        if isinstance(value, Order): self.__order = value
        else: raise ValueError("Order должен быть экземпляром класса Order")

    @property
    def historyOfOrder(self): return self.__historyOfOrder
    @historyOfOrder.setter
    def historyOfOrder(self, value):
        if isinstance(value, HistoryOfOrder): self.__historyOfOrder = value
        else: raise ValueError("historyOfOrder должен быть экземпляром класса HistoryOfOrder")

    @property
    def file_db(self): return self.__file_db
    @file_db.setter
    def file_db(self, value):
        if value and isinstance(value, str): self.__file_db = value
        else: raise ValueError("file_db должен быть непустой строкой")

    def Info(self):
        return {
            "User": self.User.Info(),
            "Customer": self.Customer.Info(),
            "Worker": self.Worker.Info(),
            "Order": self.Order.Info(),
            "historyOfOrder": self.historyOfOrder.Info(),
            "file_db": self.file_db
        }

    def Register_user(self):
        data = self.User.Register_user(self.file_db)
        if(data["status"] == "success"):
            self.User = data["user"]
        return data

    def Login_user(self):
        data = self.User.Login_user(self.file_db)
        if(data["status"] == "success"):
            self.User = data["user"]
        return data

    def Add_customer(self):
        return self.Customer.Add_car(self.User, self.file_db)

    def Remove_customer(self):
        return self.Customer.Remove_car(self.file_db)

    def Add_worker(self):
        return self.Worker.Add_worker(self.file_db)

    def Remove_worker(self):
        return self.Worker.Remove_worker(self.file_db)

    def Add_order(self):
        return self.Order.Add_order(self.file_db)

    def Remove_order(self):
        return self.Order.Remove_order(self.file_db)

    def Add_history(self):
        return self.historyOfOrder.Add_history(self.file_db)

    def Remove_history(self):
        return self.historyOfOrder.Remove_history(self.file_db)
