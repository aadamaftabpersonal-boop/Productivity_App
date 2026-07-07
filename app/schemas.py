import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: str
    created_at: datetime

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class CodeReviewRequest(BaseModel):
    language: str  # "python" | "cpp" | "java"
    code: str
    problem_title: str | None = None
    problem_statement: str | None = None

class SuggestionItem(BaseModel):
    issue: str
    why: str
    fix: str

class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    time_complexity: str | None
    space_complexity: str | None
    concepts: list[str]
    suggestions: list[dict]
    better_approach: str | None
    score: int | None
    created_at: datetime

class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    language: str
    problem_title: str | None
    created_at: datetime
    review: ReviewOut | None