import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["BOOKMARKS_DB"] = path
    from app.main import app

    with TestClient(app) as c:
        yield c

    del os.environ["BOOKMARKS_DB"]
    os.remove(path)


def test_create_and_list_bookmark(client):
    res = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "Example"}
    )
    assert res.status_code == 201
    created = res.json()
    assert created["url"] == "https://example.com"
    assert created["title"] == "Example"

    res = client.get("/bookmarks")
    assert res.status_code == 200
    bookmarks = res.json()
    assert len(bookmarks) == 1
    assert bookmarks[0]["title"] == "Example"


def test_get_missing_bookmark_returns_404(client):
    res = client.get("/bookmarks/999")
    assert res.status_code == 404


def test_delete_bookmark(client):
    created = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "Example"}
    ).json()

    res = client.delete(f"/bookmarks/{created['id']}")
    assert res.status_code == 204

    res = client.get("/bookmarks")
    assert res.json() == []
