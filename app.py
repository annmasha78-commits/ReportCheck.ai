import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Page Configuration
st.set_page_config(page_title="Report-Check.ai", layout="wide", page_icon="🛡️")

# 2. Professional Styling
st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .report-box { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #38bdf8; 
        margin-bottom: 25px; 
    }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 10px; border-radius: 8px; border-left: 4px solid #ffa500; margin-bottom: 5px; }
    .success-card { background: rgba(0, 255, 128, 0.1); padding: 10px; border-radius: 8px; border-left: 4px solid #00ff80; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Analysis Logic
def get_analysis_results(text):
    text = text.lower()
    criteria = {
        "Executive Summary": ["executive summary", "overview", "introduction"],
        "Methodology": ["methodology", "testing approach", "reconnaissance"],
        "Technical Findings": ["findings", "vulnerabilities", "results"],
        "Remediation": ["remediation", "mitigation", "recommendations"]
    }
    
    results = {}
    score = 0
    for section, keywords in criteria.items():
        found = any(k in text for k in keywords)
        results[section] = found
        if found: score += 25
        
    vulns = [v.upper() for v in ["sql injection", "xss", "rce", "idor", "brute force"] if v in text]
    return score, results, vulns

# 4. PDF Generator
def create_pdf(score, results, vulns, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 15, "Report-Check.ai Audit Result", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"File Name: {filename}", ln=True)
    pdf.cell(200, 10, f"Score: {score}%", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Structure Audit:", ln=True)
    for sec, status in results.items():
        res = "Present" if status else "Missing"
        pdf.cell(200, 8, f"- {sec}: {res}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# 5. UI Layout
st.title("🛡️ Report-Check.ai (Batch Pro)")
st.write("Ek waqt mein 10 reports tak upload karein aur result check karein.")

# Multi-file uploader added
uploaded_files = st.file_uploader("Upload Student Reports", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

if uploaded_files:
    if len
