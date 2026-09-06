from typing import Protocol

import mysql.connector
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from src.DatabaseConfig import DatabaseConfig


class HelloAppDatabase(Protocol):
    def add_greeting(self, message: str) -> None: ...

    # Blog Message CRUD Operations
    def create_message(self, title: str, content: str) -> int: ...
    def get_message(self, message_id: int) -> dict | None: ...
    def get_all_messages(self) -> list[dict]: ...
    def update_message(self, message_id: int, title: str, content: str) -> bool: ...
    def delete_message(self, message_id: int) -> bool: ...


class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    @property
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

    def create_message(self, title: str, content: str) -> int:
        db = self.connect()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO blog_messages (title, content) VALUES (%s, %s)",
            (title, content),
        )
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        if new_id is None:
            raise RuntimeError("Failed to retrieve lastrowid after INSERT")

        return new_id

    def get_message(self, message_id: int) -> dict | None:
        db = self.connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title, content FROM blog_messages WHERE id = %s",
            (message_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        db.close()

        if isinstance(row, dict):
            return row

        return None

    def get_all_messages(self) -> list[dict]:
        db = self.connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, title, content FROM blog_messages")
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        return [row for row in rows if isinstance(row, dict)]

    def update_message(self, message_id: int, title: str, content: str) -> bool:
        db = self.connect()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE blog_messages SET title = %s, content = %s WHERE id = %s",
            (title, content, message_id),
        )
        db.commit()
        affected = cursor.rowcount > 0
        cursor.close()
        db.close()
        return affected

    def delete_message(self, message_id: int) -> bool:
        db = self.connect()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM blog_messages WHERE id = %s",
            (message_id,),
        )
        db.commit()
        affected = cursor.rowcount > 0
        cursor.close()
        db.close()
        return affected

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


# Pydantic schemas for request validation
class BlogMessageCreate(BaseModel):
    title: str
    content: str


class BlogMessageUpdate(BaseModel):
    title: str
    content: str


class Api:
    def __init__(self, database: HelloAppDatabase):
        self.database = database
        self.app = FastAPI()

        self.app.get("/")(self.root)
        self.app.post("/api/hello")(self.hello)

        # Blog CRUD Routes
        self.app.post("/api/posts", status_code=status.HTTP_201_CREATED)(
            self.create_post
        )
        self.app.get("/api/posts")(self.get_posts)
        self.app.get("/api/posts/{post_id}")(self.get_post)
        self.app.put("/api/posts/{post_id}")(self.update_post)
        self.app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)(
            self.delete_post
        )

    @property
    def database(self) -> HelloAppDatabase:
        return self._database

    @database.setter
    def database(self, database: HelloAppDatabase):
        self._database = database

    @property
    def app(self) -> FastAPI:
        return self._app

    @app.setter
    def app(self, app: FastAPI):
        self._app = app

    def root(self) -> dict[str, str]:
        return {"message": "Hello from Python!"}

    def hello(self) -> dict[str, str]:
        self.database.add_greeting("Hello from Vue!")
        return {"message": "Hello!"}

    def create_post(self, payload: BlogMessageCreate) -> dict:
        new_id = self.database.create_message(payload.title, payload.content)
        return {"id": new_id, "title": payload.title, "content": payload.content}

    def get_posts(self) -> list[dict]:
        return self.database.get_all_messages()

    def get_post(self, post_id: int) -> dict:
        post = self.database.get_message(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog message with id {post_id} not found",
            )
        return post

    def update_post(self, post_id: int, payload: BlogMessageUpdate) -> dict:
        updated = self.database.update_message(post_id, payload.title, payload.content)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog message with id {post_id} not found",
            )
        return {"id": post_id, "title": payload.title, "content": payload.content}

    def delete_post(self, post_id: int) -> None:
        deleted = self.database.delete_message(post_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blog message with id {post_id} not found",
            )


config = DatabaseConfig.from_docker_secrets(
    host="db",
    user="hello",
    database="helloapp",
    password_key="db_user_password",
)

database = Database(config)
api = Api(database)

app = api.app
