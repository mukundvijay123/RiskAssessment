from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .db import get_db  # Adjust the import based on your project
from .tables import EntRisk, ThreatRisk 


dashboardrouter = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@dashboardrouter.get("/kpis")
def get_dashboard_kpis(orgId: str = Query("*"), db: Session = Depends(get_db)):
    if orgId == "*":
        total_risks = db.query(EntRisk).count()
        total_threats = db.query(ThreatRisk).count()
        critical_risks = db.query(EntRisk).filter(EntRisk.impact >= 7).count()
        departments = db.query(EntRisk.department).distinct().count()
    else:
        total_risks = db.query(EntRisk).filter(EntRisk.organization_id == orgId).count()
        total_threats = db.query(ThreatRisk).filter(ThreatRisk.organization_id == orgId).count()
        critical_risks = db.query(EntRisk).filter(
            EntRisk.organization_id == orgId, EntRisk.impact >= 7
        ).count()
        departments = db.query(EntRisk.department).filter(
            EntRisk.organization_id == orgId
        ).distinct().count()

    return {
        "totalRisks": total_risks,
        "totalThreats": total_threats,
        "criticalRisks": critical_risks,
        "departments": departments,
    }


