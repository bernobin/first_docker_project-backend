from fastapi import FastAPI
import mysql.connector

app = FastAPI()

def get_db():
    return mysql.connector.connect(
        host="db",
        user="hello",
        password="hellopassword",
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