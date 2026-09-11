from fastapi import FastAPI
from contextlib import asynccontextmanager
import database

from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Connecting to MongoDB...")

    database.connect()

    yield

    print("Disconnecting from MongoDB...")

    database.disconnect()

    print("MongoDB disconnected")


app = FastAPI(
    title="Travel Expense Tracker API",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "message": "Travel Expense Tracker API"
    }