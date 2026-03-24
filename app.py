import os
from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

# Scoring Criteria
CRITERIA = {
    "Vulnerabilities": ["sql injection", "xss", "csrf", "rce", "idor", "lfi", "brute force"],
    "Sections": ["executive summary", "methodology", "remediation", "poc", "severity"],
}

def analyze_logic(text):
    text = text.lower()
    found_vulns = [v for v in CRITERIA["Vulnerabilities"] if v in text]
    found_sections = [s for s in CRITERIA["Sections"] if s in text]
    
    # Logic: Har section ke 10 points, har vuln ke 10 points
    score = (len(found_sections) * 10) + (len(found_vulns) * 10)
    score = min(score, 100) # Max 100
    
    # Improvements
    missing = [s.capitalize() for s in CRITERIA["Sections"] if s not in text]
    
    return {
        "score": score,
        "found_vulns": found_vulns,
        "missing_sections": missing,
        "status": "Perfect" if score > 80 else "Needs Work"
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files: return redirect('/')
    file = request.files['file']
    if file.filename == '': return redirect('/')
    
    content = file.read().decode('utf-8', errors='ignore')
    results = analyze_logic(content)
    return render_template('index.html', results=results, filename=file.filename)

if __name__ == '__main__':
    app.run(debug=True)