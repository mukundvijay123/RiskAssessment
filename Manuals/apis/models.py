from pydantic import BaseModel, Field ,ConfigDict
from typing import List,Optional
from uuid import UUID
from datetime import datetime



class SubDeptRequest(BaseModel):
    org_id: str
    subdept_id: str