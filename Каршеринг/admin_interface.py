#admin_interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import db

class AdminInterface:
    def __init__(self, user_data):
        self.user_data = user_data
        self.root = tk.Tk()
        self.root.title(f"Каршеринг - Администратор")
        self.root.geometry("1000x700")
        self.root.configure(bg='#E6F3FF')
        
        self.create_widgets()
        self.load_data()
        self.root.mainloop()
    
    def create_widgets(self):
        #Верхняя панель
        top_frame = tk.Frame(self.root, bg='#003366', height=50)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        top_frame.pack_propagate(False)
        
        tk.Label(
            top_frame,
            text=f"Администратор: {self.user_data['username']}",
            font=("Arial", 14, "bold"),
            bg='#003366',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Button(
            top_frame,
            text="Выйти",
            command=self.root.destroy,
            font=("Arial", 10),
            bg='#FF4444',
            fg='white'
        ).pack(side=tk.RIGHT, padx=20, pady=10)
        
        #Основной контейнер с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#E6F3FF')
        style.configure('TNotebook.Tab', background='#CCE5FF', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#0077CC')], 
                 foreground=[('selected', 'white')])
        
        #Вкладка 1: Автомобили
        self.cars_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.cars_frame, text="🚗 Автомобили")
        self.setup_cars_tab()
        
        #Вкладка 2: Пользователи
        self.users_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.users_frame, text="👥 Пользователи")
        self.setup_users_tab()
        
        #Вкладка 3: Поездки
        self.trips_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.trips_frame, text="📋 Поездки")
        self.setup_trips_tab()
        
        #Вкладка 4: Штрафы
        self.fines_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.fines_frame, text="⚠ Штрафы")
        self.setup_fines_tab()
    
    def setup_cars_tab(self):
        #Панель управления
        control_frame = tk.Frame(self.cars_frame, bg='#E6F3FF')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            control_frame,
            text="Добавить автомобиль",
            command=self.add_car,
            font=("Arial", 10),
            bg="#0077CC",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Обновить",
            command=lambda: self.load_cars(),
            font=("Arial", 10),
            bg="#0055AA",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        #Таблица автомобилей
        columns = ("Номер", "Марка", "Модель", "СТС", "ОСАГО")
        self.cars_tree = ttk.Treeview(self.cars_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.cars_frame, orient=tk.VERTICAL, command=self.cars_tree.yview)
        self.cars_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cars_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def setup_users_tab(self):
        #Таблица пользователей
        columns = ("ID", "Фамилия", "Имя", "Отчество", "Паспорт", "ВУ")
        self.users_tree = ttk.Treeview(self.users_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.users_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_trips_tab(self):
        #Таблица поездок
        columns = ("ID", "Пользователь", "Автомобиль", "Время", "Стоимость")
        self.trips_tree = ttk.Treeview(self.trips_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.trips_tree.heading(col, text=col)
            self.trips_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.trips_frame, orient=tk.VERTICAL, command=self.trips_tree.yview)
        self.trips_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trips_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_fines_tab(self):
        #Панель управления штрафами
        control_frame = tk.Frame(self.fines_frame, bg='#E6F3FF')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            control_frame,
            text="Добавить штраф",
            command=self.add_fine,
            font=("Arial", 10),
            bg="#0077CC",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Обновить",
            command=lambda: self.load_fines(),
            font=("Arial", 10),
            bg="#0055AA",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        #Таблица штрафов
        columns = ("ID", "Поездка", "Сумма", "Причина")
        self.fines_tree = ttk.Treeview(self.fines_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.fines_tree.heading(col, text=col)
            self.fines_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.fines_frame, orient=tk.VERTICAL, command=self.fines_tree.yview)
        self.fines_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fines_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def load_data(self):
        self.load_cars()
        self.load_users()
        self.load_trips()
        self.load_fines()
    
    def load_cars(self):
        for item in self.cars_tree.get_children():
            self.cars_tree.delete(item)
        
        query = """
            SELECT 
                "Номер_автомобиля",
                "Марка",
                "Модель",
                CONCAT("Серия_СТС", ' ', "Номер_СТС"),
                CONCAT("Серия_полиса_ОСАГО", ' ', "Номер_полиса_ОСАГО")
            FROM "Автомобили"
            ORDER BY "Марка", "Модель"
        """
        
        cars = db.fetch_all(query)
        for car in cars:
            self.cars_tree.insert("", tk.END, values=car)
    
    def load_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        query = """
            SELECT 
                id_пользователя,
                Фамилия,
                Имя,
                Отчество,
                CONCAT(Серия_паспорта, ' ', Номер_паспорта),
                CONCAT(Серия_ВУ, ' ', Номер_ВУ)
            FROM "Пользователи"
            ORDER BY Фамилия, Имя
        """
        
        users = db.fetch_all(query)
        for user in users:
            self.users_tree.insert("", tk.END, values=user)
    
    def load_trips(self):
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)
        
        query = """
            SELECT 
                p.id_поездки,
                CONCAT(u.Фамилия, ' ', u.Имя),
                a."Номер_автомобиля",
                p."Время_в_пути",
                p."Стоимость"
            FROM "Поездки" p
            JOIN "Пользователи" u ON p.id_пользователя = u.id_пользователя
            JOIN "Автомобили" a ON p."Номер_автомобиля" = a."Номер_автомобиля"
            ORDER BY p.id_поездки DESC
        """
        
        trips = db.fetch_all(query)
        for trip in trips:
            self.trips_tree.insert("", tk.END, values=trip)
    
    def load_fines(self):
        for item in self.fines_tree.get_children():
            self.fines_tree.delete(item)
        
        query = """
            SELECT 
                sh.id_штрафа,
                sh.id_поездки,
                sh."Сумма",
                sh."Пункт_ПДД"
            FROM "Штрафы" sh
            ORDER BY sh.id_штрафа DESC
        """
        
        fines = db.fetch_all(query)
        for fine in fines:
            self.fines_tree.insert("", tk.END, values=fine)
    
    def add_car(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавление автомобиля")
        add_window.geometry("500x500")
        add_window.configure(bg='#E6F3FF')
        add_window.grab_set()
        
        tk.Label(
            add_window,
            text="Добавление нового автомобиля",
            font=("Arial", 14, "bold"),
            bg='#E6F3FF'
        ).pack(pady=10)
        ""
        
        tk.Label(
            add_window,
            font=("Arial", 9),
            bg='#E6F3FF',
            fg='#003366',
            justify=tk.LEFT
        ).pack(pady=10, padx=20)
        
        #Поля ввода
        fields = [
            ("Номер автомобиля*:", "number"),
            ("Марка*:", "brand"),
            ("Модель*:", "model"),
            ("Серия СТС* (2 буквы + 2 цифры):", "sts_series"),
            ("Номер СТС* (6 цифр):", "sts_number"),
            ("Серия полиса ОСАГО*:", "osago_series"),
            ("Номер полиса ОСАГО* (10 цифр):", "osago_number"),
        ]
        
        entries = {}
        for label_text, field_name in fields:
            frame = tk.Frame(add_window, bg='#E6F3FF')
            frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(frame, text=label_text, width=30, anchor="w", bg='#E6F3FF').pack(side="left")
            entry = tk.Entry(frame, width=25)
            entry.pack(side="right")
            entries[field_name] = entry
        
        entries['osago_series'].insert(0, 'ААК')  #Одна из допустимых серий
        
        def save_car():
            data = {}
            for field_name, entry in entries.items():
                data[field_name] = entry.get().strip().upper()  
            
            errors = []
            required_fields = ['number', 'brand', 'model', 'sts_series', 
                              'sts_number', 'osago_series', 'osago_number']
            
            for field in required_fields:
                if not data[field]:
                    errors.append(f"Заполните поле '{field}'")
            
            #Проверка форматов на основе CHECK-ограничений
            import re
            
            #1. Проверка номера автомобиля
            car_number_pattern = r'^[АВЕКМНОРСТУХ][0-9]{3}[АВЕКМНОРСТУХ]{2}[0-9]{2,3}$'
            if not re.match(car_number_pattern, data['number']):
                errors.append("Неверный формат номера авто. Пример: А123ВС77")
            
            #2. Проверка серии СТС
            sts_series_pattern = r'^[АВЕКМНОРСТУХ]{2}[0-9]{2}$'
            if not re.match(sts_series_pattern, data['sts_series']):
                errors.append("Неверный формат серии СТС. Пример: АВ01")
            
            #3. Проверка номера СТС
            if len(data['sts_number']) != 6 or not data['sts_number'].isdigit():
                errors.append("Номер СТС должен быть 6 цифр")
            
            #4. Проверка серии ОСАГО
            valid_osago_series = ['ХХХ', 'ТТТ', 'ААК', 'ААМ', 'ААН']
            if data['osago_series'] not in valid_osago_series:
                errors.append(f"Серия ОСАГО должна быть одна из: {', '.join(valid_osago_series)}")
            
            #5. Проверка номера ОСАГО
            if len(data['osago_number']) != 10 or not data['osago_number'].isdigit():
                errors.append("Номер ОСАГО должен быть 10 цифр")
            
            if errors:
                messagebox.showerror("Ошибка", "\n".join(errors))
                return
            
            #Проверка существования автомобиля
            check_query = """
                SELECT 1 FROM "Автомобили" 
                WHERE "Номер_автомобиля" = %s
            """
            if db.fetch_one(check_query, (data['number'],)):
                messagebox.showerror("Ошибка", "Автомобиль с таким номером уже существует")
                return
            
            #Вставка в БД
            insert_query = """
                INSERT INTO "Автомобили" 
                ("Номер_автомобиля", "Марка", "Модель", 
                 "Серия_СТС", "Номер_СТС", 
                 "Серия_полиса_ОСАГО", "Номер_полиса_ОСАГО")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                data['number'],
                data['brand'],
                data['model'],
                data['sts_series'],
                data['sts_number'],
                data['osago_series'],
                data['osago_number']
            )
            
            if db.execute_query(insert_query, params):
                messagebox.showinfo("Успех", "Автомобиль успешно добавлен")
                add_window.destroy()
                self.load_cars()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить автомобиль")
        
        #Кнопки
        button_frame = tk.Frame(add_window, bg='#E6F3FF')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Сохранить",
            command=save_car,
            bg="#0077CC",
            fg="white",
            width=15
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Отмена",
            command=add_window.destroy,
            bg="#999999",
            fg="white",
            width=15
        ).pack(side="left", padx=10)
    
    def add_fine(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавление штрафа")
        add_window.geometry("400x300")
        add_window.configure(bg='#E6F3FF')
        add_window.grab_set()
        
        tk.Label(
            add_window,
            text="Добавление штрафа",
            font=("Arial", 14, "bold"),
            bg='#E6F3FF'
        ).pack(pady=20)
        
        #Поля ввода
        tk.Label(add_window, text="ID поездки*:", bg='#E6F3FF').pack()
        trip_id_entry = tk.Entry(add_window, width=30)
        trip_id_entry.pack(pady=5)
        
        tk.Label(add_window, text="Сумма штрафа*:", bg='#E6F3FF').pack()
        amount_entry = tk.Entry(add_window, width=30)
        amount_entry.pack(pady=5)
        
        tk.Label(add_window, text="Причина (Пункт ПДД):", bg='#E6F3FF').pack()
        reason_entry = tk.Entry(add_window, width=30)
        reason_entry.pack(pady=5)
        
        def save_fine():
            trip_id = trip_id_entry.get().strip()
            amount = amount_entry.get().strip()
            reason = reason_entry.get().strip()
            
            if not trip_id or not amount or not reason:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            
            try:
                amount_float = float(amount)
            except ValueError:
                messagebox.showerror("Ошибка", "Сумма должна быть числом")
                return
            
            #Проверка существования поездки
            check_query = """
                SELECT 1 FROM "Поездки" 
                WHERE id_поездки = %s
            """
            if not db.fetch_one(check_query, (trip_id,)):
                messagebox.showerror("Ошибка", "Поездка с таким ID не существует")
                return
            
            #Вставка штрафа
            insert_query = """
                INSERT INTO "Штрафы" 
                (id_поездки, "Сумма", "Пункт_ПДД")
                VALUES (%s, %s, %s)
            """
            
            if db.execute_query(insert_query, (trip_id, amount_float, reason)):
                messagebox.showinfo("Успех", "Штраф успешно добавлен")
                add_window.destroy()
                self.load_fines()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить штраф")
        
        #Кнопки
        button_frame = tk.Frame(add_window, bg='#E6F3FF')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Сохранить",
            command=save_fine,
            bg="#0077CC",
            fg="white",
            width=15
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="Отмена",
            command=add_window.destroy,
            bg="#999999",
            fg="white",
            width=15
        ).pack(side="left", padx=10)