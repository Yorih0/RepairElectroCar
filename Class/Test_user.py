from systemData import SystemData
system = SystemData("Data/REP-1.db")

# Пользователь
res, user = system.create_user("ivan", "qwerty", "qwerty", "ivan@example.com", "+375111111111")
print(res, user.Info_all())

# Машина
res, car = system.add_car(user.id, "Tesla Model S", "VIN123456789")
print(res, car.Info_all())

# Работник
res, worker = system.add_worker(user.id, "Электрик", 5, 4.5)
print(res, worker.Info_all())

# Заказ
res, order = system.add_order(car.id, worker.id, "open", "Диагностика электросистемы", "2025-12-19 18:45:00")
print(res, order.Info_all())

# Перенос заказа в историю
res = system.move_orders_to_history(user.id, "customer", "Работы завершены")
print(res)

# История
histories = system.get_history_by_attr("order_id", order.id)
for h in histories:
    print(h.Info_all())
