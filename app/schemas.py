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
    domain: str = "cp"  # "cp" | "ml" | "swe"
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
    measured_complexity: str | None = None
    complexity_disagreement: bool = False
    complexity_warning: str | None = None
    concepts: list[str]
    suggestions: list[dict]
    better_approach: str | None
    score: int | None
    created_at: datetime

class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    language: str
    domain: str = "cp"
    problem_title: str | None
    created_at: datetime
    review: ReviewOut | None


class ContestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    platform: str
    name: str
    start_time: datetime
    duration_seconds: int
    url: str
    is_finished: bool

class TrackContestRequest(BaseModel):
    contest_id: uuid.UUID

class ActiveWeaknessOut(BaseModel):
    concept: str
    canonical_name: str = ""
    gap_count: int
    last_flagged_at: datetime | None
    recommended_problems: list[dict] = []


class ResurfaceOut(BaseModel):
    mode: str
    concept: str
    problem_title: str | None = None
    url: str | None = None
    submission_id: str | None = None
    instruction: str

class DashboardOut(BaseModel):
    user: UserOut
    recent_submissions: list[SubmissionOut]
    active_weaknesses: list[ActiveWeaknessOut]
    resurface_item: ResurfaceOut | None
    upcoming_contests: list[ContestOut]
    tracked_contests: list[ContestOut]