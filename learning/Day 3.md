## Today's AI Agent Learning

### 1. Completed the Tool-Calling Agent Loop

We moved from a single tool call to a proper agent loop:

```text
User
 ↓
LLM
 ↓
Tool call(s)
 ↓
Execute tools
 ↓
Tool results
 ↓
LLM again
 ↓
More tools? → repeat
 ↓
No tools → final response
```

Important point: **the LLM decides the tool chain** based on the tool definitions. We don't hard-code:

```text
get_rhoq_info → draft_reply
```

The tool descriptions need to clearly communicate what each tool does.

---

### 2. `previous_response_id` and Threads

We learned that with OpenAI's Responses API, a conversation can be continued using:

```python
previous_response_id=response.id
```

So we don't need to manually send the entire chat history back in every prompt.

Our application can maintain:

```text
thread_id → latest_response_id
```

We'll implement thread persistence next.

---

### 3. FastAPI Dependency Injection

We clarified the difference from Spring.

```python
db = Depends(get_db)
```

is FastAPI's dependency mechanism, but `get_db()` isn't equivalent to a Spring `@Repository`.

We learned:

```text
app.state.db
     ↓
get_db(request)
     ↓
Depends(get_db)
     ↓
API endpoint
```

And importantly:

**Don't use `Depends()` inside normal internal application classes.**

Instead:

```python
class RAGService:
    def __init__(self, db):
        self.db = db
```

Dependencies are explicitly passed into internal code.

---

### 4. Database Infrastructure

Created a `Database` class around `asyncpg`.

Its responsibilities:

```text
Database
├── connect()
├── close()
├── fetch()
├── fetchrow()
└── execute()
```

It owns a PostgreSQL connection pool.

We also moved toward keeping configuration such as:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
DB_MIN_POOL_SIZE
DB_MAX_POOL_SIZE
```

in `.env`.

We clarified that `asyncpg` is the async PostgreSQL driver and `load_dotenv()` loads `.env` into environment variables.

---

### 5. Codebase Structure

We decided to start organizing the project around actual responsibilities:

```text
app/
├── main.py
├── api/
│   ├── routes/
│   └── dependencies.py
├── core/
├── agent/
├── llm/
├── tools/
├── database/
├── ingestion/
└── rag/
```

And we deliberately **aren't creating hypothetical files** like `planner.py` or `reasoning.py` until those responsibilities actually exist.

---

# RAG — Where We Started

We decided to learn RAG in two stages.

### Stage 1 — Retrieval

```text
Document
 ↓
Chunk
 ↓
Embed
 ↓
Vector DB
 ↓
Query
 ↓
Similarity search
 ↓
Relevant chunks
```

No LLM generation yet.

### Stage 2 — Actual RAG

```text
User question
 ↓
Retrieve relevant chunks
 ↓
Give chunks + question to LLM
 ↓
Generated answer
```

Then eventually we'll make retrieval available as an **agent tool**.

---

## 6. Chunking

We created the conceptual function:

```python
chunk(document) -> list[str]
```

For now we're using simple character-based chunks with overlap.

We learned why overlap exists: to avoid losing context at chunk boundaries.

---

## 7. Local Embeddings

Instead of an embedding API, we're using a Hugging Face model:

**`BAAI/bge-base-en-v1.5`**

The flow:

```text
list[str]
    ↓
embedding model
    ↓
list[list[float]]
```

Each chunk becomes a **768-dimensional vector**.

So:

```python
def embed(texts: list[str]) -> list[list[float]]:
    ...
```

---

## 8. Ingestion Pipeline

We settled on:

```text
scripts.py
     ↓
read document
     ↓
chunk()
     ↓
embed()
     ↓
save()
     ↓
Database
```

The script owns the DB lifecycle:

```python
db = Database()
await db.connect()

try:
    ...
finally:
    await db.close()
```

And accepts the document path from the command line:

```bash
python scripts.py rhoq_knowledge.md
```

The reusable functions stay separate:

```text
chunk_embed_save.py

chunk()
embed()
save()
```

`save()` receives the DB explicitly:

```python
await save(db, chunks, embeddings)
```

We also learned `zip(chunks, embeddings)` pairs each chunk with its corresponding embedding.

---

## Where we are now

You have moved from:

```text
LLM + tools
```

to:

```text
LLM
 ↓
Agent loop
 ↓
Tools
 ↓
Threads
 ↓
RAG ingestion
 ↓
Embeddings
 ↓
Vector database
```

**Next RAG step:** finish the database/vector setup and implement **retrieval** — taking a user query, embedding it, performing similarity search, and returning the most relevant chunks.

That will give you the complete **retrieval half of RAG** before we add generation.

Absolutely. Add this to today's notes:

### FastAPI `Depends()` — Important Mental Model

`Depends()` is **bound to FastAPI's request/dependency-resolution lifecycle**.

For example:

```python
async def endpoint(
    db: Database = Depends(get_db)
):
    ...
```

FastAPI resolves `get_db()` **when handling the request**.

This is why we **don't use `Depends()` in standalone code** such as:

```text
scripts.py
RAG ingestion pipeline
workers
internal services
CLI scripts
```

Instead, those components receive dependencies explicitly:

```python
async def ingest_document(db: Database, document: str):
    ...
```

Mental model:

```text
HTTP Request
    ↓
FastAPI
    ↓
Depends(get_db)
    ↓
Database instance
    ↓
Endpoint
    ↓
Internal services
```

Whereas outside the request lifecycle:

```text
CLI / Worker / Script
        ↓
create/get dependency
        ↓
pass explicitly
```

**Key takeaway:** `Depends()` is not a general-purpose Python IoC container. It's FastAPI's request-time dependency injection mechanism.
