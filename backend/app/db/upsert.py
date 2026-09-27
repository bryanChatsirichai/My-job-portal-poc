from sqlalchemy.orm import Session

from app.models.orm import Job
from app.models.schemas import CanonicalJobInput


def upsert_job(db: Session, job: CanonicalJobInput) -> Job:
    # Step 10 — match on (source, source_job_id); set status active
    existing = (
        db.query(Job)
        .filter(Job.source == job.source, Job.source_job_id == job.source_job_id)
        .one_or_none()
    )

    payload = {
        "title": job.title,
        "company_name": job.company_name,
        "company_uen": job.company_uen,
        "location": job.location.model_dump(),
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "salary_currency": job.salary_currency,
        "salary_period": job.salary_period,
        "employment_type": job.employment_type,
        "seniority_level": job.seniority_level,
        "skills": job.skills,
        "description": job.description,
        "posted_date": job.posted_date,
        "expiry_date": job.expiry_date,
        "apply_url": job.apply_url,
        "raw_payload": job.raw_payload,
        "status": "active",
    }

    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    record = Job(source=job.source, source_job_id=job.source_job_id, **payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def expire_stale_jobs(db: Session, source: str, seen_ids: set[str]) -> int:
    # Step 11 — active rows for this source not in seen_ids → expired
    query = db.query(Job).filter(Job.source == source, Job.status == "active")
    if seen_ids:
        query = query.filter(~Job.source_job_id.in_(seen_ids))

    count = 0
    for job in query.all():
        job.status = "expired"
        count += 1

    db.commit()
    return count
