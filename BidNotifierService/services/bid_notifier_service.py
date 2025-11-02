from typing import AsyncGenerator
import asyncio
import json

from redis_service.redis_client import RedisClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from repositories.redis_interface import IRedisRepository

class BidNotifierService:
    def __init__(self, redis_repo: IRedisRepository):
        # Store the Redis repository interface for communicating with Redis
        self.redis_repo = redis_repo

    async def listen_to_bid(
        self, job_id: str, redis: RedisClient
    ) -> AsyncGenerator[str, None]:
        """
        Listens to bid updates for a given job_id as a server-sent event (SSE) stream.

        Args:
            job_id (str): The Job ID to monitor for bid updates.
            redis (RedisClient): The Redis connection instance.

        Yields:
            AsyncGenerator[str, None]: SSE event strings.
        """
        # Step 1: Check and yield any existing bids for this job_id
        try:
            existing_bids = await self.redis_repo.get_existing_bids(job_id, redis)
            if existing_bids:
                formatted = (
                    json.dumps(existing_bids)
                    if not isinstance(existing_bids, str)
                    else existing_bids
                )
                # Yield existing bids as an SSE event
                yield f"data: {formatted}\n\n"
        except Exception as exc:
            # If there is any problem fetching existing bids, raise HTTPException
            raise StarletteHTTPException(
                status_code=500, detail=f"Error fetching existing bids: {str(exc)}"
            )

        # Step 2: Subscribe to Redis pub/sub channel for the job_id
        try:
            await self.redis_repo.subscribe(job_id, redis)
            yield "event: ready\ndata: connection established\n\n"
        except Exception as exc:
            # If subscription fails, raise HTTPException
            raise StarletteHTTPException(
                status_code=500, detail=f"Subscription to job_id={job_id} failed: {str(exc)}"
            )

        async def send_heartbeats(queue: asyncio.Queue):
            """
            Sends periodic heartbeat events to keep the SSE connection alive.
            """
            try:
                while True:
                    await asyncio.sleep(5)
                    # Add a heartbeat event to the queue every 5 seconds
                    await queue.put(": heartbeat\n\n")
            except asyncio.CancelledError:
                # Heartbeat task is canceled when connection is closed, just exit
                pass
            except Exception as exc:
                # Catch and report unexpected errors in heartbeat
                await queue.put(f"event: error\ndata: Heartbeat error: {str(exc)}\n\n")

        async def listen_for_bids(queue: asyncio.Queue):
            """
            Listens for new bids on the Redis channel and pushes them to the client.
            """
            try:
                # Infinite loop: listen for messages from redis
                async for message in self.redis_repo.get_message():
                    if message is not None:
                        try:
                            # Format the message into proper JSON/string for SSE
                            formatted = (
                                json.dumps(message)
                                if not isinstance(message, str)
                                else message
                            )
                            # Put the bid update into the queue for downstream sending
                            await queue.put(f"event: message\ndata: {formatted}\n\n")
                        except Exception as exc:
                            # If message formatting fails, yield error to client
                            await queue.put(f"event: error\ndata: Error processing message: {str(exc)}\n\n")
            except asyncio.CancelledError:
                # Bid listener is canceled when connection is closed, just exit
                pass
            except Exception as exc:
                # Handle other unexpected errors in bid listener
                await queue.put(f"event: error\ndata: Error in listen_for_bids: {str(exc)}\n\n")

        # Create an asyncio queue for communication between tasks
        queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        # Start the heartbeat background task
        try:
            heartbeat_task = asyncio.create_task(send_heartbeats(queue))
        except Exception as exc:
            raise StarletteHTTPException(
                status_code=500, detail=f"Failed to start heartbeat task: {str(exc)}"
            )
        # Start the background task for listening to bid updates
        try:
            listener_task = asyncio.create_task(listen_for_bids(queue))
        except Exception as exc:
            heartbeat_task.cancel()
            raise StarletteHTTPException(
                status_code=500, detail=f"Failed to start bid listener task: {str(exc)}"
            )

        # Main loop: Yield messages (either heartbeat or new bids or errors) from the queue
        try:
            while True:
                try:
                    msg = await queue.get()
                    yield msg
                except Exception as exc:
                    # Yield errors encountered when reading from the queue
                    yield f"event: error\ndata: Error while getting from queue: {str(exc)}\n\n"
        except asyncio.CancelledError:
            # Yield a disconnect event if the main listener is cancelled
            yield "event: disconnect\ndata: client disconnected\n\n"
        except Exception as exc:
            # Yield a generic error for uncaught exceptions in main loop
            yield f"event: error\ndata: Unexpected error: {str(exc)}\n\n"
        finally:
            # On exit, ensure background tasks are properly cancelled and cleaned up
            for task in (heartbeat_task, listener_task):
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        # Task cancelled successfully, nothing to report
                        pass
                    except Exception as exc:
                        # Yield error event if fails to cancel task properly
                        yield f"event: error\ndata: Error cancelling a background task: {str(exc)}\n\n"
            try:
                # Unsubscribe from Redis pub/sub (cleanup)
                await self.redis_repo.unsubscribe()
            except Exception as exc:
                # If unsubscribe fails, yield error event to client
                yield f"event: error\ndata: Error unsubscribing from Redis: {str(exc)}\n\n"
