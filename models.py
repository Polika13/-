from pydantic import BaseModel
from typing import Union, List

class User(BaseModel): #модель для пользователя
    login: str
    password: str
    token: str
    id: Union[int, None] = None

class Polybius_Encrypt_Request(BaseModel):
    text: str
    token: str

class Polybius_Decrypt_Request(BaseModel):
    text: str
    token: str
    language: int

class Change_Text_Request(BaseModel): #модель для изменения текста
    token: str
    text_number: int
    new_text: str

class Delete_Request(BaseModel): #модель для удаления текста
    token: str
    text_number: int

class One_Text_Request(BaseModel): #модель для просмотра одного текста
    token: str
    text_number: int

class Change_Password_Request(BaseModel): #модель для смены пароля
    old_password: str
    new_password: str
    token: str

class Text_Request(BaseModel): #модель для работы с текстом
    text: str
    token: str

class Token(BaseModel):
    token: str 