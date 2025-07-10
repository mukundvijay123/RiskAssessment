from pydantic import BaseModel, Field , Optional
from typing import List

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

class RiskItem(BaseModel):
    enablerType: str
    enablerDomain: str
    majorCategory: str
    mappedThreat: str
    existingControls: str
    complianceStatus: str
    impact: str
    likelihood: str
    riskValue: str

class MitigationResponse(BaseModel):
    revisedImpact: int
    revisedLikelihood: int
    revisedRiskValue: int
    mitigationPlan: str
    ownership: str

class RiskMitigationResponse(BaseModel):
    mitigatedRisks: List[MitigationResponse]



