import requests
from fastapi import APIRouter
from .models import ProcessRiskInput  # or wherever your class is defined

processrouter = APIRouter(prefix="/processRiskAssessment")

@processrouter.post("/getThreats")
def extract_process_info(data: ProcessRiskInput):
    print("called")
    # Construct message string for threat analysis
    paragraph = (
        f"This process is conducted in {data.place}. "
        f"The process '{data.process_name}' belongs to the '{data.department}' department. "
        f"Description: {data.description}. "
        f"It is managed by {data.process_owner}. "
        f"The RTO is {data.rto} and the MTPD is {data.mtpd}."
    )

    # Call threat assessment API
    response = requests.post(
        "https://ey-catalyst-rvce.hf.space/bia/threat-assessment/api/generate-threats",
        json={"message": paragraph}
    )

    if response.status_code != 200:
        return {"error": "Failed to get threat assessment", "details": response.text}

    # Combine input + threat result
    return response.json()
