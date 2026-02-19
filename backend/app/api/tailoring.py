import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import TailoredResume, User
from app.schemas.schemas import TailoredResumeOut
from app.services.tailor_service import TailorService
from app.utils.pdf_export import text_to_pdf_bytes

router = APIRouter(prefix='/jobs', tags=['tailoring'])


@router.post('/{job_id}/tailor', response_model=TailoredResumeOut)
def tailor(job_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    service = TailorService(db)
    try:
        tr = service.generate(current.id, job_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TailoredResumeOut(
        id=tr.id,
        tailored_text=tr.tailored_text,
        ats_score=tr.ats_score,
        matched_keywords=json.loads(tr.matched_keywords_json),
        missing_keywords=json.loads(tr.missing_keywords_json),
        created_at=tr.created_at,
    )


@router.get('/{job_id}/tailored', response_model=TailoredResumeOut)
def latest_tailored(job_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    tr = (
        db.query(TailoredResume)
        .filter(TailoredResume.user_id == current.id, TailoredResume.job_id == job_id)
        .order_by(TailoredResume.created_at.desc())
        .first()
    )
    if not tr:
        raise HTTPException(status_code=404, detail='No tailored resume generated yet')

    return TailoredResumeOut(
        id=tr.id,
        tailored_text=tr.tailored_text,
        ats_score=tr.ats_score,
        matched_keywords=json.loads(tr.matched_keywords_json),
        missing_keywords=json.loads(tr.missing_keywords_json),
        created_at=tr.created_at,
    )


@router.get('/{job_id}/tailored/download')
def download_tailored(job_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    tr = (
        db.query(TailoredResume)
        .filter(TailoredResume.user_id == current.id, TailoredResume.job_id == job_id)
        .order_by(TailoredResume.created_at.desc())
        .first()
    )
    if not tr:
        raise HTTPException(status_code=404, detail='No tailored resume generated yet')

    pdf = text_to_pdf_bytes(tr.tailored_text)
    return Response(content=pdf, media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=tailored_resume.pdf'})
