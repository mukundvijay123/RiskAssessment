from fastapi import APIRouter, Depends, Query,HTTPException
from sqlalchemy.orm import Session,joinedload
from .db import get_db  # Adjust the import based on your project
from .tables import EntRisk, ThreatRisk 
from .models import AssessmentSummaryRequest
from typing import List
from uuid import UUID
import requests


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





@dashboardrouter.get("/summary")
def get_dashboard_kpis(
    orgId: str = Query("*"),
    assessment_types: List[str] = Query(...),
    db: Session = Depends(get_db)
):
    # Validate orgId
    if orgId == "*":
        raise HTTPException(status_code=400, detail="Organization ID is required.")
    
    try:
        organization_id = UUID(orgId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid organization ID format")

    # Fetch context
    eraCtx = None
    traCtx = None
    SummaryCtx = {}

    if "era" in assessment_types:
        eraCtx = db.query(EntRisk).options(joinedload(EntRisk.threats)).filter(EntRisk.organization_id == organization_id).all()
        SummaryCtx["EnterpriseRiskAssessment"] = str(eraCtx) if eraCtx else "No info"

    if "tra" in assessment_types:
        traCtx = db.query(ThreatRisk).filter(ThreatRisk.organization_id == organization_id).all()
        SummaryCtx["threatRiskAssessment"] = str(traCtx) if traCtx else "No info"

    # Construct request model with updated context
    request_model = AssessmentSummaryRequest(
        organization_id=organization_id,
        assessment_types=assessment_types,
        organization_context=str(SummaryCtx)
    )

    # Prepare payload (remove organization_id)
    payload = request_model.dict()
    payload.pop("organization_id")

    # Send POST request to external API
    try:
        response = requests.post(
            "https://ey-catalyst-rvce-ey-catalyst.hf.space/dashboard/api/dashboard/generate-kpis",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error calling external KPI generator: {str(e)}")