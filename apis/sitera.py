from fastapi import APIRouter
import json
import os
from fastapi.responses import JSONResponse
from typing import List
from models import RiskItem,RiskMitigationResponse
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
def generate_risk_mitigation(risk_items: List[RiskItem]):
    paragraphs = []

    for idx, item in enumerate(risk_items, 1):
        para = (
            f"Risk {idx}: The enabler type '{item.enablerType}' in the domain '{item.enablerDomain}' "
            f"under the major category '{item.majorCategory}' is mapped to the threat '{item.mappedThreat}'. "
            f"Existing controls include: {item.existingControls}. "
            f"Compliance status is '{item.complianceStatus}'. "
            f"The impact is rated as '{item.impact}', with a likelihood of '{item.likelihood}', "
            f"resulting in an overall risk value of '{item.riskValue}'."
        )
        paragraphs.append(para)

        combined_paragraph = "\n\n".join(paragraphs)

    # Call external threat assessment API
    response = requests.post(
        "https://ey-catalyst-rvce.hf.space/bia/threat-assessment/api/generate-threats",
        json={"message": combined_paragraph}
    )

    if response.status_code != 200:
        return {
            "error": "Failed to get threat mitigation response",
            "status_code": response.status_code,
            "details": response.text
        }

    return response.json()

        
