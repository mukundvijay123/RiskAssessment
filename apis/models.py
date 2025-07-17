from pydantic import BaseModel, Field 
from typing import List,Optional
from uuid import UUID
from datetime import datetime

class ProcessRiskInput(BaseModel):
    process_name: str = Field(..., alias="processName")
    department: str
    description: str
    business_context: str = Field(..., alias="businessContext")
    process_owner: str = Field(..., alias="owner")
    place: str
    rto: str
    mtpd: str
    min_tolerable_downtime: str = Field(..., alias="minTolerableDowntime")

    class Config:
        validate_by_name= False


class RiskQuestion(BaseModel):
    category: str
    question: str
    user_answer: str

class RiskRequestModel(BaseModel):
    responses: List[RiskQuestion]


class CriticalProcessInfo(BaseModel):
    process_id: UUID
    process_name: str
    process_owner: Optional[str]
    subdepartment_id: Optional[UUID]
    bia_process_info_id: UUID
    description: Optional[str]
    critical: bool
    review_status: str
    bia_created_at: datetime
    bia_updated_at: datetime

    class Config:
        orm_mode = True

'''
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
'''