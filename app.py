import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document
import re

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

# Styling
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
            # pdfplumber scanned aur messy text ke liye best hai
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    content = page.extract_text()
                    if content:
                        text += content + " "
        elif file.name.lower().endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode("utf-8", errors="ignore")
        
        # Cleanup: Non-ASCII characters aur extra spaces hatana
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        return " ".join(text.split())
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_logic(text):
    t = text.lower()
    
    # Super Flexible AI Patterns
    checks = {
        "Executive Summary": {
            "patterns": [r"summary", r"overview", r"introduction", r"objective"],
            "reqs": [r"risk", r"impact", r"scope", r"critical"],
            "tip": "Report mein risk level aur impact ka zikr karein."
        },
        "Methodology": {
            "patterns": [r"method", r"approach", r"tools", r"step", r"recon", r"nmap"],
            "reqs": [r"scan", r"zap", r"tool", r"enumeration", r"nikto", r"gobuster"],
            "tip": "Pentesting tools (Nmap, ZAP etc) aur scanning steps add karein."
        },
        "Technical Findings": {
            "patterns": [r"finding", r"vulnerabilit", r"result", r"issue", r"assessment", r"weakness"],
            "reqs": [r"severity", r"low", r"medium", r"high", r"poc", r"proof", r"screenshot"],
            "tip": "Har vulnerability ke saath uska Proof (PoC) aur severity lazmi add karein."
        },
        "Remediation": {
            "patterns": [r"remediation", r"fix", r"recommend", r"mitigation", r"conclusion", r"action"],
            "reqs": [r"patch", r"update", r"solution", r"prevent", r"secure"],
            "tip": "Sirf description nahi, technical patching aur fixing steps batayein."
        }
    }
    
    results = []
    total_score = 0
    
    for section, data in checks.items():
        # Step 1: Check if Section Header or related keywords exist
        found_sec = any(re.search(p, t) for p in data["patterns"])
        
        # Step 2: Check for mandatory content anywhere in the text
        found_reqs = [r for r in data["reqs"] if re.search(r, t)]
        match_ratio = len(found_reqs) / len(data["reqs"])
        
        status = "miss"
        score = 0
        msg = f"{section} ka data nahi mil saka. Heading ya keywords check karein."
        
        if found_sec or match_ratio > 0.3:  # Agar section heading na bhi mile magar content ho
            if match_ratio >= 0.7:
                status = "prof"
                score = 25
                msg = f"Zabardast! {section} ka content professional aur mukammal hai."
            else:
                status = "weak"
                score = 15
                msg = f"{section} mojud hai magar details kam hain. {data['tip']}"
        
        total_score += score
        results.append({"name": section, "status": status, "score": score, "msg": msg})
        
    return total_score, results

# UI Application
st.title("🛡️ Report-Check.ai Pro (v2.0)")
st.write("Smart Engine for Pentesting Report Audit")

f = st.file_uploader("Upload Pentesting Report (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

if f:
    with st.spinner("Analyzing document structure..."):
        content = extract_text(f)
        
        if len(content) > 50:
            score, report_data = analyze_logic(content)
            
            c1, c2 = st.columns([1, 2])
            c1.metric("Audit Score", f"{score}%")
            
            if score >= 80: c2.success("Rating: Grade A - Professional")
            elif score >= 50: c2.warning("Rating: Grade B - Needs Work")
            else: c2.error("Rating: Grade C - Incomplete")
            
            st.divider()
            for res in report_data:
                st.markdown(f"""
                <div class="status-card {res['status']}">
                    <h4>{res['name']} ({res['score']}/25)</h4>
                    <p>{res['msg']}</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Quick Check for Scanned Files
            if "camscanner" in content.lower():
                st.info("💡 Note: CamScanner detect hua hai. Engine ne text extract karne ki poori koshish ki hai.")
        else:
            st.error("Text extract nahi ho saka! Ye PDF shayad 'Image' hai. Meharbani karke direct PDF export use karein ya Word file upload karein.")
