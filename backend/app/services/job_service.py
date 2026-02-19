import json
from datetime import datetime, timedelta

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.models.models import Job, JobRun
from app.providers.adzuna_provider import AdzunaProvider
from app.providers.base import JobProvider
from app.providers.remotive_provider import RemotiveProvider
from app.utils.job_utils import dedupe_hash, sanitize_text


class JobService:
    def __init__(self, db: Session):
        self.db = db
        self.providers: list[JobProvider] = [AdzunaProvider(), RemotiveProvider()]

    async def sync_jobs(self, user_id: int, filters: dict) -> dict:
        run = JobRun(user_id=user_id, status='running', filters_json=json.dumps(filters))
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        total = 0
        provider_stats = {}
        for provider in self.providers:
            try:
                jobs = await provider.fetch_jobs(filters)
            except Exception:
                provider_stats[provider.name] = {'status': 'failed', 'count': 0}
                continue

            count = 0
            for p_job in jobs:
                if filters.get('postedWithinHours') and p_job.posted_at:
                    if p_job.posted_at < datetime.utcnow().astimezone() - timedelta(hours=filters['postedWithinHours']):
                        continue
                if not p_job.apply_url:
                    continue
                item_hash = dedupe_hash(p_job.title, p_job.company, p_job.location, p_job.apply_url)
                existing = self.db.query(Job).filter(Job.dedupe_hash == item_hash).first()
                if existing:
                    existing.fetched_at = datetime.utcnow()
                    existing.description = sanitize_text(p_job.description)
                else:
                    self.db.add(
                        Job(
                            provider=p_job.provider,
                            provider_job_id=p_job.provider_job_id,
                            title=p_job.title,
                            company=p_job.company,
                            location=p_job.location,
                            employment_type=p_job.employment_type,
                            salary_min=p_job.salary_min,
                            salary_max=p_job.salary_max,
                            currency=p_job.currency,
                            remote_type=p_job.remote_type,
                            description=sanitize_text(p_job.description),
                            apply_url=p_job.apply_url,
                            posted_at=p_job.posted_at,
                            fetched_at=datetime.utcnow(),
                            dedupe_hash=item_hash,
                        )
                    )
                count += 1
            total += count
            provider_stats[provider.name] = {'status': 'ok', 'count': count}
            self.db.commit()

        run.status = 'completed'
        run.completed_at = datetime.utcnow()
        self.db.commit()

        return {'inserted_or_updated': total, 'providers': provider_stats}

    def list_jobs(self, page: int, remote_only: bool, keyword: str | None):
        query = self.db.query(Job)
        if remote_only:
            query = query.filter(or_(Job.remote_type.ilike('%remote%'), Job.location.ilike('%remote%')))
        if keyword:
            query = query.filter(or_(Job.title.ilike(f'%{keyword}%'), Job.description.ilike(f'%{keyword}%')))
        total = query.count()
        items = query.order_by(desc(Job.posted_at), desc(Job.fetched_at)).offset((page - 1) * 20).limit(20).all()
        return items, total
