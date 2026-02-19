from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProviderJob:
    provider: str
    provider_job_id: str
    title: str
    company: str
    location: str
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    remote_type: str | None
    description: str
    apply_url: str
    posted_at: datetime | None


class JobProvider(ABC):
    name: str

    @abstractmethod
    async def fetch_jobs(self, filters: dict) -> list[ProviderJob]:
        ...
