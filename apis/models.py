from pydantic import BaseModel, Field

class ProcessRiskInput(BaseModel):
    process_name: str = Field(..., alias="processName")
    department: str
    description: str
    business_context: str = Field(..., alias="buissnessContext")
    process_owner: str = Field(..., alias="owner")
    place: str
    rto: str
    mtpd: str
    min_tolerable_downtime: str = Field(..., alias="minTolerableDowntime")

    class Config:
        validate_by_name= False
