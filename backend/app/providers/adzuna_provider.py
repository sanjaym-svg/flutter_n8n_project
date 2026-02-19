from datetime import datetime

import httpx

from app.core.config import settings
from app.providers.base import JobProvider, ProviderJob


class AdzunaProvider(JobProvider):
    name = 'adzuna'

    async def fetch_jobs(self, filters: dict) -> list[ProviderJob]:
        if not settings.adzuna_app_id or not settings.adzuna_app_key:
            return []

        params = {
            'app_id': settings.adzuna_app_id,
            'app_key': settings.adzuna_app_key,
            'what': ' '.join(filters.get('role_keywords', [])) or 'software engineer',
            'where': filters.get('location') or '',
            'results_per_page': 25,
            'content-type': 'application/json',
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get('https://api.adzuna.com/v1/api/jobs/us/search/1', params=params)
            resp.raise_for_status()
            data = resp.json()

        jobs = []
        for item in data.get('results', []):
            jobs.append(
                ProviderJob(
                    provider=self.name,
                    provider_job_id=str(item.get('id')),
                    title=item.get('title') or 'Unknown',
                    company=(item.get('company') or {}).get('display_name', 'Unknown'),
                    location=(item.get('location') or {}).get('display_name', 'Unknown'),
                    employment_type=item.get('contract_type'),
                    salary_min=item.get('salary_min'),
                    salary_max=item.get('salary_max'),
                    currency='USD',
                    remote_type='remote' if 'remote' in (item.get('title') or '').lower() else 'onsite',
                    description=item.get('description') or '',
                    apply_url=item.get('redirect_url') or '',
                    posted_at=datetime.fromisoformat(item['created'].replace('Z', '+00:00')) if item.get('created') else None,
                )
            )
        return jobs
