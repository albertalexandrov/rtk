from unittest import mock
from unittest.mock import AsyncMock

import pytest
import sqlalchemy.exc

from aiokafka import ConsumerRecord
from app.config import settings
from app.kafka import consume
from app.models import User
from app.repositories import UsersRepository


class Consumer:
    def __init__(self, seq):
        super().__init__()
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

    async def start(self):
        pass

    async def stop(self):
        pass


class Producer(AsyncMock):
    pass


class TestConsume:
    """Тестирование функции parse."""

    def setup_method(self):
        self.producer = Producer()

    async def test_user_created(self, users_repository: UsersRepository):
        xml = """
            <ns2:Request xmlns:ns2="urn://www.example.com">
                <ns2:User>
                    <ns2:Name>Иван</ns2:Name>
                    <ns2:Surname>Иванов</ns2:Surname>
                    <ns2:Email>ivan.ivanov.2023.2024@yandex.com</ns2:Email>
                    <ns2:Birthday>2005-10-23T04:00:00+03:00</ns2:Birthday>
                </ns2:User>
            </ns2:Request>
        """

        msg = ConsumerRecord(
            topic=settings.kafka.consume_topic,
            partition=0,
            offset=28,
            timestamp=1697655000970,
            timestamp_type=0,
            key=None,
            value=xml.strip().encode(),
            checksum=None,
            serialized_key_size=-1,
            serialized_value_size=350,
            headers=(),
        )
        consumer = Consumer([msg])

        with mock.patch("app.kafka.send_success_feedback") as send_success_feedback:
            await consume(consumer, self.producer, users_repository)

            assert (
                user := await users_repository.get(
                    User.name == "Иван",
                    User.surname == "Иванов",
                    User.email == "ivan.ivanov.2023.2024@yandex.com",
                )
            )
            send_success_feedback.assert_called_once_with(self.producer, user.id)

    @pytest.mark.parametrize(
        "field,bad_value",
        [
            ("name", ""),
            ("name", "a" * 256),
            ("surname", ""),
            ("surname", "a" * 256),
            ("email", "NOT-EMAIL"),
            ("email", "a" * 255 + "@mail.ru"),
        ],
    )
    async def test_user_not_created(self, field, bad_value, users_repository):
        values = {
            "name": "Иван",
            "surname": "Иванов",
            "email": "ivan.ivanov.2023.2024@yandex.com",
            "birthday": "2005-10-23T04:00:00+03:00",
        }
        values[field] = bad_value

        xml = """
            <ns2:Request xmlns:ns2="urn://www.example.com">
                <ns2:KafkaUser>
                    <ns2:Name>{name}</ns2:Name>
                    <ns2:Surname>{surname}</ns2:Surname>
                    <ns2:Email>{email}</ns2:Email>
                    <ns2:Birthday>{birthday}</ns2:Birthday>
                </ns2:KafkaUser>
            </ns2:Request>
        """.format_map(
            values
        )

        msg = ConsumerRecord(
            topic=settings.kafka.consume_topic,
            partition=0,
            offset=28,
            timestamp=1697655000970,
            timestamp_type=0,
            key=None,
            value=xml.strip().encode(),
            checksum=None,
            serialized_key_size=-1,
            serialized_value_size=350,
            headers=(),
        )
        consumer = Consumer([msg])

        with mock.patch("app.kafka.send_failed_feedback") as send_failed_feedback:
            await consume(consumer, self.producer, users_repository)

            with pytest.raises(sqlalchemy.exc.NoResultFound):
                await users_repository.get(
                    User.name == values["name"],
                    User.surname == values["surname"],
                    User.email == values["email"],
                )

            send_failed_feedback.assert_called_once_with(self.producer, values)
