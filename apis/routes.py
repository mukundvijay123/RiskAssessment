from fastapi import APIRouter
import json
import os
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/siteRiskAssessment")

@router.get("/questions")
def get_questions():
    file_path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(file_path, "r") as f:
            questions = json.load(f)
        return JSONResponse(content={"questions": questions})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
