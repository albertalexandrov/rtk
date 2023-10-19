import asyncio

import uvicorn
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import FastAPI

from app.config import settings
from app.database import SessionLocal
from app.kafka import consume
from app.repositories import UsersRepository
from app.routers import router

app = FastAPI()
app.include_router(router)

loop = asyncio.get_event_loop()

consumer = AIOKafkaConsumer(settings.kafka.consume_topic, loop=loop, bootstrap_servers=settings.kafka.bootstrap_servers)
producer = AIOKafkaProducer(loop=loop, bootstrap_servers=settings.kafka.bootstrap_servers)


@app.on_event("startup")
async def startup_event():
    await producer.start()
    await consumer.start()
    users_repository = UsersRepository(session=SessionLocal())
    loop.create_task(consume(consumer, producer, users_repository))


@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()
    # await consumer.stop()


@app.get("/")
async def index():
    print("отправка")
    msg = """<ns2:Request xmlns:ns2="urn://www.example.com">
            <ns2:KafkaUser>
            <ns2:Name>Иван</ns2:Name>
            <ns2:Surname>Иванов</ns2:Surname>
            <ns2:Email>ivan.ivanov.2023.2024@yandex.com</ns2:Email>
            <ns2:Birthday>2005-10-23T04:00:00+03:00</ns2:Birthday>
            </ns2:KafkaUser>
            </ns2:Request>""".encode()
    await producer.send(settings.kafka.consume_topic, msg)
    print("отправили")
    return "Сообщение отправлено"



if __name__ == '__main__':
    uvicorn.run("main:app", port=8003, reload=True)
