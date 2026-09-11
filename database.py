from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection

from config import settings


_client: MongoClient | None = None


def connect() -> None:
    global _client

    _client = MongoClient(
        settings.MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    _client.admin.command("ping")

    trip_collection = get_trip_collection()
    expense_collection = get_expense_collection()

    trip_collection.create_index(
        [("trip_name", ASCENDING)]
    )

    expense_collection.create_index(
        [("trip_id", ASCENDING)]
    )

    expense_collection.create_index(
        [("category", ASCENDING)]
    )

    expense_collection.create_index(
        [("paid_by", ASCENDING)]
    )


def get_client() -> MongoClient:
    if _client is None:
        connect()

    return _client


def get_trip_collection() -> Collection:
    if _client is None:
        raise ValueError("MongoDB client not initialized")

    return get_client()[
        settings.DB_NAME
    ][
        settings.TRIP_COLLECTION
    ]


def get_expense_collection() -> Collection:
    if _client is None:
        raise ValueError("MongoDB client not initialized")

    return get_client()[
        settings.DB_NAME
    ][
        settings.EXPENSE_COLLECTION
    ]


def disconnect() -> None:
    global _client

    if _client is not None:
        _client.close()
        _client = None