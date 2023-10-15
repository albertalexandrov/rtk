from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор пользователя")
    name: Mapped[str] = mapped_column(String(255), comment="Имя")
    surname: Mapped[str] = mapped_column(String(255), comment="Фамилия")
    email: Mapped[str] = mapped_column(String(255), comment="Email")
    birthday: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment="Дата и время рождения")
