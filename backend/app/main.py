from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.api.tailoring import router as tailoring_router
from app.api.user_resume import router as user_router
from app.core.config import settings
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(jobs_router)
app.include_router(tailoring_router)


@app.get('/health')
def health():
    return {'status': 'ok'}
