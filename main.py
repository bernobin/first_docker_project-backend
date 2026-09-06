from typing import Protocol

import mysql.connector
from fastapi import FastAPI

from src.DatabaseConfig import DatabaseConfig


class HelloAppDatabase(Protocol):
    def add_greeting(self, message: str) -> None: ...


class Database:
    password = property()
    config = property()

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @config.getter
    def config(self) -> DatabaseConfig:
        return self._config

    @config.setter
    def config(self, config: DatabaseConfig):
        self._config = config

    def connect(self):
        return mysql.connector.connect(
            host=self.config.host,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
        )

    def add_greeting(self, message: str) -> None:
        db = self.connect()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO greetings (message) VALUES (%s)",
            (message,),
        )

        db.commit()

        cursor.close()
        db.close()


class Api:
    database = property()

    def __init__(self, database: HelloAppDatabase):
        self.database = database
        self.app: FastAPI = FastAPI()

        self.app.get("/")(self.root)
        self.app.post("/api/hello")(self.hello)

    @database.getter
    def database(self) -> HelloAppDatabase:
        return self._database

    @database.setter
    def database(self, database: HelloAppDatabase):
        self._database = database

    def root(self) -> dict[str, str]:
        return {"message": "Hello from Python!"}

    def hello(self) -> dict[str, str]:
        self.database.add_greeting("Hello from Vue!")
        return {"message": "Hello!"}


config = DatabaseConfig.from_docker_secrets(
    host="db",
    user="hello",
    database="helloapp",
    password_key="db_user_password",
)

database = Database(config)
api = Api(database)

app = api.app
