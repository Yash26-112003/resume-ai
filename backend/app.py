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

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

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
        return jsonify({"error": "No file uploaded"}), 400

    return jsonify({
        "score": 90,
        "role": "Software Engineer",
        "matched_skills": ["Python", "Flask", "HTML"],
        "missing_skills": ["Docker", "AWS"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
