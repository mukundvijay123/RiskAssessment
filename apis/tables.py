from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text,func,TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID,JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organization"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    head_username = Column(String)
    sector = Column(String)
    criticality = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    impact_matrix = Column(JSONB)
    licensed_modules = Column(JSONB)
    description = Column(JSONB)

    # Relationships
    ent_risks = relationship("EntRisk", backref="organization")
    threat_risks = relationship("ThreatRisk", backref="organization")






class EntRisk(Base):
    __tablename__ = "ent_risks"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False
    )

    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    likelihood_justification = Column(Text, nullable=False)
    impact_justification = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    escalated = Column(Boolean, default=False)

    # One-to-many relationship
    threats = relationship("EntThreat", back_populates="risk", cascade="all, delete-orphan")


class EntThreat(Base):
    __tablename__ = "ent_threats"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("ent_risks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text, nullable=False)

    # Relationship back to Risk
    risk = relationship("EntRisk", back_populates="threats")



class ThreatRisk(Base):
    __tablename__ = "threat_risks"

    id = Column(Integer, primary_key=True, index=True)  # UUID string

    organization_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False
    )

    domain = Column(String, nullable=False)
    riskName = Column(String, nullable=False)
    threat = Column(String, nullable=False)
    vulnerability = Column(String, nullable=False)
    category = Column(String, nullable=False)
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    likelihood_justification = Column(Text, nullable=False)
    impact_justification = Column(Text, nullable=False)
    threat_justification = Column(Text, nullable=False)
    vulnerability_justification = Column(Text, nullable=False)

class SiteRiskMitigation(Base):
    __tablename__ = "site_risk_mitigation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSONB, nullable=False)


class SiteRiskAssessment(Base):
    __tablename__ = "site_risk_assessment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSONB, nullable=False)


class ProcessThreats(Base):
    __tablename__ = "process_threats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    data = Column(JSONB, nullable=False)