# add_test_data.py
from database import db

def add_test_data():
    """Добавление тестовых данных"""
    
    print("Добавление тестовых данных...")
    
    # 1. Добавление администратора (если нет)
    check_admin = db.fetch_one("SELECT 1 FROM \"Учетные записи\" WHERE логин = 'admin'")
    if not check_admin:
        db.execute_query("""
            INSERT INTO "Учетные записи" (логин, хеш_пароля, роль)
            VALUES (%s, %s, %s)
        """, ('admin', db.hash_password('admin123'), 'администратор'))
        print("✓ Администратор: admin/admin123")
    
    # 2. Добавление тестового пользователя
    check_user = db.fetch_one("SELECT 1 FROM \"Пользователи\" WHERE Фамилия = 'Иванов'")
    if not check_user:
        user_query = """
            INSERT INTO "Пользователи" 
            (Фамилия, Имя, Отчество, Серия_паспорта, Номер_паспорта, 
             Серия_ВУ, Номер_ВУ, Дата_выдачи_ВУ, Категории_ТС)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id_пользователя
        """
        
        user_result = db.fetch_one(user_query, (
            'Иванов', 'Иван', 'Иванович', 
            '1234', '567890', '4321', '654321',
            '2020-05-15', 'B'
        ))
        
        if user_result:
            user_id = user_result[0]
            db.execute_query("""
                INSERT INTO "Учетные записи" (логин, хеш_пароля, роль, id_пользователя)
                VALUES (%s, %s, %s, %s)
            """, ('user', db.hash_password('user123'), 'пользователь', user_id))
            print("✓ Пользователь: user/user123")
    
    # 3. Добавление тестовых автомобилей (с правильными форматами!)
    cars = [
        # Формат: (номер, марка, модель, серия_СТС, номер_СТС, серия_ОСАГО, номер_ОСАГО)
        ('А123ВС77', 'Toyota', 'Camry', 'АВ01', '402826', 'ААК', '1234567890'),
        ('В456ОР78', 'Honda', 'Accord', 'МН25', '567890', 'ААМ', '2345678901'),
        ('С789ТУ79', 'Kia', 'Rio', 'СТ33', '789012', 'ААН', '3456789012'),
    ]
    
    for car in cars:
        check_car = db.fetch_one("SELECT 1 FROM \"Автомобили\" WHERE Номер_автомобиля = %s", (car[0],))
        if not check_car:
            success = db.execute_query("""
                INSERT INTO "Автомобили" 
                (Номер_автомобиля, Марка, Модель, Серия_СТС, Номер_СТС, 
                 Серия_полиса_ОСАГО, Номер_полиса_ОСАГО)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, car)
            
            if success:
                print(f"✓ Автомобиль: {car[0]} {car[1]} {car[2]}")
            else:
                print(f"✗ Не удалось добавить автомобиль: {car[0]}")
    
    print("\n✅ Тестовые данные добавлены!")

if __name__ == "__main__":
    add_test_data()