from uuid import UUID

from sqlalchemy import String, cast, func, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.orm import Job

USE_SQLITE = settings.database_backend == "sqlite"


def search_jobs(
    db: Session,
    *,
    q: str | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    location: str | None = None,
    source: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "posted_date_desc",
) -> tuple[list[Job], int]:
    query = db.query(Job).filter(Job.status == "active")

    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.description.ilike(pattern),
                Job.company_name.ilike(pattern),
            )
        )

    if salary_min is not None:
        query = query.filter(or_(Job.salary_max.is_(None), Job.salary_max >= salary_min))

    if salary_max is not None:
        query = query.filter(or_(Job.salary_min.is_(None), Job.salary_min <= salary_max))

    if location:
        pattern = f"%{location}%"
        if USE_SQLITE:
            location_text = cast(Job.location, String)
            query = query.filter(location_text.ilike(pattern))
        else:
            query = query.filter(
                or_(
                    Job.location["district"].astext.ilike(pattern),
                    Job.location["region"].astext.ilike(pattern),
                    Job.location["address"].astext.ilike(pattern),
                )
            )

    if source:
        query = query.filter(Job.source == source)

    total = query.with_entities(func.count(Job.id)).scalar() or 0

    if sort == "salary_desc":
        query = query.order_by(Job.salary_max.desc().nullslast(), Job.posted_date.desc())
    else:
        query = query.order_by(Job.posted_date.desc())

    offset = max(page - 1, 0) * limit
    items = query.offset(offset).limit(limit).all()
    return items, total


def get_job_by_id(db: Session, job_id: UUID) -> Job | None:
    return db.get(Job, job_id)
