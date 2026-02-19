from datetime import datetime

from app.models.models import Job
from app.utils.job_utils import dedupe_hash


def auth_header(client):
    reg = client.post('/auth/register', json={'name': 'A', 'email': 'a@a.com', 'password': 'Password123'})
    token = reg.json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_auth_and_me(client):
    headers = auth_header(client)
    me = client.get('/me', headers=headers)
    assert me.status_code == 200
    assert me.json()['email'] == 'a@a.com'


def test_jobs_list_and_tailor(client, db):
    headers = auth_header(client)
    # insert sample job + fake current resume
    from app.models.models import Resume, User

    user = db.query(User).filter(User.email == 'a@a.com').first()
    resume = Resume(user_id=user.id, original_filename='a.pdf', storage_url='s3://x', extracted_text='Skills\nflutter python fastapi', is_current=True)
    db.add(resume)

    h = dedupe_hash('Flutter Dev', 'ACME', 'Remote', 'https://example.com')
    db.add(
        Job(
            provider='seed',
            provider_job_id='1',
            title='Flutter Dev',
            company='ACME',
            location='Remote',
            employment_type='full-time',
            remote_type='remote',
            description='Need flutter python fastapi docker',
            apply_url='https://example.com',
            posted_at=datetime.utcnow(),
            fetched_at=datetime.utcnow(),
            dedupe_hash=h,
        )
    )
    db.commit()

    jobs = client.get('/jobs', headers=headers)
    assert jobs.status_code == 200
    assert jobs.json()['total'] == 1

    job_id = jobs.json()['items'][0]['id']
    tailor = client.post(f'/jobs/{job_id}/tailor', headers=headers)
    assert tailor.status_code == 200
    assert 'ats_score' in tailor.json()

    download = client.get(f'/jobs/{job_id}/tailored/download', headers=headers)
    assert download.status_code == 200
    assert download.headers['content-type'] == 'application/pdf'
