import logging
import os

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine


class MongoDB:
    MONGO_URL = os.getenv("MONGO_DB_URL")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_MAX_CONNECTIONS = os.getenv("MONGO_MAX_CONNECTIONS")
    MONGO_MIN_CONNECTIONS = os.getenv("MONGO_MIN_CONNECTIONS")

    def __init__(self) -> None:
        self.__client: AsyncIOMotorClient = None
        self.__engine: AIOEngine = None

    @property
    def client(self) -> AsyncIOMotorClient:
        return self.__client

    @property
    def engine(self) -> AIOEngine:
        return self.__engine

    async def connect(self):
        self.__client = AsyncIOMotorClient(
            self.MONGO_URL,
            maxPoolSize=self.MONGO_MAX_CONNECTIONS,
            minPoolSize=self.MONGO_MIN_CONNECTIONS,
        )
        self.__engine = AIOEngine(client=self.__client, database=self.MONGO_DB_NAME)
        logging.info("DB와 성공적으로 연결이 되었습니다.")

    async def close(self):
        self.__client.close()


mongodb = MongoDB()
