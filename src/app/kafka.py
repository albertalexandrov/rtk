import logging
import xml.etree.ElementTree as ET
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.config import settings
from app.repositories import UsersRepository
from pydantic_core import ValidationError

LOGGER = logging.getLogger(__name__)


class KafkaUser(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    surname: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(min_length=1, max_length=255)
    birthday: datetime


def parse(msg: str) -> dict:
    """Извлечение данных из сообщения.

    Args:
        msg: сообщение из топика

    """

    xml = ET.fromstring(msg)
    namespaces = {"ns2": "urn://www.example.com"}
    name = xml.find(".//ns2:Name", namespaces).text
    surname = xml.find(".//ns2:Surname", namespaces).text
    email = xml.find(".//ns2:Email", namespaces).text
    birthday = xml.find(".//ns2:Birthday", namespaces).text

    return {
        "name": name or "",
        "surname": surname or "",
        "email": email or "",
        "birthday": birthday or "",
    }


async def send_success_feedback(producer: AIOKafkaProducer, user_id: int):
    """Отправка успешного фидбека.

    Args:
        producer: продьюсер
        user_id: идентификатор созданного пользователя

    """

    msg = f"""
        <ns2:Response xmlns:ns2="urn://www.example.com">
            <ns2:KafkaUser>
                <ns2:Id>{user_id}</ns2:Id>
                <ns2:Status>SUCCESS</ns2:Status>
            </ns2:KafkaUser>
        </ns2:Response>
    """

    await send_feedback(producer, msg.strip().encode())


async def send_failed_feedback(producer: AIOKafkaProducer, user_data: dict):
    """Отправка неуспешного фидбека.

    Args:
        producer: продьюсер
        user_data: данные пользователя из топика

    """

    msg = """
        <ns2:Response xmlns:ns2="urn://www.example.com">
            <ns2:KafkaUser>
                <ns2:Name>{name}</ns2:Name>
                <ns2:Surname>{surname}</ns2:Surname>
                <ns2:Email>{email}</ns2:Email>
                <ns2:Birthday>{birthday}</ns2:Birthday>
                <ns2:Status>FAILED</ns2:Status
            </ns2:KafkaUser>
        </ns2:Response>
    """.format_map(
        user_data
    )

    await send_feedback(producer, msg.strip().encode())


async def send_feedback(producer: AIOKafkaProducer, msg: bytes) -> None:
    """Отправка сообщения в топик фидбеков.

    Args:
        producer: продьюсер
        msg: сообщение

    """

    await producer.send(settings.kafka.feedback_topic, msg)


async def consume(
    consumer: AIOKafkaConsumer,
    producer: AIOKafkaProducer,
    users_repository: UsersRepository,
) -> None:
    """Обработка сообщений из топика.

    Args:
        consumer: консумер
        producer: продьюсер
        users_repository

    """

    try:
        async for msg in consumer:
            user_data = parse(msg.value.decode())

            try:
                user = KafkaUser(**user_data)
            except ValidationError:
                await send_failed_feedback(producer, user_data)
            else:
                create_data = user.model_dump()
                user = await users_repository.create(**create_data)
                await users_repository.commit()
                await users_repository.refresh(user)

                await send_success_feedback(producer, user.id)

    finally:
        await consumer.stop()
