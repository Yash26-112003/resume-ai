@app.route("/")
def home():
    return "🚀 AI Resume Backend Running!"

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

# ================= PDF TEXT =================
def extract_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return file.read().decode(errors="ignore").lower()

# ================= ANALYZE =================
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        job_desc = request.form.get("job_desc", "").lower()

        if not file:
            return jsonify({"error": "No file"}), 400

        resume_text = extract_text(file)

        # Role-based skills
        roles = {
            "software": ["python", "flask", "sql", "api"],
            "data": ["python", "pandas", "machine learning", "numpy"],
            "web": ["html", "css", "javascript", "react"]
        }

        skills = roles.get(role, [])
        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        similarity_score = 0
        if job_desc:
            docs = [resume_text, job_desc]
            cv = CountVectorizer().fit_transform(docs)
            similarity_score = cosine_similarity(cv)[0][1]

        skill_score = len(matched) / len(skills) if skills else 0
        final_score = int((skill_score * 0.6 + similarity_score * 0.4) * 100)

        return jsonify({
            "score": final_score,
            "role": role,
            "matched": matched,
            "missing": missing,
            "skill_score": int(skill_score * 100),
            "similarity": int(similarity_score * 100),
            "suggestions": [f"Learn {s}" for s in missing]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= PDF REPORT =================
@app.route("/download", methods=["POST"])
def download():
    data = request.json

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="AI Resume Report", ln=True)

    pdf.cell(200, 10, txt=f"Score: {data['score']}%", ln=True)
    pdf.cell(200, 10, txt=f"Role: {data['role']}", ln=True)

    pdf.cell(200, 10, txt="Matched Skills:", ln=True)
    for s in data["matched"]:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    for s in data["missing"]:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    file_path = "report.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
