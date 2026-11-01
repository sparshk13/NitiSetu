import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Integer, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

# Helper to provide cross-database compatible UUID and JSON types
GUID = UUID(as_uuid=True)
JSONType = JSONB().with_variant(JSON(), "sqlite")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    marital_status = Column(String(50), nullable=True)
    state_code = Column(String(50), nullable=True)
    district = Column(String(100), nullable=True)
    area_type = Column(String(50), default="Rural", nullable=True)
    occupation = Column(String(100), nullable=True)
    annual_family_income = Column(Numeric(12, 2), nullable=True)
    ration_card_type = Column(String(50), nullable=True)
    caste_category = Column(String(50), nullable=True)
    is_minority_community = Column(Boolean, default=False)
    is_differently_abled = Column(Boolean, default=False)
    is_landowner = Column(Boolean, default=False)
    land_holding_acres = Column(Numeric(10, 2), nullable=True)
    has_bank_account = Column(Boolean, default=True)
    is_bank_aadhaar_seeded = Column(Boolean, default=True)
    highest_qualification = Column(String(100), nullable=True)
    is_student_currently = Column(Boolean, default=False)
    education_level = Column(String(100), nullable=True)
    course = Column(String(255), nullable=True)
    study_year = Column(Integer, nullable=True)
    institution_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    scheme_type = Column(String(100), default="scholarship", nullable=False)
    state_code = Column(String(50), nullable=True)
    central_or_state = Column(String(50), default="Central Government", nullable=False)
    benefit_summary = Column(Text, nullable=True)
    official_url = Column(String(1000), nullable=False)
    application_url = Column(String(1000), nullable=True)
    deadline = Column(String(50), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    last_verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    rules = relationship("SchemeRule", back_populates="scheme", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="scheme", cascade="all, delete-orphan")


class SchemeRule(Base):
    __tablename__ = "scheme_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_key = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)  # 'eq', 'neq', 'lt', 'lte', 'gt', 'gte', 'in'
    expected_value = Column(JSONType, nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    source_section = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scheme = relationship("Scheme", back_populates="rules")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    source_url = Column(String(1000), nullable=True)
    storage_path = Column(String(500), nullable=True)
    document_type = Column(String(100), default="guideline", nullable=False)
    last_verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    content_hash = Column(String(128), nullable=True)
    processing_status = Column(String(50), default="completed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chunks = relationship("DocumentChunk", back_populates="source_document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_document_id = Column(String(36), ForeignKey("source_documents.id", ondelete="CASCADE"), nullable=False)
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    section_title = Column(String(255), nullable=True)
    # Stored as JSON array or pgvector in PostgreSQL
    embedding_json = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_document = relationship("SourceDocument", back_populates="chunks")
    scheme = relationship("Scheme", back_populates="chunks")


class UserDocument(Base):
    __tablename__ = "user_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    detected_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=False)
    processing_status = Column(String(50), default="pending", nullable=False)
    extracted_fields = Column(JSONType, nullable=True)
    user_confirmed_fields = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ApplicationDraft(Base):
    __tablename__ = "application_drafts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="draft", nullable=False)
    form_data = Column(JSONType, default=dict, nullable=False)
    automation_log = Column(JSONType, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

