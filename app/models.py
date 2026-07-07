import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from sqlalchemy import Boolean as Bool
from sqlalchemy import UniqueConstraint


def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="student", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    jti: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    replaced_by_jti: Mapped[str] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    problem_title: Mapped[str] = mapped_column(String(255), nullable=True)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    review: Mapped["ReviewResult"] = relationship(back_populates="submission", uselist=False, cascade="all, delete-orphan")


class ReviewResult(Base):
    __tablename__ = "review_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_submissions.id", ondelete="CASCADE"), unique=True, nullable=False)

    time_complexity: Mapped[str] = mapped_column(String(50), nullable=True)
    space_complexity: Mapped[str] = mapped_column(String(50), nullable=True)
    concepts: Mapped[list] = mapped_column(JSON, default=list)          # e.g. ["sliding window", "two pointers"]
    suggestions: Mapped[list] = mapped_column(JSON, default=list)       # list of {issue, why, fix}
    better_approach: Mapped[str] = mapped_column(Text, nullable=True)   # tourist-style narrative
    score: Mapped[int] = mapped_column(Integer, nullable=True)          # 0-100 code quality score
    raw_heuristics: Mapped[dict] = mapped_column(JSON, default=dict)    # what Tree-sitter found
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    submission: Mapped["CodeSubmission"] = relationship(back_populates="review")

class Contest(Base):
    __tablename__ = "contests"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)          # "codeforces" | "leetcode"
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)      # platform's own contest id/slug
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Put your table arguments here cleanly at the bottom
    __table_args__ = (
        UniqueConstraint("platform", "external_id", name="uq_platform_external_id"),
    )


class ContestTrack(Base):
    __tablename__ = "contest_tracks"
    __table_args__ = (UniqueConstraint("user_id", "contest_id", name="uq_user_contest"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    contest_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ConceptTag(Base):
    """Canonical concept taxonomy — the normalization layer."""
    __tablename__ = "concept_tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # e.g. "sliding_window"
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)                  # e.g. "Sliding Window"
    aliases: Mapped[list] = mapped_column(JSON, default=list)  # e.g. ["sliding window technique", "window sliding"]


class SubmissionConcept(Base):
    """Link table: which canonical concepts were flagged on which submission,
    and whether it was flagged as a WEAKNESS (via suggestions) vs just USED (via concepts)."""
    __tablename__ = "submission_concepts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_submissions.id", ondelete="CASCADE"), nullable=False)
    concept_tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("concept_tags.id"), nullable=False)
    was_flagged_as_gap: Mapped[bool] = mapped_column(Boolean, default=False)  # True if it came from `suggestions`, not just `concepts`
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WeaknessRecord(Base):
    """Aggregated per-user, per-concept weakness state. Updated after each review."""
    __tablename__ = "weakness_records"
    __table_args__ = (UniqueConstraint("user_id", "concept_tag_id", name="uq_user_concept"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    concept_tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("concept_tags.id"), nullable=False)
    gap_count: Mapped[int] = mapped_column(Integer, default=0)          # times flagged as a gap
    last_flagged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_resurfaced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active_weakness: Mapped[bool] = mapped_column(Boolean, default=False)  # crosses recurrence threshold
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)