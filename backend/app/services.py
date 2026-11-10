from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.audit import audit_chunks
from app.agent_graph import build_chat_graph
from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.ingestion import ALLOWED_EXTENSIONS, chunk_pages, extract_pages, safe_upload_path
from app.rag import RetrievalService, external_search
from app.repositories import DocumentRepository, FindingRepository, ProjectRepository, UserRepository, now


def not_found(label: str = "Resource") -> HTTPException:
    return HTTPException(status_code=404, detail=f"{label} not found")


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase): self.users = UserRepository(db)

    async def register(self, name: str, email: str, password: str):
        if await self.users.by_email(email):
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        try:
            user = await self.users.create({"name": name, "email": email.lower(), "password_hash": hash_password(password), "created_at": now()})
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        return {"access_token": create_access_token(user["id"]), "user": user}

    async def login(self, email: str, password: str):
        user = await self.users.by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        return {"access_token": create_access_token(user["id"]), "user": user}


class ProjectService:
    def __init__(self, db: AsyncIOMotorDatabase): self.repo = ProjectRepository(db)

    async def get_required(self, project_id: str, user_id: str):
        project = await self.repo.get(project_id, user_id)
        if not project: raise not_found("Project")
        return project

    async def create(self, user_id: str, data: dict):
        timestamp = now()
        return await self.repo.create({**data, "owner_id": user_id, "status": "active", "created_at": timestamp, "updated_at": timestamp})


class DocumentService:
    def __init__(self, db: AsyncIOMotorDatabase, settings: Settings):
        self.db, self.settings = db, settings
        self.repo = DocumentRepository(db)
        self.retrieval = RetrievalService(db, settings)

    async def upload_and_process(self, project_id: str, user_id: str, file: UploadFile, document_type: str, version: str):
        original = Path(file.filename or "document").name
        extension = Path(original).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=415, detail="Only PDF, DOCX and TXT files are supported")
        content = await file.read(self.settings.max_upload_mb * 1024 * 1024 + 1)
        if len(content) > self.settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File exceeds {self.settings.max_upload_mb} MB")
        if not content: raise HTTPException(status_code=400, detail="The uploaded file is empty")
        stored_name = f"{uuid4().hex}{extension}"
        path = safe_upload_path(self.settings.upload_dir, stored_name)
        path.write_bytes(content)
        row = await self.repo.create({
            "project_id": project_id, "filename": original, "stored_name": stored_name,
            "file_type": extension.removeprefix("."), "document_type": document_type,
            "version": version, "uploaded_by": user_id, "uploaded_at": now(),
            "processing_status": "processing", "chunk_count": 0, "error": None,
        })
        try:
            raw_chunks = chunk_pages(extract_pages(content, extension))
            if not raw_chunks: raise ValueError("No readable text was found in this document")
            embeddings = await self.retrieval.embed([item["text"] for item in raw_chunks])
            chunks = []
            for index, item in enumerate(raw_chunks):
                chunks.append({**item, "project_id": project_id, "document_id": row["id"], "filename": original, "document_type": document_type, "version": version, "chunk_id": f"{row['id']}-c{index + 1}", "embedding": embeddings[index]})
            await self.repo.replace_chunks(row["id"], chunks)
            await self.repo.update(row["id"], {"processing_status": "processed", "chunk_count": len(chunks)})
            row.update({"processing_status": "processed", "chunk_count": len(chunks)})
            return row
        except Exception as exc:
            await self.repo.update(row["id"], {"processing_status": "failed", "error": str(exc)[:300]})
            raise HTTPException(status_code=422, detail=f"Document could not be processed: {str(exc)[:180]}")

    async def delete(self, project_id: str, document_id: str):
        row = await self.repo.get(document_id, project_id)
        if not row: raise not_found("Document")
        await self.repo.delete(document_id, project_id)
        path = safe_upload_path(self.settings.upload_dir, row["stored_name"])
        path.unlink(missing_ok=True)


class IntelligenceService:
    def __init__(self, db: AsyncIOMotorDatabase, settings: Settings):
        self.db, self.settings = db, settings
        self.findings = FindingRepository(db)
        self.retrieval = RetrievalService(db, settings)

    async def run_audit(self, project_id: str, user_id: str):
        chunks = [row async for row in self.db.chunks.find({"project_id": project_id}).limit(500)]
        if not chunks: raise HTTPException(status_code=400, detail="Upload and process at least one document first")
        run_id = uuid4().hex
        rows = audit_chunks(project_id, chunks)
        for row in rows: row.update({"run_id": run_id, "created_by": user_id})
        count = await self.findings.insert_many(rows)
        await self.db.audit_runs.insert_one({"run_id": run_id, "project_id": project_id, "created_by": user_id, "status": "completed", "findings_created": count, "created_at": now()})
        return {"run_id": run_id, "status": "completed", "findings_created": count, "message": "AI candidates are ready for human review." if count else "No candidate issues were detected by the current checks."}

    async def chat(self, project_id: str, user_id: str, question: str, thread_id: str | None, use_external: bool):
        thread_id = thread_id or uuid4().hex
        graph = build_chat_graph(self.retrieval)
        state = await graph.ainvoke({"project_id": project_id, "user_id": user_id, "question": question, "retrieval_query": question, "retry_count": 0, "errors": []})
        evidence_rows = state.get("retrieved_documents", [])
        answer = state["answer"]
        sources = await external_search(self.settings.tavily_api_key, question) if use_external else []
        evidence = [{key: row.get(key) for key in ("document_id", "filename", "chunk_id", "text", "page_number", "section", "score")} for row in evidence_rows]
        await self.db.chat_messages.insert_one({"thread_id": thread_id, "project_id": project_id, "user_id": user_id, "question": question, "answer": answer, "evidence": evidence, "created_at": now()})
        return {"answer": answer, "thread_id": thread_id, "grounded": state.get("grounded", False), "evidence": evidence, "external_sources": sources, "retrieval_query": state.get("retrieval_query", question)}

    async def compare_versions(self, project_id: str, left_id: str, right_id: str):
        left = [row async for row in self.db.chunks.find({"project_id": project_id, "document_id": left_id})]
        right = [row async for row in self.db.chunks.find({"project_id": project_id, "document_id": right_id})]
        if not left or not right: raise not_found("Processed document")
        matched_right: set[int] = set()
        changes = []
        for old in left:
            best_index, best_score = max(enumerate(right), key=lambda item: SequenceMatcher(None, old["text"], item[1]["text"]).ratio())
            score = SequenceMatcher(None, old["text"], right[best_index]["text"]).ratio()
            if score >= .55:
                matched_right.add(best_index)
                changes.append({"type": "unchanged" if score >= .94 else "modified", "similarity": round(score, 3), "before": old["text"], "after": right[best_index]["text"]})
            else: changes.append({"type": "removed", "similarity": round(score, 3), "before": old["text"], "after": None})
        for index, new in enumerate(right):
            if index not in matched_right: changes.append({"type": "added", "similarity": 0, "before": None, "after": new["text"]})
        summary = {kind: sum(1 for row in changes if row["type"] == kind) for kind in ("added", "removed", "modified", "unchanged")}
        return {"summary": summary, "changes": changes}

