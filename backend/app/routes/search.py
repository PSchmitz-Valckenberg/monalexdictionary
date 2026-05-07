from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.search import search_entries

router = APIRouter()


class SearchResult(BaseModel):
    word: str
    definition: str


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[SearchResult]


@router.get("/api/search", response_model=SearchResponse)
def search(q: str = Query(default="")):
    q = q.strip()
    if not q:
        return SearchResponse(query=q, count=0, results=[])
    results = search_entries(q)
    return SearchResponse(query=q, count=len(results), results=results)
