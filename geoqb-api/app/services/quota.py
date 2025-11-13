"""Usage quota management."""
from typing import Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Layer, UsageEvent, UserPlan
from app.config import get_settings

settings = get_settings()


def check_layer_quota(db: Session, user: User) -> Tuple[bool, str]:
    """
    Check if user can create more layers based on their plan.

    Args:
        db: Database session
        user: User object

    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Get user's layer count
    layer_count = db.query(func.count(Layer.id)).join(
        Layer.workspace
    ).filter(
        Layer.workspace.has(user_id=user.id)
    ).scalar()

    # Get plan limits
    if user.plan == UserPlan.FREE:
        limit = settings.FREE_PLAN_LAYER_LIMIT
    elif user.plan == UserPlan.PROFESSIONAL:
        limit = settings.PROFESSIONAL_PLAN_LAYER_LIMIT
    elif user.plan == UserPlan.BUSINESS:
        limit = settings.BUSINESS_PLAN_LAYER_LIMIT
    else:  # Enterprise
        return True, ""  # No limit for enterprise

    if layer_count >= limit:
        return False, f"Layer limit reached ({layer_count}/{limit}). Upgrade your plan to create more layers."

    return True, ""


def check_query_quota(db: Session, user: User) -> Tuple[bool, str]:
    """
    Check if user can execute more queries based on their plan.

    Args:
        db: Database session
        user: User object

    Returns:
        Tuple of (is_allowed, error_message)
    """
    # Get current billing period (monthly)
    now = datetime.utcnow()
    period_start = datetime(now.year, now.month, 1)
    period_end = (period_start + timedelta(days=32)).replace(day=1)

    # Count queries in current period
    query_count = db.query(func.count(UsageEvent.id)).filter(
        UsageEvent.user_id == user.id,
        UsageEvent.event_type == "query_executed",
        UsageEvent.created_at >= period_start,
        UsageEvent.created_at < period_end
    ).scalar()

    # Get plan limits
    if user.plan == UserPlan.FREE:
        limit = settings.FREE_PLAN_QUERY_LIMIT
    elif user.plan == UserPlan.PROFESSIONAL:
        limit = settings.PROFESSIONAL_PLAN_QUERY_LIMIT
    elif user.plan == UserPlan.BUSINESS:
        limit = settings.BUSINESS_PLAN_QUERY_LIMIT
    else:  # Enterprise
        return True, ""  # No limit for enterprise

    if query_count >= limit:
        return False, f"Query limit reached ({query_count}/{limit} this month). Upgrade your plan to execute more queries."

    return True, ""


def get_usage_stats(db: Session, user: User) -> dict:
    """
    Get user's usage statistics for current billing period.

    Args:
        db: Database session
        user: User object

    Returns:
        Dictionary with usage stats
    """
    # Get current billing period
    now = datetime.utcnow()
    period_start = datetime(now.year, now.month, 1)
    period_end = (period_start + timedelta(days=32)).replace(day=1)

    # Layer count
    layer_count = db.query(func.count(Layer.id)).join(
        Layer.workspace
    ).filter(
        Layer.workspace.has(user_id=user.id)
    ).scalar()

    # Query count for period
    query_count = db.query(func.count(UsageEvent.id)).filter(
        UsageEvent.user_id == user.id,
        UsageEvent.event_type == "query_executed",
        UsageEvent.created_at >= period_start,
        UsageEvent.created_at < period_end
    ).scalar()

    # Get limits
    if user.plan == UserPlan.FREE:
        layer_limit = settings.FREE_PLAN_LAYER_LIMIT
        query_limit = settings.FREE_PLAN_QUERY_LIMIT
    elif user.plan == UserPlan.PROFESSIONAL:
        layer_limit = settings.PROFESSIONAL_PLAN_LAYER_LIMIT
        query_limit = settings.PROFESSIONAL_PLAN_QUERY_LIMIT
    elif user.plan == UserPlan.BUSINESS:
        layer_limit = settings.BUSINESS_PLAN_LAYER_LIMIT
        query_limit = settings.BUSINESS_PLAN_QUERY_LIMIT
    else:  # Enterprise
        layer_limit = 999999
        query_limit = 999999

    return {
        "user_id": user.id,
        "plan": user.plan.value,
        "current_period_start": period_start,
        "current_period_end": period_end,
        "layers_created": layer_count,
        "layers_limit": layer_limit,
        "queries_executed": query_count,
        "queries_limit": query_limit,
        "is_over_quota": layer_count >= layer_limit or query_count >= query_limit
    }
