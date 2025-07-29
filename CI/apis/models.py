from pydantic import BaseModel
from typing import List
from datetime import datetime

class OutdatedBIAProcess(BaseModel):
    process_name: str
    updated_at: datetime

class NotificationResponse(BaseModel):
    notifications: bool
    notificationList: List[OutdatedBIAProcess]