from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI()

def read_secret(name: str) -> str:
    with open(F"/run/secrets/{name}", "r") as f:
        return f.read().strip()

def get_db():
    password = read_secret("db_user_password")

    return mysql.connector.connect(
        host="db",
        user="hello",
        password=password,
        database="helloapp",
    )

@app.get("/")
def root():
    return {"message": "Hello from Python!"}


@app.post("/api/hello")
def hello():
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO greetings (message) VALUES (%s)",
        ("Hello from Vue!",),
    )

    db.commit()

    cursor.close()
    db.close()

    return {"message": "Hello!"}