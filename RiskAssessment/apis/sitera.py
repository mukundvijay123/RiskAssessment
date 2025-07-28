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
def generate_risk_mitigation(risk_items: RiskRequestModel):



    response = requests.post(
        "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/risk-mitigation",
        json=risk_items.model_dump(by_alias=True)
    )
    a=response.status_code
    if a != 200:
        return {
            "error": "Failed to get threat mitigation response",
            "status_code": response.status_code,
            "details": response.text
        }

    return response.json()


@siterouter.post("/site-risk-assessment")
def do_sam(input: SiteRiskSafetyInput):
    """
    Sends site risk safety input to external risk mitigation API and returns the response.
    """
    try:
        response = requests.post(
            "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/site-risk-mitigation",
            json=input.model_dump(by_alias=True),
            timeout=30
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error connecting to mitigation API: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error": "Failed to get threat mitigation response",
                "response": response.text
            }
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid JSON received from external API")
