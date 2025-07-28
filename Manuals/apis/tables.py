from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BcmManual(Base):
    __tablename__ = "bcm_manual"

    id = Column(String(50), primary_key=True)
    departments = Column(JSONB, nullable=False)
    version = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class BcmProcedures(Base):
    __tablename__ = "bcm_procedures"

    id = Column(String(50), primary_key=True)
    activation_protocol = Column(JSONB, nullable=False)
    roles_responsibilities = Column(JSONB, nullable=False)
    recovery_procedures = Column(JSONB, nullable=False)
    communication_procedures = Column(JSONB, nullable=False)
    escalation_procedures = Column(JSONB, nullable=False)
    version = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)

class BcmPolicy(Base):
    __tablename__ = "bcm_policy"

    id = Column(String(50), primary_key=True)
    statement = Column(JSONB, nullable=False)
    management_commitment = Column(JSONB, nullable=False)
    key_principles = Column(JSONB, nullable=False)
    governance = Column(JSONB, nullable=False)
    compliance = Column(JSONB, nullable=False)
    version = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
