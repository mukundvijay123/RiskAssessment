from fastapi import APIRouter, Depends,Query,HTTPException,status
from .db import get_db
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from .models import OutdatedBIAProcess,NotificationResponse

NotificationRouter = APIRouter(prefix="/api/notifications")

@NotificationRouter.get("/continious-improvement", response_model=NotificationResponse)
def get_bcm_structure(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    # Step 1: Get organization ID
    org_query = text("""
        SELECT id FROM organization
        WHERE bcm_coordinator_user_id = :user_id
        LIMIT 1
    """)
    org_result = db.execute(org_query, {"user_id": str(user_id)}).fetchone()

    if org_result is None:
        return {
            "notifications": False,
            "notificationList": []
        }

    org_id = org_result["id"]

    # Step 2: Get outdated BIA processes
    bia_query = text("""
        SELECT p.name AS process_name, bpi.updated_at
        FROM organization o
        JOIN department d ON d.organization_id = o.id
        JOIN subdepartment sd ON sd.department_id = d.id
        JOIN process p ON p.subdepartment_id = sd.id
        JOIN bia_process_info bpi ON bpi.process_id = p.id
        WHERE o.id = :org_id
          AND bpi.updated_at < NOW() - INTERVAL '6 months'
    """)
    bia_results = db.execute(bia_query, {"org_id": str(org_id)}).fetchall()

    outdated_list = [
        OutdatedBIAProcess(process_name=row["process_name"], updated_at=row["updated_at"])
        for row in bia_results
    ]

    return {
        "notifications": True,
        "notificationList": outdated_list
    }