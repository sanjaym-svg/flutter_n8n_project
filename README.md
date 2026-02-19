# SmartApply (Flutter + FastAPI + PostgreSQL)

SmartApply is an end-to-end job application assistant with:
- JWT auth (register/login)
- Master resume upload (PDF/DOCX) + text extraction
- Multi-provider job sync with pluggable adapters
- Job feed and detail views
- ATS-tailored resume generation per job
- Tailored resume PDF download

## Monorepo structure

```
backend/                 # FastAPI API
  app/
    api/                 # route handlers
    providers/           # JobProvider interface + adapters
    services/            # job sync, storage, tailoring
    models/              # SQLAlchemy models
    schemas/             # Pydantic contracts
    utils/               # parsing, sanitizing, hashing, PDF export
  tests/
  scripts/seed_dev.py
flutter_app/             # Flutter mobile app (Riverpod)
docker-compose.yml       # api + postgres + minio
```

## Quickstart

### 1) Backend + infra

```bash
cp backend/.env.example backend/.env
docker compose up --build -d
```

Run seed script:
```bash
docker compose exec api python scripts/seed_dev.py
```

API docs:
- http://localhost:8000/docs

### 2) Flutter app

```bash
cd flutter_app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

For iOS simulator use `http://localhost:8000`.

## Environment variables

- `DATABASE_URL`
- `JWT_SECRET`
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `BUCKET_NAME`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `LLM_MODE=mock|live`
- `LLM_API_KEY` (optional)

## API endpoints

### Auth
- `POST /auth/register`
- `POST /auth/login`

### User/Resume
- `GET /me`
- `POST /resume/upload` (multipart)
- `GET /resume/current`

### Jobs
- `POST /jobs/sync`
- `GET /jobs`
- `GET /jobs/{jobId}`

### Tailoring
- `POST /jobs/{jobId}/tailor`
- `GET /jobs/{jobId}/tailored`
- `GET /jobs/{jobId}/tailored/download`

## Adding job providers

1. Implement `JobProvider` in `backend/app/providers/base.py`.
2. Create new adapter in `backend/app/providers/`.
3. Register adapter in `JobService.providers`.
4. Keep provider failures isolated so others continue.

## Testing

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Flutter:
```bash
cd flutter_app
flutter test
```

## Security notes
- Password hashing via bcrypt
- JWT-based auth
- Resume upload validation (PDF/DOCX + size cap)
- Resume text is never printed in logs
- Tailoring endpoint includes basic per-hour rate limiting
- No unsafe scraping; providers use API/public endpoints only
