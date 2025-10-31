from fastapi import APIRouter, Depends
from schemas.new_job_request import JobRequest, JobResponse, NewJobCreateResponse
from services.new_job_request_service import NewJobRequestService
from repositories.redis_repository import RedisRepository
from redis_service.redis_client import get_redis_client
from jwt_service.jwt_service import verify_jwt


new_job_request_service = NewJobRequestService(RedisRepository())

router = APIRouter(prefix='/new_job_request', tags=['NewJobRequest'])

@router.post('/create-request', response_model=NewJobCreateResponse)
async def create_request(job_data: JobRequest, redis_client = Depends(get_redis_client)):
    user_email = 'test@test.com'
    return await new_job_request_service.create_new_request(user_email, job_data, redis_client)

@router.get("/all", response_model=list[JobResponse])
async def get_all_jobs(redis_client = Depends(get_redis_client)):
    return await new_job_request_service.get_all(redis_client)

@router.get("/", response_model=JobResponse)
async def get_job_by(user_email: str = Depends(verify_jwt), redis_client = Depends(get_redis_client)):
    return await new_job_request_service.get_by(user_email, redis_client)