from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

# from configs.config import MONGO_DB_NAME, MONGO_URL
import os
import logging


class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None
        self.MONGO_URL = os.getenv("MONGO_DB_URL")
        self.MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

    def connect(self):
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.engine = AIOEngine(client=self.client, database=self.MONGO_DB_NAME)
        # self.client = AsyncIOMotorClient(MONGO_URL)
        # self.engine = AIOEngine(client=self.client, database=MONGO_DB_NAME)
        logging.info("DB와 성공적으로 연결이 되었습니다.")

    def close(self):
        self.client.close()


mongodb = MongoDB()
