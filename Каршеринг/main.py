#main.py
import tkinter as tk
from tkinter import messagebox

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Каршеринг - Авторизация")
        self.root.geometry("400x350")
        self.root.configure(bg='#E6F3FF')  
        self.root.resizable(False, False)
        
        #Заголовок
        tk.Label(
            root, 
            text="Система каршеринга", 
            font=("Arial", 16, "bold"),
            bg='#E6F3FF',
            fg='#003366'  
        ).pack(pady=20)
        
        #Поле логина
        tk.Label(root, text="Логин:", font=("Arial", 12), bg='#E6F3FF').pack(pady=5)
        self.login_entry = tk.Entry(root, font=("Arial", 12), width=25)
        self.login_entry.pack()
        self.login_entry.focus()
        
        #Поле пароля
        tk.Label(root, text="Пароль:", font=("Arial", 12), bg='#E6F3FF').pack(pady=5)
        self.password_entry = tk.Entry(
            root, font=("Arial", 12), width=25, show="●"
        )
        self.password_entry.pack()
        
        #Кнопка входа
        login_button = tk.Button(
            root, text="Войти", 
            command=self.login,
            font=("Arial", 12, "bold"),
            bg="#0077CC",  
            fg="white",
            width=15,
            height=2
        )
        login_button.pack(pady=20)
        
        #Кнопка регистрации
        register_button = tk.Button(
            root, text="Регистрация",
            command=self.open_register_window,
            font=("Arial", 10),
            bg="#0055AA",  
            fg="white",
            width=12
        )
        register_button.pack()
        
        #Обработка нажатия Enter
        self.root.bind('<Return>', lambda event: self.login())
        
        #При закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def login(self):
        """Обработка входа"""
        from auth import auth
        
        username = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Внимание", "Заполните все поля")
            return
        
        self.root.config(cursor="wait")
        self.root.update()
        
        try:
            user = auth.login(username, password)
            
            if user:
                messagebox.showinfo(
                    "Успех", 
                    f"Добро пожаловать, {user['full_name']}!"
                )
                self.root.destroy()
                
                if user['is_admin']:
                    from admin_interface import AdminInterface
                    AdminInterface(user)
                else:
                    from user_interface import UserInterface
                    UserInterface(user)
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
                self.password_entry.delete(0, tk.END)
        finally:
            self.root.config(cursor="")
    
    def open_register_window(self):
        """Открытие окна регистрации"""
        from register_window import RegisterWindow
        RegisterWindow(self.root)
    
    def on_closing(self):
        """Обработка закрытия окна"""
        from database import db
        db.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()