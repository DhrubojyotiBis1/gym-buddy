from pydantic import BaseModel

class BidCreate(BaseModel):
    amount: float
    user_id: str
    job_id: str

class BidRequest(BaseModel):
    amount: float
    job_id: str

class BidResponse(BaseModel):
    amount: float
    user_id: str
    job_id: str