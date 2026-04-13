from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2

app = Flask(**name**)
CORS(app)

@app.route('/')
def home():
return "Backend Running!"

def extract_text(file):
try:
pdf = PyPDF2.PdfReader(file)
text = ""
for page in pdf.pages:
text += page.extract_text() or ""
return text.lower()
except:
return file.read().decode(errors='ignore').lower()

@app.route('/upload', methods=['POST'])
def upload():

```
file = request.files.get('resume')
role = request.form.get('role')
job_desc = request.form.get('job_desc', "").lower()

if not file:
    return jsonify({"error": "No file uploaded"}), 400

resume_text = extract_text(file)

# 🎯 ROLE BASED SKILLS
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

# ✅ MATCHING
matched = [s for s in skills if s in resume_text]
missing = [s for s in skills if s not in resume_text]

# 📊 SIMILARITY
similarity_score = 0
if job_desc:
    documents = [resume_text, job_desc]
    cv = CountVectorizer().fit_transform(documents)
    similarity_score = cosine_similarity(cv)[0][1]

# 📊 FINAL SCORE
skill_score = (len(matched) / len(skills)) if skills else 0
final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

suggestions = [f"Learn {s}" for s in missing]

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
```

if **name** == "**main**":
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
