from sentence_transformers import SentenceTransformer
import numpy as np
from pypdf import PdfReader
import os

class ResumeScreener:
    def __init__(self):
        # Load a lightweight sentence-transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text(self, file):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def extract_keywords(self, text, top_k=10):
        # Very basic keyword extraction: top frequent words ignoring stopwords
        import re
        from collections import Counter

        stopwords = set([
            'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'with', 'on',
            'as', 'by', 'an', 'at', 'from', 'or', 'this', 'that', 'be', 'are',
            'have', 'has', 'it', 'we', 'our', 'but', 'if', 'you', 'not'
        ])
        words = re.findall(r'\b\w+\b', text.lower())
        words = [w for w in words if w not in stopwords and len(w) > 2]
        counter = Counter(words)
        keywords = [word for word, count in counter.most_common(top_k)]
        return keywords

    def rank_resumes(self, jd_text, resume_files):
        jd_text = jd_text.lower()
        jd_embedding = self.model.encode([jd_text])[0]
        jd_keywords = set(self.extract_keywords(jd_text, top_k=20))

        results = []

        for file in resume_files:
            resume_text = self.extract_text(file).lower()
            resume_embedding = self.model.encode([resume_text])[0]

            # Cosine similarity score between JD and resume embeddings
            similarity = np.dot(jd_embedding, resume_embedding) / (np.linalg.norm(jd_embedding) * np.linalg.norm(resume_embedding))
            score = round(similarity * 100, 2)

            # Keyword matching
            resume_keywords = set(self.extract_keywords(resume_text, top_k=30))
            missing_skills = sorted(list(jd_keywords - resume_keywords))
            suggested_keywords = sorted(list(resume_keywords - jd_keywords))[:5]

            name = os.path.splitext(file.name)[0]

            explanation = (
                f"Resume matches {len(jd_keywords) - len(missing_skills)} out of {len(jd_keywords)} key skills."
            )

            results.append({
                "name": name,
                "score": score,
                "explanation": explanation,
                "missing_skills": missing_skills,
                "suggested_keywords": suggested_keywords
            })

        # Sort by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)

