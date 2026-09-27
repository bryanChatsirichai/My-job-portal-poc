from collections.abc import Generator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.db.search import get_job_by_id, search_jobs
from app.db.session import get_db
from app.job_sources import list_job_source_options
from app.models.schemas import (
    HealthResponse,
    JobDetail,
    JobListItem,
    JobSearchResponse,
    JobSourceOption,
    JobSourcesResponse,
)

router = APIRouter(prefix="/api/v1", tags=["jobs"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", database=settings.database_backend)


@router.get("/job-sources", response_model=JobSourcesResponse)
def job_sources() -> JobSourcesResponse:
    options = [JobSourceOption(**item) for item in list_job_source_options()]
    return JobSourcesResponse(sources=options)


@router.get("/jobs", response_model=JobSearchResponse)
def list_jobs(
    q: str | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    location: str | None = None,
    source: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="posted_date_desc"),
    db: Session = Depends(get_db),
) -> JobSearchResponse:
    items, total = search_jobs(
        db,
        q=q,
        salary_min=salary_min,
        salary_max=salary_max,
        location=location,
        source=source,
        page=page,
        limit=limit,
        sort=sort,
    )
    return JobSearchResponse(
        items=[JobListItem.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> JobDetail:
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetail.model_validate(job)
