from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, json, uuid
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.json"

# ---------------- INIT ----------------
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    return json.load(open(USERS_FILE))

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"))

# ---------------- HOME ----------------
@app.route("/")
def home():
    return "🚀 SaaS Backend Running!"

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_users()

    email = data.get("email")
    password = data.get("password")

    if email in users:
        return jsonify({"error": "User exists"}), 400

    users[email] = {"password": password, "reports": []}
    save_users(users)

    return jsonify({"message": "Registered"})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()

    email = data.get("email")
    password = data.get("password")

    if email not in users or users[email]["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login success"})

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

# ---------------- AI FEEDBACK ----------------
def generate_ai_feedback(score, missing):
    if score > 80:
        return "🔥 Excellent resume! You are job-ready."
    elif score > 60:
        return f"👍 Good resume. Improve: {', '.join(missing)}"
    else:
        return f"⚠️ Improve skills: {', '.join(missing)} and add projects."

# ---------------- ANALYZE ----------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("resume")
        role = request.form.get("role")
        job_desc = request.form.get("job_desc", "").lower()
        email = request.form.get("email")

        if not file:
            return jsonify({"error": "No file"}), 400

        resume_text = extract_text(file)

        skills_map = {
            "software": ["python","flask","sql","api"],
            "data": ["python","pandas","machine learning","numpy"],
            "web": ["html","css","javascript","react"]
        }

        skills = skills_map.get(role, [])

        matched = [s for s in skills if s in resume_text]
        missing = [s for s in skills if s not in resume_text]

        similarity = 0
        if job_desc:
            docs = [resume_text, job_desc]
            cv = CountVectorizer().fit_transform(docs)
            similarity = cosine_similarity(cv)[0][1]

        skill_score = len(matched)/len(skills) if skills else 0
        final_score = int((skill_score*0.6 + similarity*0.4)*100)

        ai_feedback = generate_ai_feedback(final_score, missing)

        result = {
            "score": final_score,
            "matched": matched,
            "missing": missing,
            "skill_score": int(skill_score*100),
            "similarity": int(similarity*100),
            "ai_feedback": ai_feedback
        }

        # SAVE REPORT
        if email:
            users = load_users()
            if email in users:
                users[email]["reports"].append(result)
                save_users(users)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- GET REPORTS ----------------
@app.route("/get_reports")
def get_reports():
    email = request.args.get("email")
    users = load_users()

    if email in users:
        return jsonify(users[email]["reports"])
    return jsonify([])

# ---------------- PDF ----------------
@app.route("/download", methods=["POST"])
def download():
    data = request.json

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200,10,"AI Resume Report", ln=True)
    pdf.cell(200,10,f"Score: {data['score']}%", ln=True)

    pdf.cell(200,10,"Matched Skills:", ln=True)
    for s in data["matched"]:
        pdf.cell(200,10,f"- {s}", ln=True)

    pdf.cell(200,10,"Missing Skills:", ln=True)
    for s in data["missing"]:
        pdf.cell(200,10,f"- {s}", ln=True)

    pdf.multi_cell(0,10,"AI Feedback: "+data["ai_feedback"])

    filename = f"report_{uuid.uuid4()}.pdf"
    pdf.output(filename)

    return send_file(filename, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
