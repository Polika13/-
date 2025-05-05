import urllib.request
import json
import hashlib
import getpass
from models import (
    User, Polybius_Encrypt_Request, Polybius_Decrypt_Request,
    Change_Text_Request, Delete_Request, One_Text_Request,
    Change_Password_Request, Text_Request, Token
)
from crypto import Polybius

user_token = None

def send_request(url: str, method: str, data: bytes) -> dict:
    #Универсальная функция для отправки HTTP-запросов

    request = urllib.request.Request(url, data=data, method=method)
    request.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(request)
        response_data = response.read().decode('utf-8')
        if response_data:  #если есть данные в ответе
            return json.loads(response_data)
        return {"message": "Операция выполнена успешно"}  #если ответ пустой
    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        try:
            error_data = json.loads(error_message)
            return {"error": error_data.get("detail", "Ошибка запроса").split(": ")[-1]}
        except json.JSONDecodeError:
            return {"error": "Ошибка при обработке ответа сервера"}

def show_texts(url: str, user: bytes, header: str) -> list:
    response = send_request(url, 'GET', user)
    print(header)
    texts = response.get('texts', [])
    for index, text_info in enumerate(texts, start=1):
        print(f"{index}. {text_info['content']}")
    return texts

def text_one(url: str, user: bytes): #для просмотра одного текста
    response = send_request(url, 'GET', user)
    texts = response.get('texts', [])  #получение количества текстов
    text_count = len(texts)
    print(f"У вас {text_count} текст(ов).")  #выбор текста
    while True:
        try:
            text_number = int(input(f"Выберете номер текста от 1 до {text_count}: "))
            if 1 <= text_number <= text_count:
                return text_number
            else:
                print(f"Введите число от 1 до {text_count}.")
        except ValueError:
            print("Введите корректное число.")

def auth():
    global user_token
    login = input("Введите логин: ")
    password = getpass.getpass("Введите пароль: ")
    user_data = User(login=login, password=password, token='token').model_dump_json().encode('utf-8')
    response = send_request('http://127.0.0.1:8000/auth', 'POST', user_data)
    if isinstance(response, dict) and "error" in response:  #если ошибка в ответе
        print("Ошибка авторизации:", response["error"])
        return False
    print("Авторизация успешна!")
    if isinstance(response, str):
        response = json.loads(response)  #декодирование ответа, если он строка
    user_token = response.get("token")  #сохраняем токен в глобальной переменной
    return True 

def registration():
    global user_token
    login = input("Введите логин: ")
    password = getpass.getpass("Введите пароль: ")
    user_data = User(login = login, password = password, token='token').model_dump_json().encode('utf-8')
    response = send_request('http://127.0.0.1:8000/register', 'POST', user_data)
    if isinstance(response, dict) and "error" in response:  #если ошибка в ответе
        print("Ошибка регистрации:", response["error"])
        return False
    print("Регистрация успешна!")
    if isinstance(response, str):
        response = json.loads(response)  #декодирование ответа, если он строка
    user_token = response.get("token")  #сохраняем токен в глобальной переменной
    return True 

def add_text():
    global user_token
    text = input("Введите текст, который хотите добавить: ")
    
    #создаем объект запроса для текста
    text_request = Text_Request(text=text, token=user_token)
    text_data = text_request.model_dump_json().encode('utf-8')
    
    #отправляем запрос на добавление текста
    response = send_request('http://127.0.0.1:8000/add_text', 'POST', text_data)
    
    if "error" in response:
        print("Ошибка при добавлении текста:", response["error"])
        return False
        
    #создаем запрос для шифрования
    encrypt_request = Polybius_Encrypt_Request(
        text=text,
        token=user_token
    )
    
    #отправляем запрос на шифрование
    encrypt_response = send_request('http://127.0.0.1:8000/encrypt', 'POST',
                        encrypt_request.model_dump_json().encode('utf-8'))
    
    if "error" in encrypt_response:
        print("Ошибка при шифровании:", encrypt_response["error"])
    else:
        print(f"Текст успешно добавлен и зашифрован!")
        print(f"Оригинальный текст: {text}")
        print(f"Зашифрованный текст: {encrypt_response['encrypted']}")
    return True

def edit_text():
    user = Token(token=user_token).model_dump_json().encode('utf-8')
    response = send_request('http://127.0.0.1:8000/view_all_texts', 'GET', user)
    print("Тексты:")
    texts = response.get('texts', [])
    for index, text_info in enumerate(texts, start=1):
        print(f"{index}. {text_info['content']}")
    while True: 
        try:
            text_number = int(input("Введите номер текста, который хотите изменить:\n"))
            if 1 <= text_number <= len(texts):  #проверка корректности индекса
                new_text = input("Введите новый текст:\n")
                change_text = Change_Text_Request(token=user_token, text_number=text_number, new_text = new_text).model_dump_json().encode('utf-8')
                response = send_request('http://127.0.0.1:8000/change_text', 'PATCH', change_text)
                if "error" in response:
                    print("Ошибка при изменении текста:", response["error"])
                else:
                    print("Текст успешно изменен!")
                return True
            else:
                print(f"Введите номер от 1 до {len(texts)}.")
        except ValueError:
            print("Введите корректный номер текста.")

def delete_text():
    user = Token(token=user_token).model_dump_json().encode('utf-8')
    texts = show_texts('http://127.0.0.1:8000/view_all_texts', user, "Тексты:")
    while True:  #выбор текста для удаления
        try:
            text_number = int(input("Введите номер текста, который хотите удалить: "))
            if 1 <= text_number <= len(texts):  #проверка корректности индекса
                delete = Delete_Request(token=user_token, text_number=text_number - 1).model_dump_json().encode('utf-8')
                response = send_request('http://127.0.0.1:8000/delete_text', 'DELETE', delete)
                
                if isinstance(response, dict):
                    if "error" in response:
                        print("Ошибка при удалении текста:", response["error"])
                    elif "message" in response:
                        print(response["message"])
                    else:
                        print("Текст успешно удален")
                else:
                    print("Текст успешно удален")
                return True
            else:
                print(f"Введите номер от 1 до {len(texts)}.")
        except ValueError:
            print("Введите корректный номер текста.")

def view_one_text():
    user = Token(token=user_token).model_dump_json().encode('utf-8')
    text = text_one(url = 'http://127.0.0.1:8000/view_all_texts', user=user)
    one_text = One_Text_Request(token=user_token, text_number=text).model_dump_json().encode('utf-8') #Получаем текст
    response = send_request('http://127.0.0.1:8000/view_one_text', 'GET', one_text)
    selected_text = response.get('text', "Текст не найден.")
    print(f"Выбранный текст: {selected_text}")
    return True
        
def view_texts():
    user = Token(token=user_token).model_dump_json().encode('utf-8')
    response = send_request('http://127.0.0.1:8000/view_all_texts', 'GET', user)
    texts = response.get('texts', [])
    
    if not texts:
        print("У вас пока нет сохраненных текстов.")
        return True
        
    print("Ваши тексты:")
    for index, text_info in enumerate(texts, start=1):
        # Создаем запрос для шифрования
        encrypt_request = Polybius_Encrypt_Request(
            text=text_info['content'],
            token=user_token
        )
        
        #отправляем запрос на шифрование
        encrypt_response = send_request('http://127.0.0.1:8000/encrypt', 'POST',
                            encrypt_request.model_dump_json().encode('utf-8'))
        
        if "error" in encrypt_response:
            print(f"{index}. Оригинал: {text_info['content']}")
            print(f"   Ошибка при шифровании: {encrypt_response['error']}")
        else:
            print(f"{index}. Оригинал: {text_info['content']}")
            print(f"   Зашифрованный: {encrypt_response['encrypted']}")
    return True

def crypto_text():
    global user_token
    text = input("Введите текст для шифрования: ")
    
    #создаем запрос для шифрования
    encrypt_request = Polybius_Encrypt_Request(
        text=text,
        token=user_token
    )
    
    #отправляем запрос на шифрование
    response = send_request('http://127.0.0.1:8000/encrypt', 'POST',
                        encrypt_request.model_dump_json().encode('utf-8'))
    
    if "error" in response:
        if "'b'" in response["error"]:
            print("Данные введены некорректно")
        else:
            print(response["error"])
    else:
        print(f"Зашифрованный текст: {response['encrypted']}")
    return True

def encrypto_text():
    global user_token
    
    print("Выберите язык текста:")
    print("1 - Русский")
    print("2 - Английский")
    
    while True:
        try:
            choice = int(input("Введите номер (1 или 2): "))
            if choice in [1, 2]:
                break
            print("Пожалуйста, введите 1 или 2")
        except ValueError:
            print("Пожалуйста, введите число")
    
    #запрашиваем текст для расшифровки
    text = input("Введите текст для расшифровки: ")
    
    #проверяем, что текст состоит только из цифр и их количество четное
    if not text.isdigit():
        print("Текст должен содержать только цифры")
        return True
    if len(text) % 2 != 0:
        print("Количество цифр должно быть четным")
        return True
    
    #создаем запрос для дешифрования
    decrypt_request = Polybius_Decrypt_Request(
        text=text,
        token=user_token,
        language=choice
    )
    
    #отправляем запрос на дешифрование
    response = send_request('http://127.0.0.1:8000/decrypt', 'POST',
                        decrypt_request.model_dump_json().encode('utf-8'))
    
    if "error" in response:
        if "'b'" in response["error"]:
            print("Данные введены некорректно")
        else:
            print(response["error"])
    else:
        print(f"Расшифрованный текст: {response['decrypted']}")
    return True


def edit_password():
    global user_token
    old_password = getpass.getpass("Введите старый пароль: ")
    password = getpass.getpass("Введите новый пароль: ")
    password_request = Change_Password_Request(old_password=old_password, new_password=password, token=user_token).model_dump_json().encode('utf-8')
    response = send_request('http://127.0.0.1:8000/change_password', 'PUT', password_request)
    
    if "error" in response:
        print("Ошибка при смене пароля:", response["error"])
        return False
    else:
        print("Пароль успешно изменен!")
        
    new_token = response.get("token") #обновление глобального токен с новым значением
    if new_token:
        user_token = new_token
    return True

def main():
    print("Добро пожаловать в приложение 'Квадрат Полибия'!")
    print("Это приложение позволяет:")
    print("- Шифровать и расшифровывать тексты")
    print("- Сохранять и управлять вашими текстами")
    print("- Работать с русским и английским языками")
    
    aut = False
    while True:
        if not aut:
            print("1 - Регистрация")
            print("2 - Авторизация")
            choice = input("Введите номер действия: ")
            if choice == "1":
                registration()
            elif choice == "2":
                aut=auth()
        else:
            print("1 - Добавить текст")
            print("2 - Изменить текст")
            print("3 - Удалить текст")
            print("4 - Просмотреть один текст")
            print("5 - Просмотреть все тексты")
            print("6 - Зашифровать текст")
            print("7 - Расшифровать текст")
            print("8 - Изменить пароль")
            print("0 - Выход")
            choice = input("Введите номер действия: ")
            if choice == "1":
                add_text()
            elif choice == "2":
                edit_text()
            elif choice == "3":
                delete_text()
            elif choice == "4":
                view_one_text()
            elif choice == "5":
                view_texts()
            elif choice == "6":
                crypto_text()
            elif choice == "7":
                encrypto_text()
            elif choice == "8":
                edit_password()
            elif choice == "0":
                break
            else:
                print("Неверная команда!")

if __name__ == "__main__":
    main()
