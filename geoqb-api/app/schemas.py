"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


# ============================================================================
# Authentication Schemas
# ============================================================================

class UserSignup(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str


class UserResponse(UserBase):
    """User response schema."""
    id: str
    plan: str
    status: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# ============================================================================
# Workspace Schemas
# ============================================================================

class WorkspaceCreate(BaseModel):
    """Workspace creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    """Workspace update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    tigergraph_graphname: Optional[str]
    created_at: datetime
    updated_at: datetime
    layer_count: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# Layer Schemas
# ============================================================================

class LayerCreate(BaseModel):
    """Layer creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    layer_type: str = Field(..., min_length=1, max_length=100)
    tags: Dict[str, str] = Field(..., min_items=1)
    bbox: List[float] = Field(..., min_items=4, max_items=4)
    resolution: int = Field(default=9, ge=0, le=15)

    @validator('bbox')
    def validate_bbox(cls, v):
        """Validate bounding box coordinates."""
        if len(v) != 4:
            raise ValueError('bbox must have exactly 4 coordinates [lat_min, lon_min, lat_max, lon_max]')
        lat_min, lon_min, lat_max, lon_max = v
        if not (-90 <= lat_min < lat_max <= 90):
            raise ValueError('Invalid latitude range')
        if not (-180 <= lon_min < lon_max <= 180):
            raise ValueError('Invalid longitude range')
        return v


class LayerUpdate(BaseModel):
    """Layer update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tags: Optional[Dict[str, str]] = None
    bbox: Optional[List[float]] = None
    resolution: Optional[int] = Field(None, ge=0, le=15)


class LayerResponse(BaseModel):
    """Layer response schema."""
    id: str
    workspace_id: str
    name: str
    layer_type: str
    tags: Dict[str, Any]
    bbox: List[float]
    resolution: int
    status: str
    error_message: Optional[str]
    feature_count: int
    ingestion_started_at: Optional[datetime]
    ingestion_completed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Usage Schemas
# ============================================================================

class UsageStats(BaseModel):
    """Usage statistics response."""
    user_id: str
    plan: str
    current_period_start: datetime
    current_period_end: datetime
    layers_created: int
    layers_limit: int
    queries_executed: int
    queries_limit: int
    is_over_quota: bool


class UsageEventCreate(BaseModel):
    """Usage event creation."""
    event_type: str
    resource_id: Optional[str] = None
    quantity: int = 1
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Analysis Schemas
# ============================================================================

class AnalysisRequest(BaseModel):
    """Analysis request schema."""
    layer_ids: List[str] = Field(..., min_items=1)
    analysis_type: str = Field(..., pattern="^(accessibility|clustering|shortest_path|network)$")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Analysis response schema."""
    analysis_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
