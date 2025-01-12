from typing import Optional, List
from pydantic import BaseModel, Field

import random
import string

class ResidentModel(BaseModel):
    id: str = Field(..., alias="_id")
    name: str = Field(...)
    voice: List[List[float]] = Field(...)
    
    class Config:
        populate_by_name = True
        
class AddRequest(BaseModel):
    payload: Optional[str]  # Encrypted payload

class GetRequest(BaseModel):
    payload: Optional[str]  # Encrypted payload
