import asyncio
from job_queue import job_queue
from job_store import jobs

async def worker():
    while True:
        job_id = await job_queue.get()
        print(f"Worker acquired Job {job_id}")

        try:
            jobs[job_id]["status"] = "running"
            print(f"Running job {job_id}")

            await asyncio.sleep(10)

            jobs[job_id]["status"] = "complete"

            print(f"Completed job {job_id}")
        except:
            jobs[job_id]["status"] = "fail"
            print(f"Error processing job {job_id}")
        finally:
            job_queue.task_done()
