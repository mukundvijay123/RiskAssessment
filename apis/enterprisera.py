from fastapi import APIRouter, Depends, Query,HTTPException,Path
import requests
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import distinct
from .db import get_db
from typing import List,Dict
from .tables import EntRisk,EntThreat  # SQLAlchemy ORM model
from .models import EntRiskModel,EntRiskUpdate,EntRiskGenerationRequest ,EntRiskAssessmentRequest,EntRiskGenerationResponse ,EntRiskEscalationRequest# Pydantic model

enterpriserouter = APIRouter(prefix="/enterpriseRiskAssessment")


@enterpriserouter.post("/generateRisks")
def generate_risks(request: EntRiskAssessmentRequest, db: Session = Depends(get_db)):
    # Convert to generation request
    risk_gen_req = EntRiskGenerationRequest(
        category=request.category,
        department=request.department,
        business_context=request.business_context or "N/A",
        specific_concerns=request.specific_concerns or "N/A",
        number_of_risks=request.number_of_risks or 5
    )

    try:
        # External API call to generate risks
        response = requests.post(
            "https://ey-catalyst-rvce-ey-catalyst.hf.space/enterprise/api/enterprise-ra/generate-risks",
            json=risk_gen_req.model_dump()
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or "risks" not in data:
            raise HTTPException(status_code=500, detail="Invalid risk generation response")

        generated_risks = []

        for risk_item in data["risks"]:
            # Create and save EntRisk
            db_risk = EntRisk(
                organization_id=request.organization_id,
                category=request.category,
                name=risk_item["name"],
                description=risk_item["description"],
                likelihood=risk_item["likelihood"],
                impact=risk_item["impact"],
                likelihood_justification=risk_item["likelihood_justification"],
                impact_justification=risk_item["impact_justification"],
                treatment=risk_item["treatment"],
                department=request.department,
                escalated=False
            )
            db.add(db_risk)
            db.flush()  # get the ID

            # Create and save EntThreats
            for threat_item in risk_item.get("threats", []):
                db_threat = EntThreat(
                    risk_id=db_risk.id,
                    name=threat_item["name"],
                    description=threat_item["description"],
                    justification=threat_item["justification"]
                )
                db.add(db_threat)

            db.refresh(db_risk)  # load threats via relationship
            generated_risks.append(EntRiskModel.model_validate(db_risk))

        db.commit()

        return EntRiskGenerationResponse(
            success=True,
            risks=generated_risks,
            message=f"Successfully generated and saved {len(generated_risks)} risks"
        )

    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")



@enterpriserouter.get("/getRisks", response_model=List[EntRiskModel])
def get_risks(orgId: str = Query(...), db: Session = Depends(get_db)):
    if orgId == "*":
        risks = db.query(EntRisk).options(joinedload(EntRisk.threats)).all()
    else:
        risks = db.query(EntRisk).options(joinedload(EntRisk.threats)).filter(EntRisk.organization_id == orgId).all()

    return risks  # FastAPI auto-converts using `from_orm`





@enterpriserouter.put("/{riskId}", response_model=Dict[str, object])
def update_risk(
    riskId: int = Path(..., description="ID of the risk to update"),
    update_data: EntRiskUpdate = ...,
    db: Session = Depends(get_db)
):
    # 1. Fetch the risk
    risk = db.query(EntRisk).filter(EntRisk.id == riskId).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    # 2. Apply only fields that are present in request
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(risk, key, value)

    # 3. Commit the update
    try:
        db.commit()
        db.refresh(risk)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")

    # 4. Return response
    return {
        "success": True,
        "risk": EntRiskModel.from_orm(risk)
    }




@enterpriserouter.post("/api/risks/{risk_id}/escalate")
def escalate_risk(
    risk_id: int,
    request: EntRiskEscalationRequest,
    db: Session = Depends(get_db)
):
    risk = db.query(EntRisk).filter(EntRisk.id == risk_id).first()

    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    risk.escalated = request.escalated
    db.commit()
    db.refresh(risk)

    return {
        "success": True,
        "risk": {
            "id": risk.id,
            "organization_id": str(risk.organization_id),
            "category": risk.category,
            "name": risk.name,
            "description": risk.description,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "likelihood_justification": risk.likelihood_justification,
            "impact_justification": risk.impact_justification,
            "treatment": risk.treatment,
            "department": risk.department,
            "escalated": risk.escalated,
            "threats": [
                {
                    "name": threat.name,
                    "description": threat.description,
                    "justification": threat.justification
                } for threat in risk.threats
            ]
        }
    }


@enterpriserouter.get("/api/threats")
def get_unique_threats(orgId: UUID = Query(...), db: Session = Depends(get_db)):
    threats = (
        db.query(distinct(EntThreat.name))
        .join(EntRisk, EntRisk.id == EntThreat.risk_id)
        .filter(EntRisk.organization_id == orgId)
        .all()
    )
    return [{"name": name[0]} for name in threats]