from user import User
from systemData import SystemData
import sqlite3

TEST_DB = "Data/REP-1.db"

def test():
    # Тест 1: Попытка входа с существующими данными
    print("=== Тест 1: Попытка входа ===")
    data = {'action': 'login', 'login': 'bobibe', 'password': 'secret123'}
    system = SystemData(data, TEST_DB)
    
    print("Данные пользователя перед входом:")
    print(system.User.Info())
    
    # Выполняем вход
    login_result = system.Login_user()
    print("\nРезультат входа:")
    print(f"Статус: {login_result['status']}")
    print(f"Сообщение: {login_result['message']}")
    
    if login_result['status'] == 'success':
        print("\nДанные пользователя после успешного входа:")
        print(login_result['user'])
    else:
        print("\nВход не удался. Возможные причины:")
        print("1. Пользователь не существует")
        print("2. Неверный пароль")
        print("3. Проблема с базой данных")
    
    # Проверим напрямую, что есть в базе данных для bobibe
    print("\n=== Проверка данных bobibe напрямую из БД ===")
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, login, password, mail, phone, hashkey FROM Users WHERE login = 'bobibe'")
        row = cursor.fetchone()
        
        if row:
            print(f"ID: {row[0]}")
            print(f"Role: {row[1]}")
            print(f"Login: {row[2]}")
            print(f"Password: {row[3][:20]}...")
            print(f"Mail: {row[4]}")
            print(f"Phone: {row[5]}")
            print(f"Hashkey: {row[6]}")
            print(f"Hashkey type: {type(row[6])}")
            print(f"Hashkey is None: {row[6] is None}")
        else:
            print("Пользователь bobibe не найден в БД")
        
        conn.close()
    except Exception as e:
        print(f"Ошибка при проверке БД: {e}")

def test_registration():
    # Тест 2: Регистрация нового пользователя
    print("\n=== Тест 2: Регистрация нового пользователя ===")
    
    import time
    timestamp = int(time.time())
    new_login = f"new_user_{timestamp}"
    
    new_user_data = {
        'action': 'register',
        'login': new_login,
        'password': '123456',
        'password_repeat': '123456',
        'mail': f'{new_login}@example.com',
        'phone': f'+7{timestamp % 10000000000:010d}'
    }
    
    new_system = SystemData(new_user_data, TEST_DB)
    register_result = new_system.Register_user()
    
    print(f"Статус регистрации: {register_result['status']}")
    print(f"Сообщение: {register_result['message']}")
    
    if register_result['status'] == 'success':
        print("\nЗарегистрированный пользователь:")
        for key, value in register_result['user'].items():
            print(f"  {key}: {value}")
        
        # Проверим, сохранился ли hashkey в БД
        print(f"\nПроверка hashkey в базе данных для {new_login}:")
        try:
            conn = sqlite3.connect(TEST_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT hashkey FROM Users WHERE login = ?", (new_login,))
            hashkey_from_db = cursor.fetchone()
            if hashkey_from_db:
                print(f"Hashkey в БД: {hashkey_from_db[0]}")
                print(f"Hashkey в объекте: {register_result['user']['hashkey']}")
                print(f"Совпадают: {hashkey_from_db[0] == register_result['user']['hashkey']}")
            conn.close()
        except Exception as e:
            print(f"Ошибка при проверке: {e}")
        
        # Тест 3: Вход новым пользователем
        print("\n=== Тест 3: Вход новым пользователем ===")
        login_data = {'action': 'login', 'login': new_login, 'password': '123456'}
        login_system = SystemData(login_data, TEST_DB)
        new_login_result = login_system.Login_user()
        
        print(f"Статус входа: {new_login_result['status']}")
        print(f"Сообщение: {new_login_result['message']}")
        
        if new_login_result['status'] == 'success':
            print("\nДанные пользователя после входа:")
            for key, value in new_login_result['user'].items():
                print(f"  {key}: {value}")
    else:
        print("\nРегистрация не удалась.")

def fix_user_hashkey():
    """Исправить hashkey для пользователя bobibe, если он пустой в БД"""
    print("\n=== Исправление hashkey для bobibe ===")
    
    import hashlib
    import os
    
    try:
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.cursor()
        
        # Проверим текущий hashkey
        cursor.execute("SELECT hashkey FROM Users WHERE login = 'bobibe'")
        current_hashkey = cursor.fetchone()[0]
        
        if not current_hashkey or current_hashkey == 'None':
            print("Hashkey пустой, генерируем новый...")
            random_bytes = os.urandom(16)
            new_hashkey = hashlib.sha256(random_bytes).hexdigest()
            
            cursor.execute("UPDATE Users SET hashkey = ? WHERE login = 'bobibe'", (new_hashkey,))
            conn.commit()
            print(f"Новый hashkey для bobibe: {new_hashkey}")
        else:
            print(f"Hashkey уже существует: {current_hashkey}")
        
        conn.close()
    except Exception as e:
        print(f"Ошибка при исправлении hashkey: {e}")

if __name__ == "__main__":
    test()
    
    # Исправить hashkey, если нужно
    fix_user_hashkey()
    
    # Запустить тест снова после исправления
    print("\n" + "="*60)
    print("Повторный тест после исправления hashkey:")
    test()
    
    # Тест регистрации
    print("\n" + "="*60)
    test_registration()