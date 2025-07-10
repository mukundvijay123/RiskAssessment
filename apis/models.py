from pydantic import BaseModel

class ProcessRiskInput(BaseModel):
    processName: str
    department: str
    description: str
    buissnessContext:str
    owner: str
    place: str
    rto: str
    mtpd: str
    minTolerableDowntime:str
