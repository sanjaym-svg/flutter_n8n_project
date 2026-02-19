from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.models import Resume, User
from app.schemas.schemas import ResumeOut, UserOut
from app.services.storage import StorageService
from app.utils.resume_parser import extract_text

router = APIRouter(tags=['user'])


@router.get('/me', response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.post('/resume/upload', response_model=ResumeOut)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    ext = (file.filename or '').lower()
    if not (ext.endswith('.pdf') or ext.endswith('.docx')):
        raise HTTPException(status_code=400, detail='Only PDF and DOCX files are supported')

    data = file.file.read()
    if len(data) > settings.max_resume_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail='File too large')

    extracted = extract_text(file.filename, data)
    if not extracted:
        raise HTTPException(status_code=400, detail='Could not extract text from resume')

    storage = StorageService()
    storage.ensure_bucket()
    url = storage.upload_resume(file.filename, data)

    db.query(Resume).filter(Resume.user_id == current.id, Resume.is_current.is_(True)).update({'is_current': False})
    resume = Resume(
        user_id=current.id,
        original_filename=file.filename,
        storage_url=url,
        extracted_text=extracted,
        is_current=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get('/resume/current', response_model=ResumeOut)
def current_resume(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current.id, Resume.is_current.is_(True))
        .order_by(Resume.created_at.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail='No current resume uploaded')
    return resume
