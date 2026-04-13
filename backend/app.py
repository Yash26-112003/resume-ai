from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import PyPDF2
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route('/')
def home():
    return "Backend Running!"

# -------------------------------
# EXTRACT TEXT FROM PDF
# -------------------------------
def extract_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

        return text.lower()

    except:
        return file.read().decode(errors='ignore').lower()

# -------------------------------
# SIMILARITY (AI)
# -------------------------------
def calculate_similarity(resume_text, job_desc):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume_text, job_desc])
    return cosine_similarity(vectors)[0][1]

# -------------------------------
# AI FEEDBACK
# -------------------------------
def generate_feedback(score, missing_skills):
    feedback = []

    if score > 80:
        feedback.append("Excellent resume! You are job ready.")
    elif score > 60:
        feedback.append("Good resume but needs improvement.")
    else:
        feedback.append("Resume needs significant improvement.")

    for skill in missing_skills:
        feedback.append(f"Add projects related to {skill}")

    return feedback

# -------------------------------
# PDF REPORT
# -------------------------------
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Resume Report", ln=True)
    pdf.cell(200, 10, txt=f"Score: {data['score']}%", ln=True)
    pdf.cell(200, 10, txt=f"Role: {data['role']}", ln=True)

    pdf.cell(200, 10, txt="Matched Skills:", ln=True)
    for s in data["matched_skills"]:
        pdf.cell(200, 10, txt=s, ln=True)

    pdf.output("report.pdf")

# -------------------------------
# MAIN API
# -------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('resume')
        role = request.form.get('role')
        job_desc = request.form.get('job_desc', "").lower()

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        resume_text = extract_text(file)

        # -------------------------------
        # ROLE BASED SKILLS
        # -------------------------------
        if role == "software":
            skills = ["python", "flask", "sql", "api"]
            role_name = "Software Engineer"

        elif role == "data":
            skills = ["python", "pandas", "machine learning", "numpy"]
            role_name = "Data Scientist"

        elif role == "web":
            skills = ["html", "css", "javascript", "react"]
            role_name = "Web Developer"

        else:
            skills = []
            role_name = "Unknown"

        # -------------------------------
        # MATCHING
        # -------------------------------
        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        # -------------------------------
        # SIMILARITY
        # -------------------------------
        similarity_score = 0
        if job_desc:
            similarity_score = calculate_similarity(resume_text, job_desc)

        # -------------------------------
        # FINAL SCORE
        # -------------------------------
        skill_score = (len(matched) / len(skills)) if skills else 0
        final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

        suggestions = [f"Learn {s}" for s in missing]

        feedback = generate_feedback(final_score, missing)

        # Optional PDF
        # generate_pdf({...})  # you can enable if needed

        return jsonify({
            "role": role_name,
            "score": final_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "similarity": round(similarity_score * 100, 2),
            "suggestions": suggestions,
            "skill_score": int(skill_score * 100),
            "similarity_score": int(similarity_score * 100),
            "feedback": feedback
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------
# RUN SERVER (VERY IMPORTANT)
# -------------------------------
if __name__ == "__main__":
    print("🚀 Backend Starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
