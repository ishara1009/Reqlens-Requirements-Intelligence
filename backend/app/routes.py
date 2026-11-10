from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from app.core.config import Settings, get_settings
from app.db import get_database, get_database_backend
from app.dependencies import current_user
from app.repositories import DocumentRepository, FindingRepository, ProjectRepository, now
from app.schemas import (
    AuditResponse, AuthResponse, ChatRequest, ChatResponse, DashboardSummary,
    DocumentPublic, FindingPublic, LoginRequest, ProjectCreate, ProjectPublic,
    ProjectUpdate, RegisterRequest, RegistrationResponse, ReviewRequest, UserPublic,
)
from app.services import AuthService, DocumentService, IntelligenceService, ProjectService


router = APIRouter()


async def owned_project(project_id: str, user=Depends(current_user), db=Depends(get_database)):
    project = await ProjectService(db).get_required(project_id, user["id"])
    return project


@router.get("/health")
async def health(db=Depends(get_database), settings: Settings = Depends(get_settings)):
    await db.command("ping")
    return {"status": "healthy", "database": get_database_backend(), "ai_configured": settings.openai_ready}


@router.post("/auth/register", response_model=RegistrationResponse, status_code=201)
async def register(payload: RegisterRequest, db=Depends(get_database)):
    return await AuthService(db).register(payload.name, payload.email, payload.password)


@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db=Depends(get_database)):
    return await AuthService(db).login(payload.email, payload.password)


@router.get("/auth/me", response_model=UserPublic)
async def me(user=Depends(current_user)):
    return user


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(user=Depends(current_user), db=Depends(get_database)):
    project_ids = [str(row["_id"]) async for row in db.projects.find({"owner_id": user["id"]}, {"_id": 1})]
    scope = {"project_id": {"$in": project_ids}}
    return {
        "total_projects": len(project_ids),
        "total_documents": await db.documents.count_documents(scope),
        "processed_documents": await db.documents.count_documents({**scope, "processing_status": "processed"}),
        "total_findings": await db.findings.count_documents(scope),
        "pending_reviews": await db.findings.count_documents({**scope, "review_status": "pending"}),
    }


@router.get("/projects", response_model=list[ProjectPublic])
async def list_projects(user=Depends(current_user), db=Depends(get_database)):
    return await ProjectRepository(db).list(user["id"])


@router.post("/projects", response_model=ProjectPublic, status_code=201)
async def create_project(payload: ProjectCreate, user=Depends(current_user), db=Depends(get_database)):
    return await ProjectService(db).create(user["id"], payload.model_dump())


@router.get("/projects/{project_id}", response_model=ProjectPublic)
async def get_project(project=Depends(owned_project)):
    return project


@router.patch("/projects/{project_id}", response_model=ProjectPublic)
async def update_project(project_id: str, payload: ProjectUpdate, user=Depends(current_user), db=Depends(get_database)):
    await ProjectService(db).get_required(project_id, user["id"])
    return await ProjectRepository(db).update(project_id, user["id"], payload.model_dump(exclude_none=True))


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    user=Depends(current_user),
    db=Depends(get_database),
    settings: Settings = Depends(get_settings),
):
    await ProjectService(db).delete(project_id, user["id"], settings.upload_dir)


@router.get("/projects/{project_id}/documents", response_model=list[DocumentPublic])
async def list_documents(project=Depends(owned_project), db=Depends(get_database)):
    return await DocumentRepository(db).list(project["id"])


@router.post("/projects/{project_id}/documents", response_model=DocumentPublic, status_code=201)
async def upload_document(
    project_id: str,
    file: Annotated[UploadFile, File()],
    document_type: Annotated[str, Form()] = "Requirements",
    version: Annotated[str, Form()] = "1.0",
    user=Depends(current_user), db=Depends(get_database), settings: Settings = Depends(get_settings),
):
    await ProjectService(db).get_required(project_id, user["id"])
    return await DocumentService(db, settings).upload_and_process(project_id, user["id"], file, document_type, version)


@router.delete("/projects/{project_id}/documents/{document_id}", status_code=204)
async def delete_document(project_id: str, document_id: str, user=Depends(current_user), db=Depends(get_database), settings: Settings = Depends(get_settings)):
    await ProjectService(db).get_required(project_id, user["id"])
    await DocumentService(db, settings).delete(project_id, document_id)


@router.post("/projects/{project_id}/audit", response_model=AuditResponse)
async def run_audit(project_id: str, user=Depends(current_user), db=Depends(get_database), settings: Settings = Depends(get_settings)):
    await ProjectService(db).get_required(project_id, user["id"])
    return await IntelligenceService(db, settings).run_audit(project_id, user["id"])


@router.get("/projects/{project_id}/findings", response_model=list[FindingPublic])
async def list_findings(project=Depends(owned_project), review_status: str | None = Query(default=None), db=Depends(get_database)):
    return await FindingRepository(db).list(project["id"], review_status)


@router.patch("/projects/{project_id}/findings/{finding_id}/review", response_model=FindingPublic)
async def review_finding(project_id: str, finding_id: str, payload: ReviewRequest, user=Depends(current_user), db=Depends(get_database)):
    await ProjectService(db).get_required(project_id, user["id"])
    finding = await FindingRepository(db).review(finding_id, project_id, user["id"], payload.status.value, payload.comment)
    if not finding: raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/projects/{project_id}/chat", response_model=ChatResponse)
async def chat(project_id: str, payload: ChatRequest, user=Depends(current_user), db=Depends(get_database), settings: Settings = Depends(get_settings)):
    await ProjectService(db).get_required(project_id, user["id"])
    return await IntelligenceService(db, settings).chat(project_id, user["id"], payload.question, payload.thread_id, payload.external_search)


@router.get("/projects/{project_id}/compare")
async def compare(project_id: str, left_document_id: str, right_document_id: str, user=Depends(current_user), db=Depends(get_database), settings: Settings = Depends(get_settings)):
    await ProjectService(db).get_required(project_id, user["id"])
    return await IntelligenceService(db, settings).compare_versions(project_id, left_document_id, right_document_id)


@router.get("/projects/{project_id}/report")
async def report(project=Depends(owned_project), db=Depends(get_database)):
    findings = await FindingRepository(db).list(project["id"])
    documents = await DocumentRepository(db).list(project["id"])
    by_status = {key: sum(1 for row in findings if row["review_status"] == key) for key in ("pending", "approved", "rejected", "needs_more_evidence")}
    return {"generated_at": now(), "project": project, "summary": {"documents": len(documents), "findings": len(findings), **by_status}, "documents": documents, "findings": findings, "notice": "AI findings are candidates until approved by a human reviewer."}

