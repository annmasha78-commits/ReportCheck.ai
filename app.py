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
    .status-card { padding: 20px; border-radius: 12px; margin: 10px 0; border-left: 8px solid; }
    .prof { background-color: #064e3b; border-color: #10b981; }
    .weak { background-color: #451a03; border-color: #f59e0b; }
    .miss { background-color: #450a0a; border-color: #ef4444; }
    h4 { margin: 0; color: white; }
    p { margin: 5px 0 0 0; opacity: 0.9; }
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
                    # Noise cleaning: extra spaces aur tabs ko theek karna
                    clean_content = re.sub(r'\s+', ' ', content)
                    text += clean_content + " "
        elif file.name.lower().endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = file.read().decode("utf-8", errors="ignore")
        return text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_logic(text):
    t = text.lower()
    
    # Flexible Patterns: Ab ye exact word nahi balki milti julti headings dhoonde ga
    checks = {
        "Executive Summary": {
            "pattern": r"(executive\s*summary|overview|introduction|summary|project\s*scope)",
            "reqs": {"impact": r"impact|criticality|risk\s*level", "scope": r"scope|target|objective"},
            "tip": "High-level impact aur risk level ka zikr zaroor karein."
        },
        "Methodology": {
            "pattern": r"(methodology|approach|tools|assessment\s*steps|reconnaissance|process)",
            "reqs": {"scanning": r"nmap|scan|enumeration", "tools": r"zap|burp|nikto|tools"},
            "tip": "Step-by-step process aur tools (Nmap, ZAP etc) ki details missing hain."
        },
        "Technical Findings": {
            "pattern": r"(findings|vulnerabilities|technical\s*assessment|results|issues|weakness)",
            "reqs": {"severity": r"low|medium|high|critical|severity", "proof": r"poc|proof|screenshot|evidence|description"},
            "tip": "Vulnerabilities ki detail aur Proof of Concept (PoC) lazmi add karein."
        },
        "Remediation": {
            "pattern": r"(remediation|recommendations|fixes|conclusion|mitigation|actions)",
            "reqs": {"patch": r"patch|fix|update|solution", "mitigation": r"mitigation|prevent"},
            "tip": "Sirf mashwara na dein, technical fix steps bhi likhein."
        }
    }
    
    results = []
    total_score = 0
    
    for section, data in checks.items():
        # Check if section header exists (using Regex for flexibility)
        found_sec = re.search(data["pattern"], t)
        
        # Check for mandatory requirements inside the whole text
        missing_reqs = []
        for req_name, pattern in data["reqs"].items():
            if not re.search(pattern, t):
                missing_reqs.append(req_name)
        
        status = "miss"
        score = 0
        msg = f"{section} section nahi mil saka. Heading sahi se likhein."
        
        if found_sec:
            if not missing_reqs:
                status = "prof"
                score = 25
                msg = f"Zabardast! {section} section mukammal aur professional hai."
            else:
                status = "weak"
                score = 15
                msg = f"{section} mojud hai lekin {', '.join(missing_reqs).upper()} ka zikr kam hai. {data['tip']}"
        
        total_score += score
        results.append({"name": section, "status": status, "score": score, "msg": msg})
        
    return total_score, results

# UI Logic
st.title("🛡️ Report-Check.ai (Smart Engine)")
st.write("Professional Pentesting Report Analyzer")

f = st.file_uploader("Upload Pentesting Report (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

if f:
    with st.spinner('Report scan ho rahi hai...'):
        content = extract_text(f)
        
        if content and len(content) > 50:
            score, report_data = analyze_logic(content)
            
            # Summary Header
            c1, c2 = st.columns([1, 2])
            c1.metric("Audit Score", f"{score}%")
            
            if score >= 85: 
                c2.success("Rating: A+ Professional Report")
            elif score >= 60: 
                c2.warning("Rating: B Needs Improvement")
            else: 
                c2.error("Rating: C Weak Structure / Incomplete")
            
            st.divider()
            st.subheader("Detailed Breakdown (Kami aur Khobiyan)")
            
            for res in report_data:
                st.markdown(f"""
                <div class="status-card {res['status']}">
                    <h4>{res['name']} ({res['score']}/25)</h4>
                    <p>{res['msg']}</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Extra Tip for Scanned Documents
            if "camscanner" in content.lower():
                st.info("💡 Note: Ye report scanned lag rahi hai. Behtar results ke liye direct Word se PDF banayein.")
                
        else:
            st.error("Document read nahi ho saka ya text bohot kam hai. Check karein ke PDF image-only (scanned) to nahi?")
