import asyncio
from fastapi import FastAPI
from worker import worker
from job_queue import job_queue
from job_store import jobs

app = FastAPI()

@app.on_event("startup")
async def startup():
    asyncio.create_task(worker())

@app.get("/")
async def root():
    return {"messge" : "Working API"}

@app.post("/")
async def post_task():
    # put a job in the job_store
    jobs["123"] = {"status" : "queued"}
    
    # Add the job_id to the queue
    await job_queue.put("123")

    return {"job_id": "123"}

@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    return jobs[job_id]["status"]
