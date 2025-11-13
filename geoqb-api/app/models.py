"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, JSON, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserPlan(str, enum.Enum):
    """User subscription plans."""
    FREE = "free"
    PROFESSIONAL = "professional"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class LayerStatus(str, enum.Enum):
    """Layer processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    plan = Column(SQLEnum(UserPlan), default=UserPlan.FREE, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)

    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    workspaces = relationship("Workspace", back_populates="owner", cascade="all, delete-orphan")
    usage_events = relationship("UsageEvent", back_populates="user", cascade="all, delete-orphan")


class Workspace(Base):
    """Workspace model for organizing layers."""
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    tigergraph_graphname = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="workspaces")
    layers = relationship("Layer", back_populates="workspace", cascade="all, delete-orphan")


class Layer(Base):
    """Layer definition model."""
    __tablename__ = "layers"

    id = Column(String(36), primary_key=True, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    layer_type = Column(String(100), nullable=False)  # amenity, building, highway, etc.

    tags = Column(JSON, nullable=False)  # OSM tags as JSON
    bbox = Column(JSON, nullable=False)  # [lat_min, lon_min, lat_max, lon_max]
    resolution = Column(Integer, default=9, nullable=False)  # H3 resolution

    status = Column(SQLEnum(LayerStatus), default=LayerStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)

    feature_count = Column(Integer, default=0)
    ingestion_started_at = Column(DateTime, nullable=True)
    ingestion_completed_at = Column(DateTime, nullable=True)

    metadata = Column(JSON, nullable=True)  # Additional metadata

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="layers")


class UsageEvent(Base):
    """Usage tracking for billing and quotas."""
    __tablename__ = "usage_events"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    event_type = Column(String(100), nullable=False)  # layer_created, query_executed, etc.
    resource_id = Column(String(255), nullable=True)  # Layer ID, workspace ID, etc.

    quantity = Column(Integer, default=1, nullable=False)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_events")


class APIKey(Base):
    """API keys for programmatic access."""
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
