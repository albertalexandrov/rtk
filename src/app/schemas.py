from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    id: int = Field(title="ID", example=1)
    name: str = Field(title="Имя", example="Сергей")
    surname: str = Field(title="Фамилия", example="Иванов")
    email: EmailStr = Field(title="Email", example="serg.ivanov@rtk.ru")
    birthday: datetime = Field(title="Дата и время рождения")

    class Config:
        from_attributes = True


class UserCreateData(BaseModel):
    name: str = Field(max_length=255, title="Имя", example="Сергей")
    surname: str = Field(max_length=255, title="Фамилия", example="Иванов")
    email: EmailStr = Field(max_length=255, title="Email", example="serg.ivanov@rtk.ru")
    birthday: datetime = Field(title="Дата и время рождения")


class UserUpdateData(BaseModel):
    name: str = Field(default=None, max_length=255, title="Имя", example="Сергей")
    surname: str = Field(default=None, max_length=255, title="Фамилия", example="Иванов")
    email: EmailStr = Field(default=None, max_length=255, title="Email", example="serg.ivanov@rtk.ru")
    birthday: datetime = Field(default=None, title="Дата и время рождения")
