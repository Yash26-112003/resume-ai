from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

print("🚀 Backend Starting...")

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "Backend Running!"

# =========================
# EXTRACT TEXT FROM PDF
# =========================
def extract_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return file.read().decode(errors="ignore").lower()

# =========================
# AI FEEDBACK (SMART LOGIC)
# =========================
def generate_ai_feedback(score, missing):
    if score > 80:
        return "🔥 Excellent resume! You are job-ready."
    elif score > 60:
        return f"👍 Good resume. Improve these skills: {', '.join(missing)}"
    else:
        return f"⚠️ Needs improvement. Learn: {', '.join(missing)} and add projects."

# =========================
# ANALYZE RESUME
# =========================
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        job_desc = request.form.get("job_desc", "").lower()

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        resume_text = extract_text(file)

        # ROLE BASED SKILLS
        if role == "software":
            skills = ["python", "flask", "sql", "api"]
        elif role == "data":
            skills = ["python", "pandas", "machine learning", "numpy"]
        elif role == "web":
            skills = ["html", "css", "javascript", "react"]
        else:
            skills = []

        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        # SIMILARITY
        similarity = 0
        if job_desc:
            docs = [resume_text, job_desc]
            cv = CountVectorizer().fit_transform(docs)
            similarity = cosine_similarity(cv)[0][1]

        skill_score = len(matched) / len(skills) if skills else 0
        final_score = int((skill_score * 0.6 + similarity * 0.4) * 100)

        suggestions = [f"Learn {s}" for s in missing]
        ai_feedback = generate_ai_feedback(final_score, missing)

        return jsonify({
            "score": final_score,
            "matched": matched,
            "missing": missing,
            "suggestions": suggestions,
            "skill_score": int(skill_score * 100),
            "similarity": int(similarity * 100),
            "ai_feedback": ai_feedback
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# PDF DOWNLOAD
# =========================
@app.route("/download", methods=["POST"])
def download():
    data = request.json

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Resume Report", ln=True)

    pdf.cell(200, 10, txt=f"Score: {data.get('score')}%", ln=True)
    pdf.cell(200, 10, txt=f"Skill Match: {data.get('skill_score')}%", ln=True)
    pdf.cell(200, 10, txt=f"JD Similarity: {data.get('similarity')}%", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Matched Skills:", ln=True)
    for s in data.get("matched", []):
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    for s in data.get("missing", []):
        pdf.cell(200, 10, txt=f"- {s}", ln=True)

    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="AI Feedback: " + data.get("ai_feedback", ""))

    file_path = "report.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

# =========================
# RUN SERVER (IMPORTANT FIX)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
