#user_interface.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import db
import re

class UserInterface:
    def __init__(self, user_data):
        self.user_data = user_data
        self.user_id = user_data['user_id']
        
        self.root = tk.Tk()
        self.root.title(f"Каршеринг - {user_data['full_name']}")
        self.root.geometry("900x600")
        self.root.configure(bg='#E6F3FF')
        
        self.create_widgets()
        self.load_available_cars()
        self.load_my_trips()
        self.load_my_fines()
        self.load_user_profile()  
        self.root.mainloop()
    
    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg='#003366', height=50)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        top_frame.pack_propagate(False)
        
        tk.Label(
            top_frame,
            text=f"Пользователь: {self.user_data['full_name']}",
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
        
        # Основной контейнер с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#E6F3FF')
        style.configure('TNotebook.Tab', background='#CCE5FF', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#0077CC')], 
                 foreground=[('selected', 'white')])
        
        # Вкладка 1: Доступные автомобили
        self.cars_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.cars_frame, text="🚗 Доступные автомобили")
        self.setup_cars_tab()
        
        # Вкладка 2: Мои поездки
        self.trips_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.trips_frame, text="📋 Мои поездки")
        self.setup_trips_tab()
        
        # Вкладка 3: Мои штрафы
        self.fines_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.fines_frame, text="⚠ Мои штрафы")
        self.setup_fines_tab()
        
        # Вкладка 4: Мой профиль (НОВАЯ ВКЛАДКА)
        self.profile_frame = tk.Frame(self.notebook, bg='#E6F3FF')
        self.notebook.add(self.profile_frame, text="👤 Мой профиль")
        self.setup_profile_tab()
    
    def setup_cars_tab(self):
        # Заголовок
        tk.Label(
            self.cars_frame,
            text="Доступные для бронирования автомобили:",
            font=("Arial", 12, "bold"),
            bg='#E6F3FF'
        ).pack(pady=10)
        
        # Таблица автомобилей
        columns = ("Номер", "Марка", "Модель", "СТС", "ОСАГО")
        self.cars_tree = ttk.Treeview(self.cars_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.cars_frame, orient=tk.VERTICAL, command=self.cars_tree.yview)
        self.cars_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cars_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Кнопка бронирования
        tk.Button(
            self.cars_frame,
            text="Забронировать выбранный автомобиль",
            command=self.book_car,
            font=("Arial", 11, "bold"),
            bg="#0077CC",
            fg="white",
            padx=20,
            pady=8
        ).pack(pady=10)
    
    def setup_trips_tab(self):
        # Таблица поездок
        columns = ("ID", "Автомобиль", "Время в пути", "Стоимость")
        self.trips_tree = ttk.Treeview(self.trips_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.trips_tree.heading(col, text=col)
            self.trips_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.trips_frame, orient=tk.VERTICAL, command=self.trips_tree.yview)
        self.trips_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trips_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка обновления
        tk.Button(
            self.trips_frame,
            text="Обновить список",
            command=self.load_my_trips,
            font=("Arial", 10),
            bg="#0055AA",
            fg="white"
        ).pack(pady=10)
    
    def setup_fines_tab(self):
        # Таблица штрафов
        columns = ("ID", "Поездка", "Сумма", "Причина")
        self.fines_tree = ttk.Treeview(self.fines_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.fines_tree.heading(col, text=col)
            self.fines_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.fines_frame, orient=tk.VERTICAL, command=self.fines_tree.yview)
        self.fines_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fines_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка обновления
        tk.Button(
            self.fines_frame,
            text="Обновить список",
            command=self.load_my_fines,
            font=("Arial", 10),
            bg="#0055AA",
            fg="white"
        ).pack(pady=10)
    
    def setup_profile_tab(self):
        """Создание вкладки с профилем пользователя"""
        # Основной фрейм с прокруткой
        main_frame = tk.Frame(self.profile_frame, bg='#E6F3FF')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        tk.Label(
            main_frame,
            text="Мой профиль",
            font=("Arial", 16, "bold"),
            bg='#E6F3FF',
            fg='#003366'
        ).pack(pady=(0, 20))
        
        # Фрейм для информации
        info_frame = tk.LabelFrame(
            main_frame,
            text="Личная информация",
            font=("Arial", 12, "bold"),
            bg='#E6F3FF',
            fg='#003366',
            padx=20,
            pady=20
        )
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Текст с информацией (будет заполнен при загрузке)
        self.profile_text = tk.Text(
            info_frame,
            font=("Arial", 11),
            bg='#F0F8FF',
            fg='#003366',
            wrap=tk.WORD,
            height=20,
            width=60,
            relief=tk.FLAT,
            state=tk.DISABLED  # Только для чтения
        )
        self.profile_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Информация о системе
        tk.Label(
            main_frame,
            text="Для изменения данных обратитесь к администратору",
            font=("Arial", 9),
            bg='#E6F3FF',
            fg='#666666'
        ).pack(pady=5)
    
    def load_user_profile(self):
        """Загрузка и отображение данных профиля пользователя"""
        query = """
            SELECT 
                Фамилия, Имя, Отчество,
                Серия_паспорта, Номер_паспорта,
                Серия_ВУ, Номер_ВУ,
                Дата_выдачи_ВУ,
                Категории_ТС
            FROM "Пользователи"
            WHERE id_пользователя = %s
        """
        
        user_info = db.fetch_one(query, (self.user_id,))
        
        if user_info:
            # Форматируем дату
            license_date = user_info[7]
            if license_date:
                license_date_str = license_date.strftime('%d.%m.%Y')
            else:
                license_date_str = "не указана"
            
            # Форматируем текст профиля
            profile_content = f"""

👤 ФИО:
  Фамилия: {user_info[0]}
  Имя: {user_info[1]}
  Отчество: {user_info[2] or 'не указано'}

📋 ПАСПОРТНЫЕ ДАННЫЕ:
  Серия паспорта: {user_info[3]}
  Номер паспорта: {user_info[4]}
  Полный номер: {user_info[3]} {user_info[4]}

🚗 ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ:
  Серия ВУ: {user_info[5]}
  Номер ВУ: {user_info[6]}
  Дата выдачи: {license_date_str}
  Категории ТС: {user_info[8]}
"""
            
            # Обновляем текст в виджете
            self.profile_text.config(state=tk.NORMAL)
            self.profile_text.delete(1.0, tk.END)
            self.profile_text.insert(1.0, profile_content.strip())
            self.profile_text.config(state=tk.DISABLED)
            
            # Также обновим заголовок окна с актуальным ФИО
            current_name = f"{user_info[0]} {user_info[1]}"
            if user_info[2]:
                current_name += f" {user_info[2]}"
            self.user_data['full_name'] = current_name
            
            # Обновим заголовок в верхней панели (если нужно)
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame) and widget.cget('bg') == '#003366':
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(text=f"Пользователь: {current_name}")
                            break
                    break
        else:
            # Если данные не найдены
            error_text = "Не удалось загрузить данные профиля.\nОбратитесь к администратору."
            self.profile_text.config(state=tk.NORMAL)
            self.profile_text.delete(1.0, tk.END)
            self.profile_text.insert(1.0, error_text)
            self.profile_text.config(state=tk.DISABLED)
    
    def load_available_cars(self):
        """Загрузка доступных автомобилей"""
        for item in self.cars_tree.get_children():
            self.cars_tree.delete(item)
        
        # Автомобили, которые не в активных поездках
        query = """
            SELECT 
                a."Номер_автомобиля",
                a."Марка",
                a."Модель",
                CONCAT(a."Серия_СТС", ' ', a."Номер_СТС"),
                CONCAT(a."Серия_полиса_ОСАГО", ' ', a."Номер_полиса_ОСАГО")
            FROM "Автомобили" a
            WHERE a."Номер_автомобиля" NOT IN (
                SELECT p."Номер_автомобиля" 
                FROM "Поездки" p
                WHERE p."Время_в_пути" IS NOT NULL
            )
            ORDER BY a."Марка", a."Модель"
        """
        
        cars = db.fetch_all(query)
        for car in cars:
            self.cars_tree.insert("", tk.END, values=car)
    
    def load_my_trips(self):
        """Загрузка поездок пользователя"""
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)
        
        query = """
            SELECT 
                p.id_поездки,
                CONCAT(a."Марка", ' ', a."Модель", ' (', a."Номер_автомобиля", ')'),
                p."Время_в_пути",
                p."Стоимость"
            FROM "Поездки" p
            JOIN "Автомобили" a ON p."Номер_автомобиля" = a."Номер_автомобиля"
            WHERE p.id_пользователя = %s
            ORDER BY p.id_поездки DESC
        """
        
        trips = db.fetch_all(query, (self.user_id,))
        for trip in trips:
            self.trips_tree.insert("", tk.END, values=trip)
    
    def load_my_fines(self):
        """Загрузка штрафов пользователя"""
        for item in self.fines_tree.get_children():
            self.fines_tree.delete(item)
        
        query = """
            SELECT 
                sh.id_штрафа,
                sh.id_поездки,
                sh."Сумма",
                sh."Пункт_ПДД"
            FROM "Штрафы" sh
            JOIN "Поездки" p ON sh.id_поездки = p.id_поездки
            WHERE p.id_пользователя = %s
            ORDER BY sh.id_штрафа DESC
        """
        
        fines = db.fetch_all(query, (self.user_id,))
        for fine in fines:
            self.fines_tree.insert("", tk.END, values=fine)
    
    def book_car(self):
        """Бронирование автомобиля"""
        selection = self.cars_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите автомобиль для бронирования")
            return
        
        car_data = self.cars_tree.item(selection[0])['values']
        car_number = car_data[0]
        
        # Окно для ввода времени поездки
        booking_window = tk.Toplevel(self.root)
        booking_window.title("Бронирование автомобиля")
        booking_window.geometry("300x250")
        booking_window.configure(bg='#E6F3FF')
        booking_window.grab_set()
        
        tk.Label(
            booking_window,
            text=f"Бронирование: {car_data[1]} {car_data[2]}",
            font=("Arial", 12, "bold"),
            bg='#E6F3FF'
        ).pack(pady=10)
        
        # Ввод времени поездки
        tk.Label(booking_window, text="Время поездки (часы):", bg='#E6F3FF').pack(pady=5)
        
        hours_var = tk.StringVar(value="1")
        hours_spinbox = tk.Spinbox(booking_window, from_=1, to=24, 
                                  textvariable=hours_var, width=10)
        hours_spinbox.pack(pady=5)
        
        # Расчет стоимости (5 руб/минута = 300 руб/час)
        def calculate_cost():
            try:
                hours = int(hours_var.get())
                cost = hours * 300  # 300 руб/час
                cost_label.config(text=f"Примерная стоимость: {cost} руб.")
            except:
                cost_label.config(text="Ошибка расчета")
        
        tk.Button(booking_window, text="Рассчитать стоимость", 
                 command=calculate_cost, bg='#0077CC', fg='white').pack(pady=10)
        
        cost_label = tk.Label(booking_window, text="", font=("Arial", 11), 
                             bg='#E6F3FF', fg='#003366')
        cost_label.pack(pady=5)
        
        def confirm_booking():
            try:
                hours = int(hours_var.get())
                
                # Форматируем время как HH:MM:SS
                time_str = f"{hours:02d}:00:00"
                
                # Создаем поездку
                query = """
                    INSERT INTO "Поездки" 
                    (id_пользователя, "Номер_автомобиля", "Время_в_пути", "Стоимость")
                    VALUES (%s, %s, %s, %s)
                """
                
                cost = hours * 300
                
                if db.execute_query(query, (self.user_id, car_number, time_str, cost)):
                    messagebox.showinfo("Успех", f"Автомобиль {car_number} забронирован!\nСтоимость: {cost} руб.")
                    booking_window.destroy()
                    self.load_available_cars()
                    self.load_my_trips()
                else:
                    messagebox.showerror("Ошибка", "Не удалось забронировать автомобиль")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка бронирования: {e}")
        
        # Кнопки
        btn_frame = tk.Frame(booking_window, bg='#E6F3FF')
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Подтвердить",
            command=confirm_booking,
            bg='#0077CC',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            command=booking_window.destroy,
            bg='#999999',
            fg='white',
            width=12
        ).pack(side=tk.LEFT, padx=10)