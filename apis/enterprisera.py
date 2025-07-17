import requests
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .models import CriticalProcessInfo
from .db import get_db

enterpriserouter = APIRouter(prefix="/entrerpriseRiskAssessment")

@enterpriserouter.get("/critical-processes", response_model=List[CriticalProcessInfo])
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
