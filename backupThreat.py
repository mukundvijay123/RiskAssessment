from pydantic import BaseModel, Field 
from typing import List,Optional
from uuid import UUID
from datetime import datetime


'''
Models for enterprise RA
'''

# Request Models
class RiskGenerationRequest(BaseModel):
    category: str
    department: str
    business_context: Optional[str] = ""
    specific_concerns: Optional[str] = ""
    number_of_risks: Optional[int] = 5

class ThreatGenerationRequest(BaseModel):
    risk_name: str
    category: str
    department: str
    number_of_threats: Optional[int] = 3

# Response Models
class Threat(BaseModel):
    id: Optional[int]  # Optional if the DB generates it (SERIAL)
    risk_id: int       # Foreign key to risks.id
    name: str
    description: str
    justification: str  # Make sure this exists in DB too

    class Config:
        orm_mode = True


class Risk(BaseModel):
    id: Optional[int]  # SERIAL PK
    organization_id: str  # UUID from organization table
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
    threats: List[Threat]


class RiskUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    likelihood: Optional[int]
    impact: Optional[int]
    treatment: Optional[str]
    department: Optional[str]



class RiskGenerationResponse(BaseModel):
    success: bool
    risks: List[Risk]
    message: str

class ThreatGenerationResponse(BaseModel):
    success: bool
    threats: List[Threat]
    message: str


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

