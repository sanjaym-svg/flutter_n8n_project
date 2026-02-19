from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeOut(BaseModel):
    id: int
    original_filename: str
    storage_url: str
    extracted_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobFilters(BaseModel):
    role_keywords: list[str] = []
    location: str | None = None
    remoteOnly: bool = False
    postedWithinHours: int = 72


class JobsSyncRequest(BaseModel):
    filters: JobFilters


class JobOut(BaseModel):
    id: int
    provider: str
    title: str
    company: str
    location: str
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    remote_type: str | None
    description: str
    apply_url: str
    posted_at: datetime | None
    fetched_at: datetime

    class Config:
        from_attributes = True


class PaginatedJobs(BaseModel):
    items: list[JobOut]
    page: int
    total: int


class TailorResponse(BaseModel):
    tailored_resume_text: str
    ats_score: int
    matched_keywords: list[str]
    missing_keywords: list[str]


class TailoredResumeOut(BaseModel):
    id: int
    tailored_text: str
    ats_score: int
    matched_keywords: list[str]
    missing_keywords: list[str]
    created_at: datetime


class MessageOut(BaseModel):
    detail: str


class SyncResult(BaseModel):
    inserted_or_updated: int
    providers: dict[str, Any]
