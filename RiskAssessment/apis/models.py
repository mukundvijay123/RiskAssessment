from pydantic import BaseModel, Field ,ConfigDict
from typing import List,Optional
from uuid import UUID
from datetime import datetime



'''
Models for Dashboard
'''
class AssessmentSummaryRequest(BaseModel):
    organization_id:UUID
    assessment_types: List[str]
    organization_context: Optional[str] = ""



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

class SiteRiskSafetyInput(BaseModel):
    riskCategory: str
    controlQuestion: str
    complianceStatus: str
    address_of_location: str
    nature_of_occupancy: str
    building_construction_details: str
    nature_of_other_occupancies: str
    total_floors_and_communication: str
    total_floor_area: str
    maximum_undivided_area: str
    floors_occupied: str
    building_age: str
    stability_certificate: str
    fire_noc_availability: str
    people_working_floor_wise: str
    max_visitors_peak_day: str
    business_hours: str
    power_backup_details: str
    store_room_stacking: str
    floor_covering_nature: str
    false_ceiling_details: str
    hvac_system_details: str
    area_passage_around_building: str

class RiskTrends(BaseModel):
    top_category: str
    risk_severity: str
    observations: List[str]



class SiteDetails(BaseModel):
    site_name: str
    address: str
    building_type: str
    floor_area_sq_ft: int
    occupancy_type: str
    year_of_construction: int
    no_of_floors: int

class GeneratedRiskOutput(BaseModel):
    risk_id: str
    category: str
    business_unit: str
    risk_owner: str
    timeline: str
    risk_name: str
    question: str
    compliance_status: str
    identified_threat: str
    likelihood: int
    impact: int
    risk_value: int
    residual_risk: str
    current_control_description: str
    current_control_rating: str
    mitigation_plan: str
    site_details: SiteDetails
    risk_classification_summary: str
    mitigation_suggestions: List[str]
    risk_trends: RiskTrends




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
    process_id:UUID
    process_name: str
    process_owner: Optional[str]
    description: Optional[str]

