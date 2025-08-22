"""
Common Schemas
"""

from typing import Optional, Any
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Any] = None