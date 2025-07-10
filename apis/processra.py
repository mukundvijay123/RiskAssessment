import requests
from fastapi import APIRouter
from .models import ProcessRiskInput  # or wherever your class is defined

processrouter = APIRouter(prefix="/processRiskAssessment")

@processrouter.post("/getThreats")
def extract_process_info(data: ProcessRiskInput):
    # Optional: Generate paragraph for logging or UI
    paragraph = (
        f"This process is conducted in {data.place}. "
        f"The process '{data.process_name}' belongs to the '{data.department}' department. "
        f"Description: {data.description}. "
        f"It is managed by {data.process_owner}. "
        f"The RTO is {data.rto} and the MTPD is {data.mtpd}."
    )
    print("Generated paragraph:\n", paragraph)
    print(data)
    # Send entire data object to Hugging Face API with correct aliasing
    try:
        response = requests.post(
            "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/generate-threats",
            json=data.model_dump(by_alias=True),
            timeout=30
        )
    except Exception as e:
        return {"error": "Failed to call threat assessment API", "details": str(e)}

    if response.status_code != 200:
        return {
            "error": "Failed to get threat assessment",
            "status_code": response.status_code,
            "details": response.text
        }

    return response.json()