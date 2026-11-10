from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


def now() -> datetime:
    return datetime.now(timezone.utc)


def oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid resource id")
    return ObjectId(value)


def public(document: dict[str, Any] | None) -> dict[str, Any] | None:
    if document is None:
        return None
    result = dict(document)
    result["id"] = str(result.pop("_id"))
    return result


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.collection = db.users

    async def by_email(self, email: str):
        return public(await self.collection.find_one({"email": email.lower()}))

    async def by_id(self, user_id: str):
        return public(await self.collection.find_one({"_id": oid(user_id)}))

    async def create(self, data: dict[str, Any]):
        result = await self.collection.insert_one(data)
        return public(await self.collection.find_one({"_id": result.inserted_id}))


class ProjectRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.projects
        self.documents = db.documents
        self.findings = db.findings

    async def list(self, owner_id: str):
        items = []
        async for item in self.collection.find({"owner_id": owner_id}).sort("updated_at", -1):
            row = public(item)
            row["document_count"] = await self.documents.count_documents({"project_id": row["id"]})
            row["finding_count"] = await self.findings.count_documents({"project_id": row["id"]})
            items.append(row)
        return items

    async def get(self, project_id: str, owner_id: str):
        row = public(await self.collection.find_one({"_id": oid(project_id), "owner_id": owner_id}))
        if row:
            row["document_count"] = await self.documents.count_documents({"project_id": row["id"]})
            row["finding_count"] = await self.findings.count_documents({"project_id": row["id"]})
        return row

    async def create(self, data: dict[str, Any]):
        result = await self.collection.insert_one(data)
        return await self.get(str(result.inserted_id), data["owner_id"])

    async def update(self, project_id: str, owner_id: str, values: dict[str, Any]):
        values["updated_at"] = now()
        await self.collection.update_one({"_id": oid(project_id), "owner_id": owner_id}, {"$set": values})
        return await self.get(project_id, owner_id)


class DocumentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection, self.chunks = db.documents, db.chunks

    async def list(self, project_id: str):
        return [public(row) async for row in self.collection.find({"project_id": project_id}).sort("uploaded_at", -1)]

    async def get(self, document_id: str, project_id: str):
        return public(await self.collection.find_one({"_id": oid(document_id), "project_id": project_id}))

    async def create(self, data: dict[str, Any]):
        result = await self.collection.insert_one(data)
        return public(await self.collection.find_one({"_id": result.inserted_id}))

    async def update(self, document_id: str, values: dict[str, Any]):
        await self.collection.update_one({"_id": oid(document_id)}, {"$set": values})

    async def replace_chunks(self, document_id: str, chunks: list[dict[str, Any]]):
        await self.chunks.delete_many({"document_id": document_id})
        if chunks: await self.chunks.insert_many(chunks)

    async def delete(self, document_id: str, project_id: str):
        await self.chunks.delete_many({"document_id": document_id, "project_id": project_id})
        return await self.collection.delete_one({"_id": oid(document_id), "project_id": project_id})


class FindingRepository:
    def __init__(self, db: AsyncIOMotorDatabase): self.collection = db.findings

    async def list(self, project_id: str, status: str | None = None):
        query: dict[str, Any] = {"project_id": project_id}
        if status: query["review_status"] = status
        return [public(row) async for row in self.collection.find(query).sort("created_at", -1)]

    async def insert_many(self, rows: list[dict[str, Any]]) -> int:
        if not rows: return 0
        await self.collection.insert_many(rows)
        return len(rows)

    async def review(self, finding_id: str, project_id: str, reviewer_id: str, status: str, comment: str):
        await self.collection.update_one(
            {"_id": oid(finding_id), "project_id": project_id},
            {"$set": {"review_status": status, "review_comment": comment, "reviewer_id": reviewer_id, "reviewed_at": now()}},
        )
        return public(await self.collection.find_one({"_id": oid(finding_id), "project_id": project_id}))

