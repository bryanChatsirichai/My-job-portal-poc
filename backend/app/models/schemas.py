from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationSchema(BaseModel):
    address: str | None = None
    district: str | None = None
    region: str | None = None
    lat: float | None = None
    lng: float | None = None


class JobListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    title: str
    company_name: str
    company_uen: str | None = None
    location: LocationSchema
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    skills: list[str] = Field(default_factory=list)
    posted_date: datetime
    expiry_date: datetime | None = None
    apply_url: str
    status: str


class JobDetail(JobListItem):
    description: str | None = None


class JobSearchResponse(BaseModel):
    items: list[JobListItem]
    total: int
    page: int
    limit: int


class HealthResponse(BaseModel):
    status: str
    database: str


class JobSourceOption(BaseModel):
    id: str
    label: str


class JobSourcesResponse(BaseModel):
    sources: list[JobSourceOption]


class CanonicalJobInput(BaseModel):
    source: str
    source_job_id: str
    title: str
    company_name: str
    company_uen: str | None = None
    location: LocationSchema
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    skills: list[str] = Field(default_factory=list)
    description: str | None = None
    posted_date: datetime
    expiry_date: datetime | None = None
    apply_url: str
    raw_payload: dict[str, Any]
