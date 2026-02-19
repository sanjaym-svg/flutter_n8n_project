from datetime import datetime

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.models import Job, Resume, User
from app.utils.job_utils import dedupe_hash

Base.metadata.create_all(bind=engine)
db = SessionLocal()

if not db.query(User).filter(User.email == 'demo@smartapply.dev').first():
    user = User(name='Demo User', email='demo@smartapply.dev', password_hash=hash_password('Password123'))
    db.add(user)
    db.commit()
    db.refresh(user)

    resume = Resume(
        user_id=user.id,
        original_filename='demo_resume.pdf',
        storage_url='s3://resumes/demo.pdf',
        extracted_text='Summary\nFlutter engineer with Python backend skills\nSkills\nFlutter FastAPI PostgreSQL Docker',
        is_current=True,
    )
    db.add(resume)

sample_jobs = [
    {
        'title': 'Flutter Developer',
        'company': 'Acme Labs',
        'location': 'Remote',
        'description': 'Looking for Flutter, Dart, REST API, CI/CD experience',
        'apply_url': 'https://example.com/jobs/flutter-dev',
    },
    {
        'title': 'Backend Python Engineer',
        'company': 'CloudForge',
        'location': 'Berlin',
        'description': 'FastAPI, PostgreSQL, Docker, AWS',
        'apply_url': 'https://example.com/jobs/backend-py',
    },
]

for j in sample_jobs:
    h = dedupe_hash(j['title'], j['company'], j['location'], j['apply_url'])
    if not db.query(Job).filter(Job.dedupe_hash == h).first():
        db.add(
            Job(
                provider='seed',
                provider_job_id=h[:8],
                title=j['title'],
                company=j['company'],
                location=j['location'],
                employment_type='full-time',
                remote_type='remote' if j['location'].lower() == 'remote' else 'onsite',
                description=j['description'],
                apply_url=j['apply_url'],
                posted_at=datetime.utcnow(),
                fetched_at=datetime.utcnow(),
                dedupe_hash=h,
            )
        )

db.commit()
print('Seed complete: demo@smartapply.dev / Password123')
