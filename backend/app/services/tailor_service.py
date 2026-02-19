import json
import re
from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Job, Resume, TailoredResume


class TailorService:
    def __init__(self, db: Session):
        self.db = db

    def check_rate_limit(self, user_id: int) -> None:
        since = datetime.utcnow() - timedelta(hours=1)
        count = self.db.query(TailoredResume).filter(TailoredResume.user_id == user_id, TailoredResume.created_at >= since).count()
        if count >= settings.tailor_rate_limit_per_hour:
            raise ValueError('Rate limit exceeded. Please try again later.')

    def generate(self, user_id: int, job_id: int) -> TailoredResume:
        self.check_rate_limit(user_id)
        job = self.db.query(Job).filter(Job.id == job_id).first()
        resume = (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id, Resume.is_current.is_(True))
            .order_by(Resume.created_at.desc())
            .first()
        )
        if not job or not resume:
            raise ValueError('Job or current resume not found')

        result = self._mock_tailor(resume.extracted_text, job.description, job.title)

        tr = TailoredResume(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume.id,
            tailored_text=result['tailored_resume_text'],
            ats_score=result['ats_score'],
            matched_keywords_json=json.dumps(result['matched_keywords']),
            missing_keywords_json=json.dumps(result['missing_keywords']),
        )
        self.db.add(tr)
        self.db.commit()
        self.db.refresh(tr)
        return tr

    def _mock_tailor(self, resume_text: str, job_description: str, target_role: str | None = None) -> dict:
        keywords = self._extract_keywords(job_description)
        resume_words = set(self._tokenize(resume_text))
        matched = sorted([k for k in keywords if k in resume_words])
        missing = sorted([k for k in keywords if k not in resume_words])

        sections = ['Summary', 'Skills', 'Experience', 'Projects', 'Education']
        section_score = 20 if all(section.lower() in resume_text.lower() for section in sections[:3]) else 10
        coverage = int((len(matched) / max(1, len(keywords))) * 70)
        length_penalty = 0 if len(resume_text.split()) <= 700 else 10
        score = max(1, min(100, coverage + section_score - length_penalty))

        tailored = (
            f"Summary\nTarget Role: {target_role or 'Software Engineer'}\n\n"
            f"Skills\n{', '.join(matched[:12] or keywords[:8])}\n\n"
            "Experience\n"
            "- Improved API latency by 35% using async pipelines and caching.\n"
            "- Built mobile features with production-grade state management and testing.\n\n"
            "Projects\n"
            "- SmartApply: Job aggregation and ATS tailoring platform with Flutter + FastAPI.\n\n"
            "Education\n- Bachelor's Degree (or equivalent experience).\n"
        )

        return {
            'tailored_resume_text': tailored,
            'ats_score': score,
            'matched_keywords': matched,
            'missing_keywords': missing,
        }

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r'[a-zA-Z][a-zA-Z0-9+#.-]{1,}', text.lower())

    def _extract_keywords(self, text: str) -> list[str]:
        words = [w for w in self._tokenize(text) if len(w) > 2]
        stop = {'with', 'the', 'and', 'for', 'you', 'our', 'are', 'will', 'this'}
        filtered = [w for w in words if w not in stop]
        return [w for w, _ in Counter(filtered).most_common(20)]
