from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class UserPublic(ApiModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class RegisterRequest(ApiModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(ApiModel):
    email: EmailStr
    password: str


class AuthResponse(ApiModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class RegistrationResponse(ApiModel):
    message: str
    user: UserPublic


class ProjectStatus(str, Enum):
    active = "active"
    archived = "archived"


class ProjectCreate(ApiModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    domain: str = Field(default="General", max_length=80)


class ProjectUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    domain: str | None = Field(default=None, max_length=80)
    status: ProjectStatus | None = None


class ProjectPublic(ProjectCreate):
    id: str
    status: ProjectStatus
    owner_id: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    finding_count: int = 0


class ProcessingStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class DocumentPublic(ApiModel):
    id: str
    project_id: str
    filename: str
    file_type: str
    document_type: str
    version: str
    processing_status: ProcessingStatus
    uploaded_at: datetime
    chunk_count: int = 0
    error: str | None = None


class Evidence(ApiModel):
    document_id: str
    filename: str
    chunk_id: str
    text: str
    page_number: int | None = None
    section: str | None = None
    score: float | None = None


class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    needs_more_evidence = "needs_more_evidence"


class FindingPublic(ApiModel):
    id: str
    project_id: str
    issue_type: str
    title: str
    explanation: str
    confidence: float
    grounded: bool
    review_status: ReviewStatus
    evidence: list[Evidence]
    created_at: datetime
    reviewed_at: datetime | None = None
    review_comment: str | None = None


class ReviewRequest(ApiModel):
    status: ReviewStatus
    comment: str = Field(default="", max_length=1000)


class ChatRequest(ApiModel):
    question: str = Field(min_length=2, max_length=2000)
    thread_id: str | None = None
    external_search: bool = False


class ExternalSource(ApiModel):
    title: str
    url: str
    content: str


class ChatResponse(ApiModel):
    answer: str
    thread_id: str
    grounded: bool
    evidence: list[Evidence]
    external_sources: list[ExternalSource] = []
    retrieval_query: str


class AuditResponse(ApiModel):
    run_id: str
    status: str
    findings_created: int
    message: str


class DashboardSummary(ApiModel):
    total_projects: int
    total_documents: int
    processed_documents: int
    total_findings: int
    pending_reviews: int

