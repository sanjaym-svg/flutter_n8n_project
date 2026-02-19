from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Job, User
from app.schemas.schemas import JobOut, JobsSyncRequest, PaginatedJobs, SyncResult
from app.services.job_service import JobService

router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.post('/sync', response_model=SyncResult)
async def sync_jobs(
    payload: JobsSyncRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    service = JobService(db)
    return await service.sync_jobs(current.id, payload.filters.model_dump())


@router.get('', response_model=PaginatedJobs)
def list_jobs(
    page: int = Query(1, ge=1),
    remoteOnly: bool = False,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = JobService(db)
    items, total = service.list_jobs(page, remoteOnly, keyword)
    return PaginatedJobs(items=items, page=page, total=total)


@router.get('/{job_id}', response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return job
