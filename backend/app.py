from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "AI Resume Screening Backend Running!"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']

    # Dummy response (for testing)
    return jsonify({
        "score": 85,
        "role": "Software Developer",
        "matched_skills": ["Python", "Flask"],
        "missing_skills": ["Docker", "AWS"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

@app.route('/')
def home():
    return "AI Resume Screening API is running 🚀"