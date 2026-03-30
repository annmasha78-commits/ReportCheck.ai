import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import re

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    .status-card { padding: 18px; border-radius: 10px; margin: 8px 0; border-left: 6px solid; }
    .prof { background-color: #064e3b; border-color: #10b981; }
    .weak { background-color: #451a03; border-color: #f59e0b; }
    .miss { background-color: #450a0a; border-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

def extract_text(file):
    text = ""
    try:
        if file.name.lower().endswith('.pdf'):
            pdf = PdfReader(file)
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    # CamScanner noise cleaning
                    text += content + " "
        elif file.name.lower().endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode("utf-8", errors="ignore")
        
        # Sab se important: clean extra newlines and special characters
        text = re.sub(r'[^\x00-\x7F]+', ' ', text) # Remove non-ascii
        return " ".join(text.split())
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_logic(text):
    t = text.lower()
    
    # AI-style logic: Ye sirf word nahi, balki context dhoonde ga
    checks = {
        "Executive Summary": {
            "patterns": [r"executiv", r"summary", r"overview", r"introduction"],
            "reqs": [r"impact", r"risk", r"scope", r"high"],
            "tip": "Impact aur Risk level ka zikr zaroor karein."
        },
        "Methodology": {
            "patterns": [r"method", r"approach", r"tools", r"step", r"recon"],
            "reqs": [r"nmap", r"scan", r"zap", r"tool", r"enumeration"],
            "tip": "Step-by-step process aur scanner tools add karein."
        },
        "Technical Findings": {
            "patterns": [r"finding", r"vulnerabilit", r"result", r"issue", r"assessment"],
            "reqs": [r"severity", r"low", r"medium", r"high", r"poc", r"proof"],
            "tip": "Screenshots aur CVSS scoring lazmi add karein."
        },
        "Remediation": {
            "patterns": [r"remediation", r"fix", r"recommend", r"mitigation", r"conclusion"],
            "reqs": [r"patch", r"update", r"solution", r"prevent"],
            "tip": "Sirf description nahi, technical fix steps bhi likhein."
        }
    }
    
    results = []
    total_score = 0
    
    for section, data in checks.items():
        # Check if ANY of the section patterns exist
        found_sec = any(re.search(p, t) for p in data["patterns"])
        
        # Check requirements anywhere in the report (more flexible)
        found_reqs = [r for r in data["reqs"] if re.search(r, t)]
        missing_count = len(data["reqs"]) - len(found_reqs)
        
        status = "miss"
        score = 0
        msg = f"{section} section missing lag raha hai."
        
        if found_sec:
            if missing_count == 0:
                status = "prof"
                score = 25
                msg = "Perfect! Ye section professional hai."
            elif missing_count <= 2:
                status = "weak"
                score = 15
                msg = f"Section mojud hai lekin kuch details kam hain. {data['tip']}"
            else:
                status = "weak"
                score = 10
                msg = f"Heading mili hai magar content bohot weak hai."
        
        total_score += score
        results.append({"name": section, "status": status, "score": score, "msg": msg})
        
    return total_score, results

st.title("🛡️ Report-Check.ai Pro")
st.write("Auditing your Cybersecurity Reports...")

f = st.file_uploader("Upload Report", type=['pdf', 'docx', 'txt'])

if f:
    content = extract_text(f)
    if len(content) > 100:
        score, report_data = analyze_logic(content)
        
        c1, c2 = st.columns([1, 2])
        c1.metric("Overall Score", f"{score}%")
        
        if score >= 75: c2.success("Rating: Professional")
        elif score >= 50: c2.warning("Rating: Needs Improvement")
        else: c2.error("Rating: Weak / Incomplete")
        
        st.divider()
        for res in report_data:
            st.markdown(f'<div class="status-card {res["status"]}"><h4>{res["name"]}</h4><p>{res["msg"]}</p></div>', unsafe_allow_html=True)
    else:
        st.error("Text detect nahi ho saka. Agar file scanned hai to direct Word file upload karein.")
