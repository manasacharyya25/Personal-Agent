# Agentic Development — Day 1

## What we built

We started a FastAPI application and built a simple local long-running job system.

The architecture is:

```text
Client
  │
  │ POST /agent
  ▼
FastAPI
  │
  ├── Create job_id
  ├── Store job as "queued"
  └── Put job_id into queue
          │
          ▼
       Queue
          │
          ▼
       Worker
          │
          ├── Take job
          ├── Mark "running"
          ├── Execute work
          └── Mark "completed"
          │
          ▼
      Job Store
```

---

## 1. Project setup

Initial project:

```text
agentic-app/
├── main.py
├── requirements.txt
└── .venv/
```

We created a virtual environment:

```bash
python -m venv .venv
```

And activated it.

Our initial dependencies were:

```text
fastapi
uvicorn[standard]
```

---

## 2. Uvicorn

We ran:

```bash
uvicorn main:app --reload
```

We learned that:

```text
main:app
│    │
│    └── variable named "app"
└────── Python module "main"
```

Conceptually, Uvicorn is loading:

```python
from main import app
```

The `.py` extension isn't used because `main` is treated as a Python module.

`--reload` watches the code during development and restarts the server when files change.

---

## 3. FastAPI application

Our initial API was:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Agentic App is running"}
```

FastAPI also gives us interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# Long-running jobs

We established an important architecture:

> The HTTP request should create a job and return a job ID instead of waiting for a long-running operation to finish.

For example:

```text
POST /agent
```

returns:

```json
{
  "job_id": "abc123"
}
```

The client can then check:

```text
GET /jobs/abc123
```

---

## 4. The three core components

We identified three separate concepts.

### Job Store

The job store remembers the state of jobs.

For our local implementation:

```python
jobs = {}
```

Example:

```python
jobs["abc123"] = {
    "status": "queued"
}
```

The store can later contain:

```text
queued
running
completed
failed
```

Important:

The `job_id` identifies the job, but the ID itself does not track the status. The job store does.

Also, because this is a Python dictionary, all state disappears when the process restarts.

---

### Queue

The queue holds work waiting to be executed.

We used Python's built-in:

```python
asyncio.Queue()
```

Example:

```python
await job_queue.put(job_id)
```

A worker gets the next job with:

```python
job_id = await job_queue.get()
```

If the queue is empty, `await job_queue.get()` waits asynchronously until work becomes available.

We also learned that the queue and worker are different things:

> Queue = holds work

> Worker = executes work

---

### Worker

The worker continuously waits for jobs and executes them.

Conceptually:

```python
while True:
    job_id = await job_queue.get()

    # execute job

    job_queue.task_done()
```

Our worker currently simulates a long-running job with:

```python
await asyncio.sleep(10)
```

The worker changes the job state:

```text
queued
   ↓
running
   ↓
completed
```

If execution fails:

```text
queued
   ↓
running
   ↓
failed
```

---

## 5. Worker does not necessarily mean threads

Initially we thought of a worker as something with a number of threads.

We refined that understanding.

A worker is fundamentally an **execution mechanism** that takes work and runs it.

It can use:

- async tasks
- threads
- processes
- containers
- machines
- serverless functions

For our first implementation, we're using an asynchronous worker task.

This is particularly relevant because our eventual workload will involve agent execution and many network/API calls.

---

## 6. Starting the worker

FastAPI needs to start the worker when the application starts.

We used:

```python
@app.on_event("startup")
async def startup():
    asyncio.create_task(worker())
```

The important distinction is:

```python
await worker()
```

would wait for the worker to finish.

But our worker contains:

```python
while True:
```

so it never finishes.

Instead:

```python
asyncio.create_task(worker())
```

starts the worker as an asynchronous task alongside the API.

Conceptually:

```text
Python Process
     │
     ├── FastAPI
     │
     └── Worker Task
```

We also noted that modern FastAPI code uses the lifespan mechanism instead of `@app.on_event("startup")`, and we'll eventually move to that pattern.

---

# 7. Complete request flow

Our `/agent` endpoint does four things:

### Step 1 — Generate an ID

```python
job_id = str(uuid.uuid4())
```

### Step 2 — Create the job

```python
jobs[job_id] = {
    "status": "queued"
}
```

### Step 3 — Put it in the queue

```python
await job_queue.put(job_id)
```

### Step 4 — Return immediately

```python
return {
    "job_id": job_id
}
```

The API does not wait for the actual work.

---

# 8. Job status endpoint

We added:

```text
GET /jobs/{job_id}
```

which looks up the job:

```python
return jobs.get(job_id)
```

This gives the client a way to check the current state.

Example:

```json
{
  "status": "running"
}
```

Later:

```json
{
  "status": "completed"
}
```

---

# The mental model to remember

The most important lesson from today:

```text
                 FastAPI
                    │
              create job
                    │
                    ▼
              ┌──────────┐
              │Job Store │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  Queue   │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  Worker  │
              └────┬─────┘
                   │
                execute
                   │
                   ▼
              ┌──────────┐
              │Job Store │
              └──────────┘
```

Remember:

**Job Store** → remembers state

**Queue** → holds pending work

**Worker** → executes work

**Job ID** → identifies a particular execution

---

# What we deliberately did NOT add yet

Our implementation is intentionally local and simple.

We have not introduced:

- Redis
- Celery
- RabbitMQ
- PostgreSQL
- Docker
- multiple workers
- distributed workers
- production infrastructure

That is intentional.

The goal was to understand the underlying architecture before introducing infrastructure that abstracts it away.

---

# Where we go next

The next useful steps are:

1. Improve the job model instead of using raw dictionaries.
2. Separate the worker from the application more cleanly.
3. Understand multiple concurrent jobs.
4. Understand async vs threads vs processes.
5. Replace the in-memory queue/store with real infrastructure.
6. Eventually replace the simulated job with an actual agent execution loop.

The final destination is roughly:

```text
FastAPI
   │
   ▼
Persistent Job Store
   │
   ▼
Distributed Queue
   │
   ▼
Agent Worker(s)
   │
   ▼
Agent
   ├── LLM
   ├── Tools
   ├── Tool results
   ├── LLM
   └── ...
```

But we should understand each layer before adding it.
