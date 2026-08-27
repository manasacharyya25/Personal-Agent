import asyncio
from fastapi import FastAPI, BackgroundTasks, File, Form, HTTPException, Header, UploadFile, Request
from worker import worker
from job_queue import job_queue
from job_store import jobs
from logger import log_message
from llm_client import llm_client
from contextlib import asynccontextmanager
import uuid
from Database import Database
from llm_request_body import LlmRequestBody
from api_response_model import LlmResponseModel
from routers import users
from config.settings import get_settings
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.state.db = Database(settings)
    app.state.db.connect()

    app.state.llm_client = llm_client(settings)
    asyncio.create_task(worker(app.state.llm_client, app.state.db))
    yield

    await app.state.db.close()

app = FastAPI(lifespan=lifespan)
app.include_router(users.router)

@app.middleware("http")
async def request_logger(request: Request, call_next):
     request_id = str(uuid.uuid4())[:8]
     start = time.time()

     response = await call_next(request)

     duration = time.time() - start
     status = response.status_code

     print(f"[{request_id}] {request.method} {request.url.path} {status} ({duration:.3f}sec)")

     response.headers["X-Request-ID"] = request_id
     return response

@app.get("/")
async def root():
    return {"messge" : "Working API"}

@app.post("/notty_api/{user_query}")
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

@app.post("/query_llm", response_model=LlmResponseModel)
async def query_llm(request : LlmRequestBody):
     print(f"""
        Request received with System prompt {request.system_prompt}
        User prompt {request.user_prompt}
        Top_K {request.top_k}
        Stream {request.stream}
     """)

     if not request.user_prompt:
        raise HTTPException(
             status_code=400,
             detail = {
                  "message": "Request not complete",
                  "field": "user_prompt"
             }
        )          
          
     return "{'id':1, 'llm_response':'Success', 'created_at':'now', 'call_id':'1234'}"


@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...), title : str = Form(...), x_api_key: str = Header(None)):
    if x_api_key != "correct_key":
         raise HTTPException(
              status_code=401,
              detail = "Unauthorized"
         )

    file_content = await file.read()

    return {
         "name": file.filename,
         "type": file.content_type,
         "size": len(file_content)
    }