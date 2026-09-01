from typing import Protocol

import mysql.connector
from fastapi import FastAPI


class GreetingDatabase(Protocol):
    def add_greeting(self, message: str) -> None: ...


class Database:
    def __init__(self):
        self.password: str = self.read_secret("db_user_password")

    def read_secret(self, name: str) -> str:
        with open(f"/run/secrets/{name}", "r") as f:
            return f.read().strip()

    def connect(self):
        return mysql.connector.connect(
            host="db",
            user="hello",
            password=self.password,
            database="helloapp",
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
    def __init__(self, database: Database):
        self.database: GreetingDatabase = database
        self.app: FastAPI = FastAPI()

        self.app.get("/")(self.root)
        self.app.post("/api/hello")(self.hello)

    def root(self) -> dict[str, str]:
        return {"message": "Hello from Python!"}

    def hello(self) -> dict[str, str]:
        self.database.add_greeting("Hello from Vue!")
        return {"message": "Hello!"}


database = Database()
api = Api(database)

app = api.app
