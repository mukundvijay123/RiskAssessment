from pydantic import BaseModel

class ProcessRiskInput(BaseModel):
    process_name: str
    department: str
    description: str
    process_owner: str
    place: str
    rto: str
    mtpd: str
