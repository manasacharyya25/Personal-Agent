import asyncio
from fastapi import FastAPI, BackgroundTasks
from worker import worker
from job_queue import job_queue
from job_store import jobs
from logger import log_message
from llm_client import llm_client
from contextlib import asynccontextmanager
import uuid
from Database import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    app.state.db.connect()

    app.state.llm_client = llm_client()
    asyncio.create_task(worker(app.state.llm_client, app.state.db))
    yield

    await app.state.db.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"messge" : "Working API"}

@app.post("/{user_query}")
async def post_task(user_query: str, bg_task : BackgroundTasks):
    # put a job in the job_store
    job_id = uuid.uuid4().hex[:3]
    jobs[job_id] = {"status" : "queued", "query": user_query}

    bg_task.add_task(log_message, f"job queued with job id {job_id}")
    # Add the job_id to the queue
    await job_queue.put(job_id)

    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    return jobs[job_id]

@app.post("/rag_retrieval/{query}")
async def get_rag_retrieval(query: str):
    # put a job in the job_store
        job_id = uuid.uuid4().hex[:3]
        jobs[job_id] = {"status" : "queued", "query": query}
    
        # Add the job_id to the queue
        await job_queue.put(job_id)
    
        return {"job_id": job_id}