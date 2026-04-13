from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend Running!"

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend Running!"

@app.route('/upload', methods=['POST'])
def upload():

    file = request.files.get('resume')
    role = request.form.get('role')
    job_desc = request.form.get('job_desc', "")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    # Extract text
    resume_text = extract_text(file)

    # Role-based skills
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

    # Matching
    matched = [s for s in skills if s in resume_text]
    missing = [s for s in skills if s not in resume_text]

    # Similarity
    similarity_score = 0
    if job_desc:
        documents = [resume_text, job_desc.lower()]
        cv = CountVectorizer().fit_transform(documents)
        similarity_score = cosine_similarity(cv)[0][1]

    # Final score
    skill_score = (len(matched) / len(skills)) if skills else 0
    final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

    suggestions = [f"Learn {s}" for s in missing]

    return jsonify({
        "role": role_name,
        "score": final_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "similarity": round(similarity_score * 100, 2),
        "suggestions": suggestions
    })

    # 🔥 READ FILE CONTENT
    content = file.read().decode(errors='ignore').lower()

    # 🎯 ROLE-BASED SKILLS
    if role == "software":
        required_skills = ["python", "flask", "sql", "api"]
        role_name = "Software Engineer"

    elif role == "data":
        required_skills = ["python", "pandas", "machine learning", "numpy"]
        role_name = "Data Scientist"

    elif role == "web":
        required_skills = ["html", "css", "javascript", "react"]
        role_name = "Web Developer"

    else:
        required_skills = []
        role_name = "Unknown"

    # ✅ MATCHING LOGIC
    matched = [skill for skill in required_skills if skill in content]
    missing = [skill for skill in required_skills if skill not in content]

    # 📊 SCORE
    score = int((len(matched) / len(required_skills)) * 100) if required_skills else 0

    return jsonify({
        "role": role_name,
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing
    })

if __name__ == '__main__':
    app.run(debug=True)
    if 'resume' not in request.files:

    return jsonify({
        "score": 90,
        "role": "Software Engineer",
        "matched_skills": ["Python", "Flask", "HTML"],
        "missing_skills": ["Docker", "AWS"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
