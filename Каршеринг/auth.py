#auth.py
from database import db

class Auth:
    def login(self, username: str, password: str) -> dict:
        """
        Авторизация пользователя
        Возвращает словарь с данными пользователя или None
        """
        hashed_password = db.hash_password(password)
        
        #Для администратора
        admin_query = """
            SELECT 
                роль,
                id_пользователя,
                'Администратор' as "Фамилия",
                '' as "Имя"
            FROM "Учетные записи"
            WHERE логин = %s AND хеш_пароля = %s AND роль = 'администратор'
        """
        
        admin_result = db.fetch_one(admin_query, (username, hashed_password))
        
        if admin_result:
            return {
                'role': admin_result[0],
                'user_id': admin_result[1],  #Может быть NULL
                'full_name': 'Администратор системы',
                'username': username,
                'is_admin': True
            }
        
        #Для обычного пользователя
        user_query = """
            SELECT 
                uz.роль,
                uz.id_пользователя,
                p.Фамилия, 
                p.Имя
            FROM "Учетные записи" uz
            LEFT JOIN "Пользователи" p ON uz.id_пользователя = p.id_пользователя
            WHERE uz.логин = %s AND uz.хеш_пароля = %s AND uz.роль = 'пользователь'
        """
        
        user_result = db.fetch_one(user_query, (username, hashed_password))
        
        if user_result:
            full_name = f"{user_result[2] or ''} {user_result[3] or ''}".strip()
            return {
                'role': user_result[0],
                'user_id': user_result[1],
                'full_name': full_name if full_name else username,
                'username': username,
                'is_admin': False
            }
        
        return None
    
    def register(self, username: str, password: str, user_data: dict) -> tuple:
        """
        Регистрация нового пользователя
        Возвращает (успех, сообщение)
        """
        #1. Проверка существования логина
        check_query = """
            SELECT id_учетной_записи 
            FROM "Учетные записи" 
            WHERE логин = %s
        """
        if db.fetch_one(check_query, (username,)):
            return False, "Логин уже существует"
        
        #2. Валидация пароля
        if len(password) < 6:
            return False, "Пароль должен быть не менее 6 символов"
        
        #3. Добавление пользователя в таблицу Пользователи
        user_query = """
            INSERT INTO "Пользователи" 
            (Фамилия, Имя, Отчество, Серия_паспорта, Номер_паспорта, 
             Серия_ВУ, Номер_ВУ, Дата_выдачи_ВУ, Категории_ТС)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id_пользователя
        """
        
        user_params = (
            user_data['last_name'],
            user_data['first_name'],
            user_data.get('patronymic', ''),
            user_data['passport_series'],
            user_data['passport_number'],
            user_data['license_series'],
            user_data['license_number'],
            user_data['license_date'],
            user_data['categories']
        )
        
        user_result = db.fetch_one(user_query, user_params)
        if not user_result:
            return False, "Ошибка при создании пользователя"
        
        user_id = user_result[0]
        
        #4. Создание учётной записи (пользователь)
        account_query = """
            INSERT INTO "Учетные записи" 
            (логин, хеш_пароля, роль, id_пользователя)
            VALUES (%s, %s, %s, %s)
        """
        
        success = db.execute_query(
            account_query,
            (username, db.hash_password(password), 'пользователь', user_id)
        )
        
        if success:
            return True, "Регистрация успешна! Теперь вы можете войти."
        else:
            #Удаляем пользователя, если учётная запись не создалась
            cleanup_query = """
                DELETE FROM "Пользователи" 
                WHERE id_пользователя = %s
            """
            db.execute_query(cleanup_query, (user_id,))
            return False, "Ошибка при создании учётной записи"

auth = Auth()