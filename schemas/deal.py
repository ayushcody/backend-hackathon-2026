from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageSchema(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    conversation: List[MessageSchema]
    product: Optional[str] = None

class DealCreate(BaseModel):
    prospect: str
    conversation: List[MessageSchema]

class ClassificationResult(BaseModel):
    stage: str
    confidence: float
    reason: str
