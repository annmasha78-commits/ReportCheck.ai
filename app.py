import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import matplotlib.pyplot as plt
import re
import io

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #ffffff; }
    .success-box { padding: 15px; background-color: #064e3b; border-radius: 10px; margin: 10px 0; border-left: 5px solid #10b981; }
    .error-box { padding: 15px; background-color: #7f1d1d; border-radius: 10px; margin: 10px 0; border-left: 5px solid #ef4444; }
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
    checks = {
        "Executive Summary": ["executive", "summary", "overview", "introduction"],
        "Methodology": ["methodology", "scope", "approach", "tools", "testing"],
        "Technical Findings": ["findings", "vulnerabilities", "technical", "results"],
        "Remediation": ["remediation", "recommendations", "mitigation", "fixes"]
    }
    
    found = []
    for section, keywords in checks.items():
        if any(k in t for k in keywords):
            found.append(section)
            
    score = len(found) * 25
    vuln_list = ["sql", "xss", "rce", "idor", "leak", "bypass", "broken", "exposure"]
    detected = [v.upper() for v in vuln_list if v in t]
    
    return score, found, list(checks.keys()), list(set(detected))

st.title("🛡️ Report-Check.ai (Stable Engine)")
tab1, tab2 = st.tabs(["🔍 Analyzer", "🏆 Leaderboard"])

with tab1:
    f = st.file_uploader("Upload Report", type=['pdf', 'docx', 'txt'])
    if f:
        with st.spinner("Analyzing Report..."):
            content = extract_text(f)
            
            # DEBUG: Agar text khali hai toh batao
            if not content:
                st.error("Document se koi text nahi mila. Kya ye scanned image hai?")
            elif content.startswith("Error:"):
                st.error(content)
            else:
                score, found, all_sec, vulns = analyze_logic(content)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Score", f"{score}%")
                c2.metric("Findings", len(vulns))
                c3.metric("Status", "Passed" if score >= 75 else "Needs Work")
                
                st.divider()
                st.subheader("Audit Results")
                for s in all_sec:
                    if s in found:
                        st.markdown(f'<div class="success-box">✅ <b>{s}</b>: Identified</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ <b>{s}</b>: Not Detected</div>', unsafe_allow_html=True)
                
                if vulns:
                    st.warning(f"Detected Vulnerability Keywords: {', '.join(vulns)}")

with tab2:
    st.info("Leaderboard is active. Upload multiple files to compare scores.")
    # (Rest of your leaderboard code)
