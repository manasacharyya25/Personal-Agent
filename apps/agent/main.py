"""FastAPI dashboard API + later chat."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import errors as pg_errors

from packages.common.config import get_settings
from packages.common.schemas import (
    CategoryCreate,
    CategoryUpdate,
    SearchCreate,
    SearchUpdate,
    SourceCreate,
    SourceUpdate,
    jsonable,
)
from packages.database.database import Database
from packages.database.repositories import categories as category_repo
from packages.database.repositories import search_queries as search_repo
from packages.database.repositories import sources as source_repo
from packages.database.repositories.categories import (
    CategoryInUseError,
    DuplicateNameError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    db = Database(settings.DB_CONNECTION_STRING)
    db.connect()
    app.state.db = db
    yield
    db.close()


app = FastAPI(title="Personal Agent", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Database:
    return app.state.db


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/categories")
def list_categories(db: Database = Depends(get_db)):
    return [jsonable(row) for row in category_repo.list_categories(db)]


@app.post("/api/categories", status_code=201)
def create_category(body: CategoryCreate, db: Database = Depends(get_db)):
    try:
        return jsonable(
            category_repo.create_category(
                db,
                body.name,
                purpose=body.purpose,
                prompt=body.prompt,
                examples=body.examples,
                evaluation_metrics=[m.model_dump() for m in body.evaluation_metrics],
                active=body.active,
            )
        )
    except DuplicateNameError:
        raise HTTPException(status_code=409, detail="Category already exists")


@app.patch("/api/categories/{category_id}")
def update_category(
    category_id: int, body: CategoryUpdate, db: Database = Depends(get_db)
):
    try:
        row = category_repo.update_category(
            db,
            category_id,
            name=body.name,
            purpose=body.purpose,
            prompt=body.prompt,
            examples=body.examples,
            evaluation_metrics=(
                [m.model_dump() for m in body.evaluation_metrics]
                if body.evaluation_metrics is not None
                else None
            ),
            active=body.active,
        )
    except DuplicateNameError:
        raise HTTPException(status_code=409, detail="Category already exists")
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    return jsonable(row)


@app.delete("/api/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Database = Depends(get_db)):
    try:
        deleted = category_repo.delete_category(db, category_id)
    except CategoryInUseError:
        raise HTTPException(
            status_code=409,
            detail="Remove subreddits and search queries in this category first",
        )
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")


@app.get("/api/reddit/sources")
def list_sources(db: Database = Depends(get_db)):
    return [jsonable(row) for row in source_repo.list_sources(db)]


@app.post("/api/reddit/sources", status_code=201)
def create_source(body: SourceCreate, db: Database = Depends(get_db)):
    try:
        return jsonable(
            source_repo.create_source(
                db,
                body.subreddit,
                body.category_id,
                body.active,
                body.priority,
            )
        )
    except pg_errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Category does not exist")
    except pg_errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Subreddit already added")


@app.patch("/api/reddit/sources/{source_id}")
def update_source(
    source_id: int, body: SourceUpdate, db: Database = Depends(get_db)
):
    row = source_repo.update_source(
        db,
        source_id,
        category_id=body.category_id,
        active=body.active,
        priority=body.priority,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Subreddit not found")
    return jsonable(row)


@app.delete("/api/reddit/sources/{source_id}", status_code=204)
def delete_source(source_id: int, db: Database = Depends(get_db)):
    if not source_repo.delete_source(db, source_id):
        raise HTTPException(status_code=404, detail="Subreddit not found")


@app.get("/api/reddit/search-queries")
def list_searches(db: Database = Depends(get_db)):
    return [jsonable(row) for row in search_repo.list_search_queries(db)]


@app.post("/api/reddit/search-queries", status_code=201)
def create_search(body: SearchCreate, db: Database = Depends(get_db)):
    try:
        return jsonable(
            search_repo.create_search_query(
                db,
                body.query,
                body.time_filter,
                body.category_id,
                body.active,
                body.priority,
            )
        )
    except pg_errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="Category does not exist")
    except pg_errors.UniqueViolation:
        raise HTTPException(
            status_code=409, detail="This search query already exists for that time filter"
        )


@app.patch("/api/reddit/search-queries/{query_id}")
def update_search(
    query_id: int, body: SearchUpdate, db: Database = Depends(get_db)
):
    row = search_repo.update_search_query(
        db,
        query_id,
        time_filter=body.time_filter,
        category_id=body.category_id,
        active=body.active,
        priority=body.priority,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Search query not found")
    return jsonable(row)


@app.delete("/api/reddit/search-queries/{query_id}", status_code=204)
def delete_search(query_id: int, db: Database = Depends(get_db)):
    if not search_repo.delete_search_query(db, query_id):
        raise HTTPException(status_code=404, detail="Search query not found")
