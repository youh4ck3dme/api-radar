"""
Dashboard module for API Centrum
Provides endpoints for dashboard data and statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import get_db
from .models import User, AuditLog
from .auth_neon import get_current_user_or_neon
from .auth import verify_password
from .websupport import WebsupportService
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

router = APIRouter()

class DashboardStats:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user-specific statistics"""
        # Count total domains (would need to track in local DB or fetch from Websupport)
        total_domains = 0  # This would be calculated from actual data
        
        # Count recent activities
        recent_activities = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
        ).count()
        
        # Get last login (simplified)
        user = self.db.query(User).filter(User.id == user_id).first()
        
        return {
            "total_domains": total_domains,
            "recent_activities": recent_activities,
            "last_login": user.created_at if user else None,
            "account_type": "neon_auth" if user and verify_password("neon_auth_temp", user.hashed_password) else "local"
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        # Check Websupport API connectivity
        websupport_status = "unknown"
        try:
            # Simple connectivity check
            WebsupportService.get_user_info()
            websupport_status = "online"
        except Exception:
            websupport_status = "offline"
        
        # Check database connectivity
        db_status = "unknown"
        try:
            self.db.execute(text("SELECT 1")).scalar()
            db_status = "online"
        except Exception:
            db_status = "offline"
        
        # Check Neon Auth trial status
        from .neon_auth import is_neon_trial_active
        neon_status = "active" if is_neon_trial_active() else "inactive"
        
        return {
            "websupport_api": websupport_status,
            "database": db_status,
            "neon_auth_trial": neon_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_recent_activities(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activities for user"""
        activities = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return [
            {
                "action": activity.action,
                "detail": activity.detail,
                "timestamp": activity.created_at.isoformat()
            }
            for activity in activities
        ]

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_or_neon),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    try:
        stats = DashboardStats(db)
        user_stats = stats.get_user_stats(current_user.id)
        system_health = stats.get_system_health()
        
        return {
            "user_stats": user_stats,
            "system_health": system_health,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/dashboard/activities")
async def get_recent_activities(
    current_user: User = Depends(get_current_user_or_neon),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get recent activities for current user"""
    try:
        stats = DashboardStats(db)
        activities = stats.get_recent_activities(current_user.id, limit)
        
        return {
            "activities": activities,
            "count": len(activities)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent activities: {str(e)}")

@router.get("/dashboard/health")
async def get_system_health(
    db: Session = Depends(get_db)
):
    """Get system health status (public endpoint)"""
    try:
        stats = DashboardStats(db)
        health = stats.get_system_health()
        
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")