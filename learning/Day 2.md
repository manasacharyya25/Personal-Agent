# Agentic Development --- Today

## 1. FastAPI `BackgroundTasks`

We learned that FastAPI provides:

``` python
from fastapi import BackgroundTasks
```

It can be used like:

``` python
async def endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(log_message, "Job created")
```

It is useful for small ancillary work such as logging, notifications, or
small follow-up tasks.

It is **not a replacement for a real job queue + worker architecture**.

Our architecture therefore remains:

``` text
FastAPI
   ↓
Queue
   ↓
Worker
   ↓
AgentService
```

while `BackgroundTasks` can be used for things like logging at the API
layer.

------------------------------------------------------------------------

## 2. FastAPI-specific dependencies should stay at the API boundary

We established an important separation:

``` text
API Layer
├── FastAPI
├── BackgroundTasks
├── Request
├── Response
└── Depends

Internal Code
├── Worker
├── AgentService
├── LLMClient
└── Logger
```

Internal classes/functions should generally not depend on FastAPI.

For example, `LLMClient` should not import:

``` python
from fastapi import BackgroundTasks
```

If the Agent needs logging, it can call a logging abstraction directly.

The logging mechanism itself can be asynchronous, but the Agent should
not need to know about FastAPI.

------------------------------------------------------------------------

## 3. `Depends()` vs special FastAPI parameters

We clarified:

``` python
async def endpoint(background_tasks: BackgroundTasks):
```

is correct.

`BackgroundTasks` is a special object that FastAPI knows how to provide
automatically.

`Depends()` is generally used for application dependencies we define
ourselves:

``` python
user = Depends(get_current_user)
```

So:

``` text
Framework-provided special objects
    ↓
type annotation is enough

Application dependencies
    ↓
Depends(...)
```

------------------------------------------------------------------------

# 4. Agent Service

We created an `agent_service.py`.

Its responsibility is to orchestrate Agent behavior, rather than having
the worker directly perform LLM logic.

Current conceptual flow:

``` text
Worker
   ↓
AgentService
   ↓
LLMClient
   ↓
LLM
```

We chose to keep the AgentService as functions for now rather than
introducing a class unnecessarily.

Example:

``` python
from llm_client import LLMClient


async def process_query(
    user_msg: str,
    llm_client: LLMClient
):
    prompt = f"Answer me this {user_msg}"

    response = await llm_client.send_message(prompt)

    return response
```

The dependency is passed explicitly.

------------------------------------------------------------------------

# 5. LLM Client

We created an `LLMClient` abstraction.

Its responsibility is communicating with the LLM provider.

Conceptually:

``` python
class LLMClient:

    async def send_message(self, prompt: str):
        ...
```

The AgentService should not need to know the details of the underlying
LLM SDK.

So:

``` text
AgentService
     ↓
LLMClient
     ↓
LLM Provider
```

------------------------------------------------------------------------

# 6. One LLM Client instance

We decided to create a single `LLMClient` instance when the application
starts instead of creating one for every job.

The client reads its configuration/API key from environment variables.

Conceptually:

``` text
Application startup
       ↓
Create LLMClient
       ↓
Worker receives LLMClient
       ↓
AgentService uses LLMClient
```

We explicitly avoided making the client a module-level global.

------------------------------------------------------------------------

# 7. FastAPI lifespan

We moved from the deprecated startup event approach:

``` python
@app.on_event("startup")
```

to the modern lifespan pattern:

``` python
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup
    ...

    yield

    # shutdown / cleanup
```

Everything before:

``` python
yield
```

is startup.

Everything after:

``` python
yield
```

is shutdown.

We use lifespan to create application-level resources such as the LLM
client and start the worker.

------------------------------------------------------------------------

# 8. Passing dependencies to the worker

We discussed two options:

### Option A

Have the worker reach into:

``` python
app.state.llm_client
```

### Option B --- chosen approach

Pass the dependency explicitly:

``` python
asyncio.create_task(
    worker(app.state.llm_client)
)
```

Then:

``` python
async def worker(llm_client):
    ...
```

This is cleaner because the worker doesn't need to know about FastAPI.

The dependency chain becomes:

``` text
Lifespan
   ↓
LLMClient
   ↓
Worker
   ↓
AgentService
   ↓
LLMClient
```

`app.state` is used by the FastAPI layer to own application-level
resources, while internal functions receive what they need explicitly.

------------------------------------------------------------------------

# 9. Current worker flow

The worker now roughly does:

``` python
async def worker(llm_client):
    while True:
        job_id = await job_queue.get()

        try:
            jobs[job_id]["status"] = "running"

            response = await process_query(
                job_id,
                llm_client
            )

            jobs[job_id]["status"] = "complete"
            jobs[job_id]["result"] = response

        except Exception:
            jobs[job_id]["status"] = "fail"

        finally:
            job_queue.task_done()
```

The important flow is:

``` text
Job
 ↓
Queue
 ↓
Worker
 ↓
AgentService
 ↓
LLMClient
 ↓
LLM
 ↓
Response
 ↓
Job Store
```

The response is stored in the job store so the polling endpoint can
return it.

------------------------------------------------------------------------

# 10. Python-specific things we encountered

### `await asyncio.sleep()`

This:

``` python
asyncio.sleep(10)
```

does not actually wait unless awaited.

Correct:

``` python
await asyncio.sleep(10)
```

------------------------------------------------------------------------

### Assignment vs type annotation

This:

``` python
prompt: f"Answer me this {user_msg}"
```

is not assigning a value.

Correct:

``` python
prompt = f"Answer me this {user_msg}"
```

`:` is used for type annotations.

------------------------------------------------------------------------

### Class naming

Python convention is to use PascalCase for classes:

``` python
class LLMClient:
    ...
```

Then:

``` python
async def process_query(
    user_msg: str,
    llm_client: LLMClient
):
```

------------------------------------------------------------------------

# 11. Where we are now

We now have the first working asynchronous Agent API:

``` text
                 POST /agent
                      │
                      ▼
                  FastAPI
                      │
                 create job
                      │
                      ▼
                    Queue
                      │
                      ▼
                   Worker
                      │
                      ▼
                AgentService
                      │
                      ▼
                  LLMClient
                      │
                      ▼
                     LLM
                      │
                      ▼
                  Response
                      │
                      ▼
                  Job Store
                      │
                      ▼
              GET /jobs/{id}
```

The next step is to turn the simple:

``` text
User Query → LLM → Response
```

into a real Agent loop:

``` text
User Query
    ↓
LLM
    ↓
Tool required?
   /  No   Yes
 │     │
 │    Tool
 │     │
 │   Result
 │     │
 └──→ LLM
        ↓
   Final Response
```

That is where the core Agentic implementation begins.
