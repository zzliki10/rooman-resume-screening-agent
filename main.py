import streamlit as st
from agent import ResumeScreener

st.set_page_config(page_title="Rooman Resume Screener", layout="wide")
st.title("Resume Screening Agent")
st.markdown("*Rooman 48-Hour AI Challenge → Resume Screening Agent*")

screener = ResumeScreener()

jd_text = st.text_area("Paste Job Description here", height=200)
uploaded_jd = st.file_uploader("Or upload JD PDF", type=["pdf"])

resumes = st.file_uploader("Upload Candidate Resumes (Multiple PDFs)", type=["pdf"], accept_multiple_files=True)

if st.button("Rank Resumes Now", type="primary"):
    if not resumes:
        st.error("Upload at least one resume")
    elif not jd_text and not uploaded_jd:
        st.error("Provide Job Description")
    else:
        with st.spinner("Screening resumes..."):
            if uploaded_jd:
                jd_text = screener.extract_text(uploaded_jd)
            rankings = screener.rank_resumes(jd_text, resumes)

            st.success("Ranking Complete!")
            for i, r in enumerate(rankings, 1):
                with st.expander(f"#{i} → {r['name']} → {r['score']}/100", expanded=i<=3):
                    st.write("*Explanation:*", r['explanation'])
                    if r['missing_skills']:
                        st.write("*Missing Skills:*", ", ".join(r['missing_skills']))
                    if r['suggested_keywords']:
                        st.write("*Add Keywords:*", ", ".join(r['suggested_keywords']))