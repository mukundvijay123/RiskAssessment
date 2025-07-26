from pydantic import BaseModel, Field ,ConfigDict
from typing import List,Optional
from uuid import UUID
from datetime import datetime


'''
Models for threat RA
'''

class ThreatRiskModel(BaseModel):
    id: Optional[int]
    organization_id:UUID
    domain: str
    riskName: str
    threat: str
    vulnerability: str
    category: str
    likelihood: int
    impact: int
    rating: int
    likelihood_justification: str
    impact_justification: str
    threat_justification: str
    vulnerability_justification: str
    class Config:
        from_attributes = True 

class ThreatRiskGenerationRequest(BaseModel):
    organization_id:UUID
    domain: str
    category: str
    business_context: Optional[str] = ""
    specific_focus: Optional[str] = ""
    number_of_records: Optional[int] = 10

class ThreatRiskGenerationResponse(BaseModel):
    success: bool
    threatRisks: List[ThreatRiskModel]
    message: str



class ThreatRiskUpdate(BaseModel):
    domain: str
    riskName: str
    threat: str
    vulnerability: str
    category: str
    likelihood: int
    impact: int
    rating: int



'''
Models for enterprise RA
'''

class EntRiskAssessmentRequest(BaseModel):
    organization_id: UUID
    category: str
    department: str
    business_context: Optional[str] = ""
    specific_concerns: Optional[str] = ""
    number_of_risks: Optional[int] = 5


class EntRiskGenerationRequest(BaseModel):
    category: str
    department: str
    business_context: Optional[str] = ""
    specific_concerns: Optional[str] = ""
    number_of_risks: Optional[int] = 5

class EntThreatModel(BaseModel):
    id: Optional[int]  # Optional if the DB generates it (SERIAL)
    risk_id: int       # Foreign key to risks.id
    name: str
    description: str
    justification: str  # Make sure this exists in DB too

    class Config:
        orm_mode = True


class EntRiskModel(BaseModel):
    id: Optional[int]  # SERIAL PK
    organization_id: UUID  # UUID from organization table
    category: str
    name: str
    description: str
    likelihood: int
    impact: int
    likelihood_justification: str
    impact_justification: str
    treatment: str
    department: str
    escalated: bool
    threats: List[EntThreatModel]
    model_config = ConfigDict(from_attributes=True)  


class EntRiskUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    likelihood: Optional[int]
    impact: Optional[int]
    likelihood_justification: Optional[str]
    impact_justification: Optional[str]
    treatment: Optional[str]
    department: Optional[str]
    escalated: Optional[bool]

    model_config = ConfigDict(from_attributes=True)


class EntRiskGenerationResponse(BaseModel):
    success: bool
    risks: List[EntRiskModel]
    message: str


class EntRiskEscalationRequest(BaseModel):
    escalated: bool

'''
Models for site RA
'''
class RiskQuestion(BaseModel):
    category: str
    question: str
    user_answer: str

class RiskRequestModel(BaseModel):
    responses: List[RiskQuestion]





'''
Models for the process RA
'''
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

class ProcessInput(BaseModel):
    process_id: UUID
    process_name: str
    process_owner: Optional[str]
    description: Optional[str]

