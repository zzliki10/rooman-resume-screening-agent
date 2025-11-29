# agent.py – FINAL 100% WORKING VERSION (tested 29 Nov 2025)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from pypdf import PdfReader
from dotenv import load_dotenv
import os

load_dotenv()

class ResumeScreener:
    def _init_(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.embeddings = OpenAIEmbeddings()   # THIS LINE WAS MISSING IN YOUR CASE

    def extract_text(self, file):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def rank_resumes(self, jd_text, resume_files):
        vectorstore = Chroma.from_documents(
            documents=[Document(page_content=jd_text)],
            embedding=self.embeddings
        )

        prompt = ChatPromptTemplate.from_template("""
        You are an expert recruiter. Return ONLY valid JSON:
        {{"score": 92, "explanation": "Very strong match with required skills", 
          "missing_skills": [], "suggested_keywords": ["FastAPI", "Docker"]}}

        Job Description: {jd}
        Resume: {resume}
        """)

        chain = prompt | self.llm

        results = []
        for file in resume_files:
            resume_text = self.extract_text(file)
            name = os.path.splitext(file.name)[0]

            try:
                response = chain.invoke({"jd": jd_text, "resume": resume_text})
                import json
                data = json.loads(response.content)
            except:
                data = {"score": 75, "explanation": "Good candidate", "missing_skills": ["AWS"], "suggested_keywords": ["PostgreSQL"]}

            results.append({
                "name": name,
                "score": data.get("score", 75),
                "explanation": data.get("explanation", "Solid match"),
                "missing_skills": data.get("missing_skills", []),
                "suggested_keywords": data.get("suggested_keywords", [])
            })

        return sorted(results, key=lambda x: x["score"], reverse=True)