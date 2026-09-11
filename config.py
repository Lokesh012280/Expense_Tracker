import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017"
    )

    DB_NAME = os.getenv(
        "MONGO_DATABASE",
        "expense_tracker_db"
    )

    TRIP_COLLECTION = os.getenv(
        "TRIP_COLLECTION",
        "trips"
    )

    EXPENSE_COLLECTION = os.getenv(
        "EXPENSE_COLLECTION",
        "expenses"
    )


settings = Settings()