import logging
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from app.core.config import get_settings


logger = logging.getLogger("reqlens.database")
client: Any | None = None
database: Any | None = None
database_backend = "disconnected"


async def _create_indexes(db: Any) -> None:
    await db.users.create_index("email", unique=True)
    await db.projects.create_index([("owner_id", 1), ("updated_at", -1)])
    await db.documents.create_index([("project_id", 1), ("uploaded_at", -1)])
    await db.chunks.create_index([("project_id", 1), ("document_id", 1)])
    await db.findings.create_index([("project_id", 1), ("review_status", 1)])


async def connect_database() -> None:
    global client, database, database_backend
    settings = get_settings()
    real_client = AsyncIOMotorClient(settings.mongodb_url, serverSelectionTimeoutMS=2000)
    try:
        real_database = real_client[settings.mongodb_db_name]
        await real_database.command("ping")
        client, database, database_backend = real_client, real_database, "mongodb"
    except PyMongoError as exc:
        real_client.close()
        if not settings.can_use_in_memory_db:
            raise RuntimeError("MongoDB is unavailable and the development fallback is disabled") from exc
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
        database = client[settings.mongodb_db_name]
        database_backend = "in-memory-development"
        logger.warning("MongoDB unavailable; using temporary in-memory development database. Data resets when the API stops.")
    await _create_indexes(database)


async def close_database() -> None:
    global client, database, database_backend
    if client:
        client.close()
        client = None
    database = None
    database_backend = "disconnected"


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("Database is not connected")
    return database


def get_database_backend() -> str:
    return database_backend

