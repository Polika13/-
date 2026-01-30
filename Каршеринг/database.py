#database.py
import psycopg2
import hashlib

class Database:
    def __init__(self):
        """
        Подключение к БД PostgreSQL
        """
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                database="carsharing",      
                user="postgres",           
                password="123",     
                port=5432
            )
            self.cursor = self.conn.cursor()
            print("✅ Подключение к БД установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def execute_query(self, query: str, params=None) -> bool:
        """
        Выполнение SQL-запроса (INSERT, UPDATE, DELETE)
        Возвращает True при успехе, False при ошибке
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            print(f"   Запрос: {query}")
            print(f"   Параметры: {params}")
            self.conn.rollback()
            return False
    
    def fetch_all(self, query: str, params=None):
        """
        Выполнение SELECT запроса с возвратом всех строк
        Возвращает список кортежей или пустой список
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка выборки данных: {e}")
            return []
    
    def fetch_one(self, query: str, params=None):
        """
        Выполнение SELECT запроса с возвратом одной строки
        Возвращает кортеж или None
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"❌ Ошибка выборки одной строки: {e}")
            return None
    
    def close(self):
        """Закрытие соединения с БД"""
        self.cursor.close()
        self.conn.close()
        print("🔌 Соединение с БД закрыто")

db = Database()