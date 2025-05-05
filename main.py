from typing import Union, List
from fastapi import FastAPI, HTTPException, Header, Request
import time
import json
import os
import hashlib 
import secrets 
from models import (
    User, Polybius_Encrypt_Request, Polybius_Decrypt_Request,
    Change_Text_Request, Delete_Request, One_Text_Request,
    Change_Password_Request, Text_Request, Token
)
from crypto import Polybius

app = FastAPI()

def token_search(token: str): #поиск пользователя по токену
    file_path = 'users'
    user_id = None
    user_login = None
    for json_file in os.listdir(file_path):
        if json_file.endswith('.json'):
            file1_path = os.path.join(file_path, json_file)
            with open(file1_path, 'r', encoding="utf-8") as f:
                tmp_user = json.load(f)
            if tmp_user['token'] == token:
                user_id = tmp_user['id']
                user_login = tmp_user['login']
                return user_id, user_login
    return None

@app.post("/register") #регистрация пользователя
def create_user(user: User):
    user.id = int(time.time())
    user.token = secrets.token_hex(8) #генерация технического токена
    folder_path = 'users'
    json_files = [file for file in os.listdir(folder_path) if file.endswith('.json')]
    for json_file in json_files: #проверна на существование пользователя
        file_path = os.path.join(folder_path, json_file)
        with open(file_path, 'r') as f:
            tmp_user = json.load(f)
            if (tmp_user['login']==user.login):
                raise HTTPException(status_code=409, detail="Пользователь существует.")
    user.password = hashlib.sha256(user.password.encode()).hexdigest()  #хеширование пароля
    with open(f"users/user_{user.id}.json", 'w') as f: #сохранение пользователя
        json.dump(user.dict(), f)
    return user

@app.post("/auth") #авторизация пользователя
def authorization(user: User):
    folder_path = 'users'
    user_found = False
    for json_file in os.listdir(folder_path): #поиск пользователя по логину
        if json_file.endswith('.json'):
            file_path = os.path.join(folder_path, json_file)
            with open(file_path, 'r') as f:
                tmp_user = json.load(f)
                if tmp_user['login'] == user.login: #проверка логина
                    user_found = True
                    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() #хеширование пароля и сравнивание его с сохранённым
                    if tmp_user['password'] == hashed_password:
                        return {"token": tmp_user['token']}
                    else:
                        raise HTTPException(status_code=409, detail="Неверный пароль.")
    if not user_found:
        raise HTTPException(status_code=409, detail="Пользователь не найден.")
    

@app.put("/change_password") #изменение пароля
def edit_password(data: Change_Password_Request):
    folder_path = 'users'
    user_found = False
    for json_file in os.listdir(folder_path):
        if json_file.endswith('.json'):
            file_path = os.path.join(folder_path, json_file)
            with open(file_path, 'r') as f:
                tmp_user = json.load(f)
            if tmp_user['token'] == data.token:
                user_found = True
                if tmp_user['password'] != hashlib.sha256(data.old_password.encode()).hexdigest():
                    raise HTTPException(status_code=401, detail="Неверный старый пароль.")
                tmp_user['password'] = hashlib.sha256(data.new_password.encode()).hexdigest()
                new_token = secrets.token_hex(8)
                tmp_user['token'] = new_token
                with open(file_path, 'w') as fw:
                    json.dump(tmp_user, fw)
                return {"message": "Пароль успешно изменён.", "token": new_token}
    if not user_found:
        raise HTTPException(status_code=409, detail="Пользователь не найден.")
    
@app.post("/add_text")  #добавление текста
def add_text2(text: Text_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        #создаем директорию для текстов пользователя
        folder_path = os.path.join(os.getcwd(), 'texts')
        user_folder = os.path.join(folder_path, str(user_id))
        os.makedirs(user_folder, exist_ok=True)
        
        #генерируем уникальное имя файла
        current_time = int(time.time())
        file_name = f"text_{current_time}.txt"
        file_path = os.path.join(user_folder, file_name)
        
        #записываем текст в файл
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text.text)
            
        return {"message": "Текст успешно добавлен!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении текста: {str(e)}")

@app.patch("/change_text") #изменение текста
def change_the_text(text: Change_Text_Request):
    user_id = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_folder = os.path.join('texts', str(user_id))  #получение списка файлов пользователя
    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        raise HTTPException(status_code=404, detail="Нет доступных текстов для изменения")
    files = os.listdir(user_folder)
    if text.text_number < 1 or text.text_number > len(files):
        raise HTTPException(status_code=404, detail="Текст с указанным номером не найден")
    if not text.new_text.strip():
        raise HTTPException(status_code=400, detail="Новый текст не может быть пустым")
    file_to_update = os.path.join(user_folder, files[text.text_number - 1])
    with open(file_to_update, 'w', encoding="utf-8") as f: #обновление текста в файле
        f.write(text.new_text)
    return {"message": "Текст успешно обновлён!"}

@app.delete("/delete_text")  #удаление текста
def delete_text(text: Delete_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_folder = os.path.join('texts', str(user_id))  
    if not os.path.exists(user_folder):
        raise HTTPException(status_code=404, detail="Папка с текстами не найдена")
    files = os.listdir(user_folder)
    if text.text_number < 0 or text.text_number >= len(files):
        raise HTTPException(status_code=404, detail="Текст с указанным номером не найден")
    file_to_delete = os.path.join(user_folder, files[text.text_number])
    os.remove(file_to_delete)
    return {"message": "Текст успешно удалён"}

@app.get("/view_all_texts")  #просмотр всех текстов пользователя
def view_all_texts(token: Token):
    user_id, user_login = token_search(token.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        #путь к директории с текстами пользователя
        user_folder = os.path.join(os.getcwd(), 'texts', str(user_id))
        
        #проверка существования директории
        if not os.path.exists(user_folder):
            return {"texts": []}
            
        #получение списка всех текстовых файлов
        all_texts = []
        for file_name in sorted(os.listdir(user_folder)):
            if file_name.endswith('.txt'):
                file_path = os.path.join(user_folder, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        all_texts.append({"content": content})
                except Exception as e:
                    print(f"Ошибка при чтении файла {file_name}: {str(e)}")
                    continue
                    
        return {"texts": all_texts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка текстов: {str(e)}")

@app.get("/view_one_text")  #просмотр одного текста пользователя
def view_one_text(text: One_Text_Request):
    user_id, user_login = token_search(text.token)
    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user_folder = os.path.join(text.type, str(user_id))
    text_files = os.listdir(user_folder)  #получение списка файлов
    if text.text_number < 0 or text.text_number > len(text_files):
        raise HTTPException(status_code=400, detail=f"Выберите номер от 1 до {len(text_files)}")
    selected_file = text_files[text.text_number - 1]  #индексация с 0
    file_path = os.path.join(user_folder, selected_file)
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
    return {"text": content}

@app.post("/encrypt")
def encrypt_polybius(data: Polybius_Encrypt_Request):
    if token_search(data.token) is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    try:
        #Удаляем пробелы из текста для шифрования
        text_to_encrypt = data.text.replace(" ", "")
        if not text_to_encrypt:
            raise HTTPException(status_code=400, detail="Текст для шифрования не может быть пустым")
            
        #Создаем объект Polybius с текстом для определения алфавита
        poly = Polybius(text_to_encrypt)
        encrypted = poly.encrypt(text_to_encrypt)
        return {"encrypted": encrypted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при шифровании: {str(e)}")


@app.post("/decrypt")
def decrypt_polybius(data: Polybius_Decrypt_Request):
    if token_search(data.token) is None:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    try:
        if data.language == 1:  #русский
            poly = Polybius("А")
        elif data.language == 2:  #английский
            poly = Polybius("A")
        else:
            raise HTTPException(status_code=400, detail="Необходимо указать язык (1 - русский, 2 - английский)")
            
        # Удаляем пробелы из текста для дешифрования
        text_to_decrypt = data.text.replace(" ", "")
        if not text_to_decrypt:
            raise HTTPException(status_code=400, detail="Текст для дешифрования не может быть пустым")
            
        # Проверяем, что текст содержит только цифры
        if not all(c.isdigit() for c in text_to_decrypt):
            raise HTTPException(status_code=400, detail="Текст для дешифрования должен содержать только цифры")
            
        decrypted = poly.decrypt(text_to_decrypt)
        return {"decrypted": decrypted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при дешифровании: {str(e)}")

