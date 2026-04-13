from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend Running!"

# 🔥 Extract text from PDF
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files.get('resume')
    role = request.form.get('role')
    job_desc = request.form.get('job_desc', "")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # 📄 Extract text
    resume_text = extract_text(file)

    # 🎯 Role-based skills
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

    # ✅ Skill matching
    matched = [s for s in skills if s in resume_text]
    missing = [s for s in skills if s not in resume_text]

    # 🧠 Similarity
    similarity_score = 0
    if job_desc:
        documents = [resume_text, job_desc.lower()]
        cv = CountVectorizer().fit_transform(documents)
        similarity_score = cosine_similarity(cv)[0][1]

    # 📊 Score
    skill_score = (len(matched) / len(skills)) if skills else 0
    final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

    # 💡 Suggestions
   suggestions = []

if missing:
    suggestions.append("Improve missing technical skills")

for s in missing:
    suggestions.append(f"Add {s} projects to your resume")

if similarity_score < 0.5:
    suggestions.append("Resume not aligned with job description")

if final_score < 50:
    suggestions.append("Add more relevant experience and keywords")

   return jsonify({
    "role": role_name,
    "score": final_score,
    "matched_skills": matched,
    "missing_skills": missing,
    "similarity": round(similarity_score * 100, 2),
    "suggestions": suggestions,
    "skill_score": int(skill_score * 100),
    "similarity_score": int(similarity_score * 100)
})

# ✅ IMPORTANT for Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
