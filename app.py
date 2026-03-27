import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import matplotlib.pyplot as plt
import re
import io

# Page Config
st.set_page_config(page_title="Report-Check.ai Pro", layout="wide")

# Professional Dark UI
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .report-card { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# --- SMART Extraction Function ---
def extract_text(file):
    fname = file.name.lower()
    text = ""
    try:
        if fname.endswith('.pdf'):
            pdf = PdfReader(file)
            for page in pdf.pages:
                text += page.extract_text() or ""
        elif fname.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif fname.endswith('.txt'):
            text = file.read().decode("utf-8")
        # Image support (OCR error handling)
        elif fname.endswith(('.png', '.jpg', '.jpeg')):
            try:
                import pytesseract
                text = pytesseract.image_to_string(Image.open(file))
            except:
                return "ERROR_OCR: Tesseract not installed on server."
        return text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- ADVANCED Analysis Logic ---
def analyze_content(text):
    text_lower = text.lower()
    
    # Smart Matching: Multiple keywords for each section
    check_list = {
        "Executive Summary": ["executive summary", "summary of findings", "high-level overview", "introduction"],
        "Methodology": ["methodology", "scope", "engagement", "approach", "tools used"],
        "Technical Findings": ["findings", "vulnerabilities", "risk assessment", "technical analysis", "attack verification"],
        "Remediation": ["remediation", "recommendations", "mitigation", "strategic recommendations", "short-term fixes"]
    }
    
    found_sections = []
    for section, keywords in check_list.items():
        if any(k in text_lower for k in keywords):
            found_sections.append(section)
    
    score = len(found_sections) * 25
    
    # Vulnerability Scanner
    vulns_to_check = ["sql injection", "xss", "rce", "api leak", "pii leak", "broken access", "idor", "version exposure"]
    detected_vulns = [v.upper() for v in vulns_to_check if v in text_lower]
    
    return score, found_sections, list(check_list.keys()), detected_vulns

# --- APP INTERFACE ---
st.title("🛡️ Report-Check.ai (Pro Edition)")
tab1, tab2 = st.tabs(["🔍 Single Deep Analysis", "🏆 25-File Leaderboard"])

with tab1:
    up_file = st.file_uploader("Upload Report (PDF, Word, Image)", type=['pdf', 'docx', 'txt', 'png', 'jpg'], key="single")
    if up_file:
        raw_text = extract_text(up_file)
        if "ERROR_OCR" in raw_text:
            st.warning("OCR (Image reading) is not active. Please upload PDF or Word for better results.")
        elif raw_text:
            score, found, all_sec, vulns = analyze_content(raw_text)
            
            # Layout
            c1, c2 = st.columns([1, 1])
            with c1:
                st.metric("Report Score", f"{score}%")
                st.write("### Structure Audit")
                for s in all_sec:
                    if s in found: st.success(f"✅ {s}: Found")
                    else: st.error(f"❌ {s}: Missing or not clearly labeled")
            
            with c2:
                st.write("### Security Findings")
                if vulns: st.warning(f"Detected: {', '.join(vulns)}")
                else: st.info("No critical keywords found.")
                
                # Image Export Logic
                fig, ax = plt.subplots(figsize=(5,2))
                ax.barh(all_sec, [1 if s in found else 0 for s in all_sec], color='#38bdf8')
                plt.title("Section Presence")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                st.download_button("📥 Download Analysis as Image", buf.getvalue(), "analysis.png", "image/png")

with tab2:
    multi_files = st.file_uploader("Upload up to 25 files for Comparison", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'png', 'jpg'])
    if multi_files:
        results = []
        for f in multi_files[:25]:
            t = extract_text(f)
            s, _, _, _ = analyze_content(t)
            results.append({"Filename": f.name, "Score": s})
        
        df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
        st.table(df)
        
        # Leaderboard Image Export
        fig2, ax2 = plt.subplots()
        df.plot(kind='bar', x='Filename', y='Score', ax=ax2, color='#38bdf8')
        plt.tight_layout()
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png')
        st.download_button("📥 Download Leaderboard Image", buf2.getvalue(), "leaderboard.png", "image/png")
