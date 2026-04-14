from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, json, uuid
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

USER_DB = "users.json"
REPORT_DIR = "reports"

# Create folders/files
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "🚀 SaaS Backend Running!"

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]

    users = json.load(open(USER_DB))

    if email in users:
        return jsonify({"error": "User already exists"}), 400

    users[email] = {"password": password, "reports": []}
    json.dump(users, open(USER_DB, "w"))

    return jsonify({"msg": "Signup successful"})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    users = json.load(open(USER_DB))

    if email not in users or users[email]["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"msg": "Login success"})

# ---------------- TEXT EXTRACT ----------------
def extract_text(file):
    try:
        pdf = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        return text.lower()
    except:
        return file.read().decode(errors="ignore").lower()

# ---------------- ANALYZE ----------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        jd = request.form.get("job_desc", "").lower()
        email = request.form.get("email")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        resume_text = extract_text(file)

        skills_map = {
            "software": ["python", "flask", "sql", "api"],
            "data": ["python", "pandas", "numpy", "machine learning"],
            "web": ["html", "css", "javascript", "react"]
        }

        skills = skills_map.get(role, [])

        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        similarity = 0
        if jd:
            cv = CountVectorizer().fit_transform([resume_text, jd])
            similarity = cosine_similarity(cv)[0][1]

        skill_score = len(matched) / len(skills) if skills else 0
        final_score = int((skill_score * 0.6 + similarity * 0.4) * 100)

        suggestions = [f"Learn {s}" for s in missing]

        result = {
            "score": final_score,
            "matched": matched,
            "missing": missing,
            "suggestions": suggestions,
            "skill_score": int(skill_score * 100),
            "similarity": int(similarity * 100)
        }

        # Save report
        if email:
            users = json.load(open(USER_DB))
            if email in users:
                users[email]["reports"].append(result)
                json.dump(users, open(USER_DB, "w"))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["POST"])
def dashboard():
    email = request.json["email"]
    users = json.load(open(USER_DB))
    return jsonify(users.get(email, {}).get("reports", []))

# ---------------- PDF DOWNLOAD ----------------
@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.json

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, "AI Resume Report", ln=True)
        pdf.cell(200, 10, f"Score: {data.get('score',0)}%", ln=True)
        pdf.cell(200, 10, f"Skill Score: {data.get('skill_score',0)}%", ln=True)
        pdf.cell(200, 10, f"JD Similarity: {data.get('similarity',0)}%", ln=True)

        pdf.ln(5)

        pdf.cell(200, 10, "Matched Skills:", ln=True)
        pdf.multi_cell(0, 10, ", ".join(data.get("matched", [])))

        pdf.ln(5)

        pdf.cell(200, 10, "Missing Skills:", ln=True)
        pdf.multi_cell(0, 10, ", ".join(data.get("missing", [])))

        filename = f"report_{uuid.uuid4()}.pdf"
        filepath = os.path.join(REPORT_DIR, filename)

        pdf.output(filepath)

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
