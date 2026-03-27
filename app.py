import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import matplotlib.pyplot as plt
import re
import io

# Page Configuration
st.set_page_config(page_title="Report-Check.ai Pro", page_icon="🛡️", layout="wide")

# Futuristic Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .report-card { background: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
    .stMetric { background: rgba(56, 189, 248, 0.05); padding: 15px; border-radius: 10px; border: 1px solid #1d4ed8; }
    </style>
    """, unsafe_allow_html=True)

# --- Enhanced Extraction Function ---
def extract_text(file):
    fname = file.name.lower()
    text = ""
    try:
        if fname.endswith('.pdf'):
            pdf = PdfReader(file)
            for page in pdf.pages:
                content = page.extract_text()
                if content: text += content
        elif fname.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif fname.endswith('.txt'):
            text = file.read().decode("utf-8")
        return text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- SMART Analysis Engine ---
def analyze_content(text):
    text_lower = text.lower()
    
    # Smart Mapping (Jo aapki report ke titles ko handle karega)
    criteria = {
        "Executive Summary": ["executive summary", "overview", "introduction", "summary"],
        "Methodology": ["methodology", "scope", "engagement", "testing approach", "tools"],
        "Technical Findings": ["findings", "vulnerabilities", "technical analysis", "risk assessment"],
        "Remediation": ["remediation", "recommendations", "mitigation", "strategic recommendations", "fixes"]
    }
    
    found_sections = [name for name, keys in criteria.items() if any(k in text_lower for k in keys)]
    score = len(found_sections) * 25
    
    # Vulnerability Keywords
    vuln_tags = ["sql injection", "xss", "rce", "idor", "pii leak", "api bypass", "brute force", "exposure"]
    detected_vulns = [v.upper() for v in vuln_tags if v in text_lower]
    
    return score, found_sections, list(criteria.keys()), detected_vulns

# --- Main Interface ---
st.title("🛡️ Report-Check.ai (Pro Suite)")
st.write("Professional Pentesting Report Analyzer & Leaderboard")

tab1, tab2 = st.tabs(["🔍 Single Report Deep-Dive", "🏆 Multi-Report Leaderboard (25 Files)"])

with tab1:
    st.subheader("Individual Report Analysis")
    up_file = st.file_uploader("Upload Report (PDF/DOCX/TXT)", type=['pdf', 'docx', 'txt'], key="single_up")
    
    if up_file:
        with st.spinner('Analyzing...'):
            raw_text = extract_text(up_file)
            if raw_text:
                score, found, all_sec, vulns = analyze_content(raw_text)
                
                # Dashboard
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Overall Score", f"{score}%")
                with c2: st.metric("Critical Findings", len(vulns))
                with c3: st.metric("Structure Health", f"{len(found)}/4")
                
                st.divider()
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.write("### 📋 Section Audit")
                    for s in all_sec:
                        if s in found: st.success(f"✅ **{s}**: Found in report")
                        else: st.error(f"❌ **{s}**: Missing or not labeled correctly")
                
                with col_right:
                    st.write("### 🚀 Improvement Guide")
                    if score == 100:
                        st.balloons()
                        st.success("Report is perfect and ready for submission!")
                    else:
                        st.warning("Professional report ke liye missing sections add karein.")
                
                # Image Download Section
                st.write("### 📥 Export Result")
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.barh(all_sec, [1 if s in found else 0.1 for s in all_sec], color=['#22c55e' if s in found else '#ef4444' for s in all_sec])
                plt.title("Report Quality Blueprint")
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                st.download_button("Download Analysis Image (PNG)", buf.getvalue(), "report_analysis.png", "image/png")

with tab2:
    st.subheader("25-File Comparison Leaderboard")
    multi_files = st.file_uploader("Upload up to 25 Reports", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
    
    if multi_files:
        data = []
