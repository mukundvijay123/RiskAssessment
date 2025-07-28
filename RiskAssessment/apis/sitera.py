from fastapi import APIRouter,HTTPException,Depends
import json
import os
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from typing import List
from .models import RiskRequestModel,SiteRiskSafetyInput,GeneratedRiskOutput
from .db import get_db
from .tables import SiteRiskAssessment,SiteRiskMitigation
import requests
siterouter = APIRouter(prefix="/siteRiskAssessment")

@siterouter.get("/questions")
def get_questions():
    file_path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(file_path, "r") as f:
            questions = json.load(f)
        return JSONResponse(content={"questions": questions})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@siterouter.post("/riskMitigation")
def generate_risk_mitigation(risk_items: RiskRequestModel, db: Session = Depends(get_db)):
    if risk_items.organization_id is None and risk_items.demo:
        # Case: demo — send to external API and save with random UUID
        payload = risk_items.model_dump(by_alias=True, exclude={"organization_id", "demo"})

        try:
            response = requests.post(
                "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/risk-mitigation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"External API failed: {str(e)}")
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON from mitigation API")

        

        return response_data

    elif not risk_items.demo and risk_items.organization_id:
        # Case: real request — try DB first
        record = db.query(SiteRiskMitigation).filter(
            SiteRiskMitigation.org_id == risk_items.organization_id
        ).first()

        if record:
            return record.data

        # Not found, call API
        payload = risk_items.model_dump(by_alias=True, exclude={"demo"})
        try:
            response = requests.post(
                "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/risk-mitigation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"External API failed: {str(e)}")
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON from mitigation API")

        # Save to DB
        new_record = SiteRiskMitigation(
            org_id=risk_items.organization_id,
            data=response_data
        )
        db.add(new_record)
        db.commit()

        return response_data

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid input. Use demo=True without organization_id or demo=False with valid organization_id."
        )




@siterouter.post("/site-risk-assessment")
def do_sam(input: SiteRiskSafetyInput, db: Session = Depends(get_db)):
    """
    Handles site risk assessment:
    - If demo=True and organization_id is None:
        Send to external API (exclude org_id/demo), save to DB with random UUID, return result
    - If demo=False and organization_id is provided:
        Check DB → if not found, send to API, save to DB, return
    """
    if input.organization_id is None and input.demo:
        # Case: demo with no org_id — call API, save, return
        payload = input.model_dump(by_alias=True, exclude={"demo", "organization_id"})

        try:
            response = requests.post(
                "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/site-risk-mitigation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Error connecting to mitigation API: {str(e)}")
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON received from external API")

       
        

        return response_data

    elif not input.demo and input.organization_id:
        # Case: real org request — try DB first
        record = db.query(SiteRiskAssessment).filter(SiteRiskAssessment.org_id == input.organization_id).first()
        if record:
            return record.data

        # Not found — call API, save, return
        payload = input.model_dump(by_alias=True, exclude={"demo"})
        try:
            response = requests.post(
                "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/site-risk-mitigation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Error connecting to mitigation API: {str(e)}")
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON received from external API")

        # Save to DB
        new_record = SiteRiskAssessment(
            org_id=input.organization_id,
            data=response_data
        )
        db.add(new_record)
        db.commit()

        return response_data

    else:
        # Invalid input case
        raise HTTPException(
            status_code=400,
            detail="Invalid input. Use demo=True with no organization_id, or demo=False with a valid organization_id."
        )