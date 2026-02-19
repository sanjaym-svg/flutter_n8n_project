from datetime import datetime

import httpx

from app.core.config import settings
from app.providers.base import JobProvider, ProviderJob


class RemotiveProvider(JobProvider):
    name = 'remotive'

    async def fetch_jobs(self, filters: dict) -> list[ProviderJob]:
        params = {'search': ' '.join(filters.get('role_keywords', [])) or 'software'}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(settings.remotive_base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        jobs = []
        for item in data.get('jobs', []):
            if filters.get('remoteOnly') and 'remote' not in (item.get('candidate_required_location', '')).lower():
                continue
            jobs.append(
                ProviderJob(
                    provider=self.name,
                    provider_job_id=str(item.get('id')),
                    title=item.get('title') or 'Unknown',
                    company=item.get('company_name') or 'Unknown',
                    location=item.get('candidate_required_location') or 'Unknown',
                    employment_type=item.get('job_type'),
                    salary_min=None,
                    salary_max=None,
                    currency=None,
                    remote_type='remote',
                    description=item.get('description') or '',
                    apply_url=item.get('url') or '',
                    posted_at=datetime.fromisoformat(item['publication_date'].replace('Z', '+00:00')) if item.get('publication_date') else None,
                )
            )
        return jobs
