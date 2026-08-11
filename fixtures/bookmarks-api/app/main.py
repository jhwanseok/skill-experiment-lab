from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.db import get_connection, init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class BookmarkCreate(BaseModel):
    url: str
    title: str


class Bookmark(BookmarkCreate):
    id: int
    created_at: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Bookmarks API", lifespan=lifespan)


@app.get("/bookmarks", response_model=List[Bookmark])
def list_bookmarks(sort: Optional[str] = None):
    conn = get_connection()
    if sort == "title":
        rows = conn.execute("SELECT * FROM bookmarks ORDER BY title").fetchall()
    else:
        rows = conn.execute("SELECT * FROM bookmarks ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.post("/bookmarks", response_model=Bookmark, status_code=201)
def create_bookmark(bookmark: BookmarkCreate):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO bookmarks (url, title) VALUES (?, ?)",
        (bookmark.url, bookmark.title),
    )
    conn.commit()
    row = conn.execute(
        "SELECT * FROM bookmarks WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return dict(row)


@app.get("/bookmarks/{bookmark_id}", response_model=Bookmark)
def get_bookmark(bookmark_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return dict(row)


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM bookmarks WHERE id = ?", (bookmark_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Bookmark not found")
    conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
    conn.commit()
    conn.close()
    return None


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
