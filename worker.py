import asyncio
from job_queue import job_queue
from job_store import jobs
from agent_service import process_query
from llm_client import llm_client

async def worker(llm_client):
    while True:
        job_id = await job_queue.get()
        print(f"Worker acquired Job {job_id}")

        try:
            jobs[job_id]["status"] = "running"
            user_query = jobs[job_id]["query"]

            print(f"Running job {job_id}")

            response = await process_query(user_query, llm_client)

            jobs[job_id]["status"] = "complete"
            jobs[job_id]["response"] = response
            print(f"Completed job {job_id}")
        except:
            jobs[job_id]["status"] = "fail"
            print(f"Error processing job {job_id}")
        finally:
            job_queue.task_done()
