#register_window.py
import tkinter as tk
from tkinter import messagebox, ttk
from auth import auth
from datetime import datetime
import re

class RegisterWindow:
    def __init__(self, parent_window=None):
        """Открывает окно регистрации"""
        self.window = tk.Toplevel(parent_window) if parent_window else tk.Tk()
        self.window.title("Регистрация нового пользователя")
        self.window.geometry("500x600")
        self.window.configure(bg='#E6F3FF')
        self.window.resizable(False, False)
        
        canvas = tk.Canvas(self.window, bg='#E6F3FF')
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        #Заголовок
        tk.Label(
            scrollable_frame, 
            text="Регистрация в системе каршеринга", 
            font=("Arial", 14, "bold"),
            background='#E6F3FF'
        ).grid(row=0, column=0, columnspan=2, pady=20, padx=10)
        
        #Словарь для полей ввода
        self.entries = {}
        row = 1
        
        #Обязательные поля 
        required_fields = [
            ("Фамилия*:", "last_name", False, 20),
            ("Имя*:", "first_name", False, 15),
            ("Отчество*:", "patronymic", False, 20),
            ("Серия паспорта* (4 цифры):", "passport_series", False, 4),
            ("Номер паспорта* (6 цифр):", "passport_number", False, 6),
            ("Серия ВУ* (4 цифры):", "license_series", False, 4),
            ("Номер ВУ* (6 цифр):", "license_number", False, 6),
            ("Дата выдачи ВУ* (ДД.ММ.ГГГГ):", "license_date", False, 10),
            ("Логин*:", "username", False, 50),
            ("Пароль* (мин. 6 символов):", "password", True, None),
            ("Подтверждение пароля*:", "password_confirm", True, None),
        ]
        
        #Создание полей ввода
        for label_text, field_name, is_password, max_length in required_fields:
            tk.Label(
                scrollable_frame, 
                text=label_text, 
                font=("Arial", 10),
                background='#E6F3FF'
            ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            
            if is_password:
                entry = tk.Entry(scrollable_frame, font=("Arial", 10), show="●")
            else:
                entry = tk.Entry(scrollable_frame, font=("Arial", 10))
                if max_length:
                    entry.config(width=max_length)
            
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            self.entries[field_name] = entry
            row += 1
        
        #Категории 
        tk.Label(
            scrollable_frame, 
            text="Категории ТС* (например, B):", 
            font=("Arial", 10),
            background='#E6F3FF'
        ).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            scrollable_frame, 
            textvariable=category_var,
            values=['B', 'A,B', 'B,C', 'B,C,D', 'C,D', 'D,E', 'Все категории'],
            width=28,
            state='readonly'
        )
        category_combo.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        category_combo.set('B')  # Значение по умолчанию
        self.entries['categories'] = category_combo
        row += 1
        
        
        tk.Label(
            scrollable_frame, 
            font=("Arial", 9),
            background='#E6F3FF',
            fg='#666666',
            justify=tk.LEFT
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        row += 1
        
        #Фрейм для кнопок
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(
            button_frame, 
            text="Зарегистрироваться", 
            command=self.register,
            font=("Arial", 11, "bold"),
            bg="#0077CC",
            fg="white",
            width=20
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame, 
            text="Отмена", 
            command=self.window.destroy,
            font=("Arial", 11),
            bg="#999999",
            fg="white",
            width=15
        ).pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        #Центрирование окна
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        if not parent_window:
            self.window.mainloop()
    
    def register(self):
        """Обработка регистрации"""
        #Сбор данных
        data = {}
        errors = []
        
        #Проверка обязательных полей
        for field_name, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                value = widget.get().strip()
            else:
                value = widget.get().strip()
            
            if field_name in ['last_name', 'first_name', 'patronymic', 
                            'passport_series', 'passport_number', 
                            'license_series', 'license_number', 'license_date',
                            'categories', 'username', 'password', 'password_confirm']:
                if not value:
                    errors.append(f"Поле '{field_name}' обязательно для заполнения")
            
            data[field_name] = value
        
        #Проверка паролей
        if data['password'] != data['password_confirm']:
            errors.append("Пароли не совпадают")
        
        if len(data['password']) < 6:
            errors.append("Пароль должен быть не менее 6 символов")
        
        #Проверка формата даты
        try:
            date_obj = datetime.strptime(data['license_date'], '%d.%m.%Y')
            data['license_date'] = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            errors.append("Дата должна быть в формате ДД.ММ.ГГГГ")
        
        #Проверка форматов
        if len(data['passport_series']) != 4 or not data['passport_series'].isdigit():
            errors.append("Серия паспорта должна быть 4 цифры")
        
        if len(data['passport_number']) != 6 or not data['passport_number'].isdigit():
            errors.append("Номер паспорта должен быть 6 цифр")
        
        if len(data['license_series']) != 4 or not data['license_series'].isdigit():
            errors.append("Серия ВУ должна быть 4 цифры")
        
        if len(data['license_number']) != 6 or not data['license_number'].isdigit():
            errors.append("Номер ВУ должен быть 6 цифр")
        
        #Проверка категорий ТС 
        categories = data['categories'].replace(' ', '').upper()  
        
        #Проверяем формат: только буквы A,B,C,D,E, разделенные запятыми
        category_pattern = r'^[ABCDE](,[ABCDE])*$'
        if not re.match(category_pattern, categories):
            errors.append("Некорректный формат категорий ТС. Допустимо: B или A,B (только латинские A,B,C,D,E)")
        
        data['categories'] = categories # Используем очищенный вариант
        
        if errors:
            messagebox.showerror("Ошибки в форме", "\n".join(errors))
            return
        
        #Подготовка данных для БД
        user_data = {
            'last_name': data['last_name'],
            'first_name': data['first_name'],
            'patronymic': data['patronymic'],
            'passport_series': data['passport_series'],
            'passport_number': data['passport_number'],
            'license_series': data['license_series'],
            'license_number': data['license_number'],
            'license_date': data['license_date'],
            'categories': data['categories']
        }
        
        #Регистрация
        success, message = auth.register(
            data['username'],
            data['password'],
            user_data
        )
        
        if success:
            messagebox.showinfo("Успех", message)
            self.window.destroy()
        else:
            messagebox.showerror("Ошибка регистрации", message)