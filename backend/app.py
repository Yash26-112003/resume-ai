from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2

app = Flask(__name__)
CORS(app)

# ✅ Test route
@app.route('/')
def home():
    return "Backend Running!"

# ✅ Extract text
def extract_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return file.read().decode(errors="ignore").lower()

# ✅ Main API
@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('resume')
        role = request.form.get('role', 'software')
        job_desc = request.form.get('job_desc', '').lower()

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

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

        # ✅ Matching
        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        # ✅ Similarity
        similarity_score = 0
        if job_desc:
            docs = [resume_text, job_desc]
            cv = CountVectorizer().fit_transform(docs)
            similarity_score = cosine_similarity(cv)[0][1]

        # ✅ Scores
        skill_score = (len(matched) / len(skills)) if skills else 0
        final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

        # ✅ Suggestions
        suggestions = [f"Learn {s}" for s in missing]

        # ✅ Feedback
        if final_score > 80:
            feedback = "Excellent resume! You're job ready 🚀"
        elif final_score > 60:
            feedback = "Good resume. Improve missing skills."
        else:
            feedback = "Resume needs improvement. Add projects for missing skills."

        return jsonify({
            "role": role_name,
            "score": final_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "suggestions": suggestions,
            "skill_score": int(skill_score * 100),
            "similarity_score": int(similarity_score * 100),
            "feedback": feedback
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Backend Starting...")
    app.run(host="0.0.0.0", port=10000)
