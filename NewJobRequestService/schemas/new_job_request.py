from pydantic import BaseModel
from datetime import datetime

class _CommunicationMode(BaseModel):
    chat: bool
    video_call: bool
    voice_call: bool

class JobRequest(BaseModel):
    heading: str
    description: str
    duration: datetime
    communication_mode: _CommunicationMode
    initial_price: float

class NewJobCreateResponse(BaseModel):
    message: str

class JobResponse(BaseModel):
    id: str
    job_details: JobRequest