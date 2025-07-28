import requests
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .models import ProcessRiskInput,CriticalProcessInfo,ProcessInput  # or wherever your class is defined
from .tables import ProcessThreats
from .db import get_db

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

@processrouter.post("/v2/getThreats")
def extract_process_info(data: ProcessInput, db: Session = Depends(get_db)):
    query = """
        SELECT DISTINCT ON (p.id)
            p.name AS process_name,
            sd.name AS department,
            bpi.description,
            bpi.spoc AS process_owner,
            bpi.peak_period AS place,
            ia.rto,
            ia.mtpd,
            ia.mtpd AS min_tolerable_downtime,
            '' AS business_context
        FROM process p
        LEFT JOIN subdepartment sd ON p.subdepartment_id = sd.id
        LEFT JOIN bia_process_info bpi ON bpi.process_id = p.id
        LEFT JOIN impact_analysis ia ON ia.bia_process_id = bpi.id
        WHERE p.id = :process_id
        ORDER BY p.id, bpi.updated_at DESC;
    """

    result = db.execute(text(query), {"process_id": str(data.process_id)})
    row = result.mappings().fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Process data not found")

    # Map to ProcessRiskInput
    process_risk_input = ProcessRiskInput(
        processName=row["process_name"],
        department=row["department"],
        description=row["description"] or data.description or "",
        owner=row["process_owner"] or data.process_owner or "",
        place=row["place"] or "N/A",
        rto=row["rto"] or "N/A",
        mtpd=row["mtpd"] or "N/A",
        minTolerableDowntime=row["min_tolerable_downtime"] or "N/A",
        businessContext=row["business_context"] or ""
    )

    try:
        response = requests.post(
            "https://ey-catalyst-rvce-ey-catalyst.hf.space/api/generate-threats",
            json=process_risk_input.model_dump(by_alias=True),
            timeout=30
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat API call failed: {str(e)}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Threat generation failed: {response.text}"
        )

    return response.json()

@processrouter.get("/critical-processes", response_model=List[CriticalProcessInfo])
def get_critical_processes(db: Session = Depends(get_db)):
    query = """
    SELECT
        p.id AS process_id,
        p.name AS process_name,
        p.process_owner,
        p.subdepartment_id,
        bpi.id AS bia_process_info_id,
        bpi.description,
        bpi.critical,
        bpi.review_status,
        bpi.created_at AS bia_created_at,
        bpi.updated_at AS bia_updated_at
    FROM process p
    JOIN bia_process_info bpi ON p.id = bpi.process_id
    WHERE bpi.critical = TRUE
    """
    results = db.execute(text(query)).mappings().all()  # <-- This is the key fix
    return [CriticalProcessInfo(**row) for row in results]


