from systemData import SystemData
import os

def base():
    print("Текущая рабочая директория:", os.getcwd())
    print(os.getcwd())
    file_db = "Data/REP-1.db"
    print(f"Используем базу данных: {file_db}")
    
    user_dict = {
        "login": "ivan456",
        "password": "securepass",
        "password_repeat": "securepass",
        "mail": "ivan456@example.com",
        "phone": "+375291234568"
    }

    system = SystemData(user_dict,file_db)

    print("Регистрация пользователя...")
    reg_result = system.Register_user()
    print(reg_result)

    car_dict = {
        "user_id": system.User.id,
        "car_model": "Audi A4",
        "car_vin": "WAUZZZ8K9AA123456"
    }

    system.Customer = system.Customer.__class__(car_dict) 
    print("Добавление автомобиля...")
    car_result = system.Add_customer()
    print("Автомобиль добавлен:", car_result)

    worker_dict = {
        "user_id": system.User.id,
        "specialization": "Механик",
        "experience": 5,
        "rating": 4.7
    }
    system.Worker = system.Worker.__class__(worker_dict)
    print("Добавление работника...")
    worker_result = system.Add_worker()
    print("Работник добавлен:", worker_result)

    order_dict = {
        "customer_id": system.Customer.user_id,
        "worker_id": system.Worker.user_id,
        "status": "new",
        "description": "Диагностика двигателя",
        "created_at": "2025-12-11 22:05",
        "finished_at": None
    }
    system.Order = system.Order.__class__(order_dict)
    print("Создание заказа...")
    order_result = system.Add_order()
    print("Заказ создан:", order_result)

    history_dict = {
        "order_id": system.Order.id,
        "status": "in_progress",
        "timestamp": "2025-12-11 22:10",
        "comment": "Начата диагностика"
    }
    system.historyOfOrder = system.historyOfOrder.__class__(history_dict)
    print("Добавление истории заказа...")
    history_result = system.Add_history()
    print("История добавлена:", history_result)

    print("\nИтоговое состояние:")
    print(system.Info())

if __name__ == "__main__":
    base()
