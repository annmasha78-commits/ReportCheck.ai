import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import matplotlib.pyplot as plt
import re
import io

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

# Dark Futuristic UI
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    .stMetric { background: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .success-box { padding: 10px; background-color: #064e3b; border-radius: 5px; margin: 5px 0; }
    .error-box { padding: 10px; background-color: #7f1d1d; border-radius: 5px; margin: 5px 0; }
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
        return text.replace('\x00', '') # Remove null bytes
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_logic(text):
    t = text.lower()
    
    # Boht zyada flexible keywords taake koi bhi report miss na ho
    checks = {
        "Executive Summary": ["executive", "summary", "overview", "introduction"],
        "Methodology": ["methodology", "scope", "approach", "tools", "engagement", "testing"],
        "Technical Findings": ["findings", "vulnerabilities", "technical", "analysis", "results", "assessment"],
        "Remediation": ["remediation", "recommendations", "mitigation", "strategic", "fixes", "solutions"]
    }
    
    found = []
    for section, keywords in checks.items():
        # Agar koi bhi keyword text mein kahin bhi mil jaye
        if any(re.search(rf"\b{k}\b", t) for k in keywords) or any(k in t for k in keywords):
            found.append(section)
            
    score = len(found) * 25
    
    # Vuln Keywords
    vuln_list = ["sql", "xss", "rce", "idor", "leak", "bypass", "broken", "exposure"]
    detected = [v.upper() for v in vuln_list if v in t]
    
    return score, found, list(checks.keys()), list(set(detected))

st.title("🛡️ Report-Check.ai (Stable Engine)")
tab1, tab2 = st.tabs(["🔍 Analyzer", "🏆 Leaderboard"])

with tab1:
    f = st.file_uploader("Upload Report", type=['pdf', 'docx', 'txt'])
    if f:
        content = extract_text(f)
        if content:
            score, found, all_sec, vulns = analyze_logic(content)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Score", f"{score}%")
            c2.metric("Findings", len(vulns))
            c3.metric("Status", "Passed" if score >= 75 else "Needs Work")
            
            st.divider()
            st.subheader("Audit Results")
            for s in all_sec:
                if s in found:
                    st.markdown(f'<div class="success-box">✅ <b>{s}</b>: Identified in Document</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ <b>{s}</b>: Not Detected (Check Heading)</div>', unsafe_allow_html=True)

with tab2:
    m_files = st.file_uploader("Bulk Upload (Max 25)", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
    if m_files:
        res = []
        for file in m_files[:25]:
            txt = extract_text(file)
            s, _, _, _ = analyze_logic(txt)
            res.append({"File": file.name, "Score": f"{s}%"})
        st.table(pd.DataFrame(res).sort_values("Score", ascending=False))
