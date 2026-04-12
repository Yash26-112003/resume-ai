from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import extract_text
from matcher import match_resume

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "AI Resume Screening Backend Running!"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['resume']
        file.save("resume.pdf")

        text = extract_text("resume.pdf")
        results = match_resume(text)

        return jsonify({
            "matched_skills": results["matched_skills"],
            "missing_skills": results["missing_skills"],
            "score": results["score"],
            "role": results["best_role"]
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

@app.route('/')
def home():
    return "AI Resume Screening API is running 🚀"