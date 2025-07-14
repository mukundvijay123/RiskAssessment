from fastapi import APIRouter
import json
import os
from fastapi.responses import JSONResponse
from typing import List
from .models import RiskRequestModel
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

        
