from repositories.redis_interface import IRedisRepository
from redis_service.redis_client import RedisClient
from schemas.new_job_request import JobRequest, NewJobCreateResponse, JobResponse
from starlette.exceptions import HTTPException as StarletteHTTPException 
from datetime import datetime, timezone

class NewJobRequestService:
    def __init__(self, redis: IRedisRepository):
        self.redis = redis
    
    async def create_new_request(self, id: str, job_data: JobRequest, redis_client: RedisClient):
        now = datetime.now(timezone.utc)
        if now > job_data.duration:
            raise StarletteHTTPException(status_code=400, detail='Duration can not be in past')
        exp = (job_data.duration-now)
        result = await self.redis.insert(id, job_data, redis_client, expire_in=exp)
        if result:
            return NewJobCreateResponse(message='sucess')
        return NewJobCreateResponse(message='failed')
    
    async def get_all(self, redis_client: RedisClient):
        jobs = await self.redis.get_all(redis_client)
        serialised_jobs = []
        for job in jobs:
            serialised_job_response = JobResponse(**job)
            serialised_jobs.append(serialised_job_response)
        return serialised_jobs
    
    async def get_by(self, id: str, redis_client: RedisClient):
        job = await self.redis.get_by_id(id, redis_client)
        if not job:
            raise StarletteHTTPException(404, "Job not found")
        return JobResponse(**job)