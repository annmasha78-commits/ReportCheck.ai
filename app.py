import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import re

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    .status-card { padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 6px solid; }
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
                if content: text += content + " "
        elif file.name.lower().endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode("utf-8")
        return text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_logic(text):
    t = text.lower()
    
    # Define Sections and what to look for inside them
    checks = {
        "Executive Summary": {
            "keywords": ["executive", "summary", "overview"],
            "reqs": ["impact", "risk", "scope"],
            "tip": "High-level impact aur risk level ka zikr zaroor karein."
        },
        "Methodology": {
            "keywords": ["methodology", "approach", "tools", "nmap", "zap"],
            "reqs": ["scanning", "enumeration", "tools"],
            "tip": "Step-by-step process aur tools ki details missing hain."
        },
        "Technical Findings": {
            "keywords": ["findings", "vulnerabilities", "assessment"],
            "reqs": ["cvss", "severity", "poc", "proof"],
            "tip": "Screenshots (PoC) aur CVSS scoring lazmi add karein."
        },
        "Remediation": {
            "keywords": ["remediation", "recommendations", "fixes"],
            "reqs": ["patch", "solution", "mitigation"],
            "tip": "Sirf mashwara na dein, technical fix steps bhi likhein."
        }
    }
    
    results = []
    total_score = 0
    
    for section, data in checks.items():
        found_sec = any(k in t for k in data["keywords"])
        missing_reqs = [r for r in data["reqs"] if r not in t]
        
        status = "miss"
        score = 0
        msg = "Section missing hai. Report incomplete lag rahi hai."
        
        if found_sec:
            if not missing_reqs:
                status = "prof"
                score = 25
                msg = "Zabardast! Section mukammal aur professional hai."
            else:
                status = "weak"
                score = 15
                msg = f"Section mojud hai lekin {', '.join(missing_reqs).upper()} missing hai. {data['tip']}"
        
        total_score += score
        results.append({"name": section, "status": status, "score": score, "msg": msg})
        
    return total_score, results

st.title("🛡️ Report-Check.ai (Smart Engine)")

f = st.file_uploader("Upload Pentesting Report", type=['pdf', 'docx', 'txt'])

if f:
    content = extract_text(f)
    if content:
        score, report_data = analyze_logic(content)
        
        # Summary Header
        c1, c2 = st.columns([1, 2])
        c1.metric("Audit Score", f"{score}%")
        
        if score >= 80: c2.success("Rating: A+ Professional Report")
        elif score >= 50: c2.warning("Rating: B Needs Improvement")
        else: c2.error("Rating: C Weak Structure")
        
        st.divider()
        st.subheader("Detailed Breakdown (Kami aur Khobiyan)")
        
        for res in report_data:
            st.markdown(f"""
            <div class="status-card {res['status']}">
                <h4>{res['name']} ({res['score']}/25)</h4>
                <p>{res['msg']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Document read nahi ho saka. File check karein.")
