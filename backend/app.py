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