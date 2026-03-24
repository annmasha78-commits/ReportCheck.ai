import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Page & UI Styling
st.set_page_config(page_title="Report-Check.ai Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #ffa500; margin-bottom: 10px; }
    .success-card { background: rgba(0, 255, 128, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #00ff80; }
    .metric-box { background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; border-radius: 12px; padding: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Analysis Logic
def analyze_pentest_report(text):
    text = text.lower()
    criteria = {
        "Executive Summary": {
            "keywords": ["executive summary", "overview", "introduction"],
            "advice": "Add a high-level summary for management. Focus on business impact."
        },
        "Methodology": {
            "keywords": ["methodology", "testing approach", "reconnaissance", "scanning"],
            "advice": "List the tools (Nmap, Burp Suite) and steps taken during testing."
        },
        "Technical Findings": {
            "keywords": ["findings", "vulnerabilities", "results", "poc"],
            "advice": "Include screenshots and step-by-step Proof of Concept (PoC) for every bug."
        },
        "Remediation": {
            "keywords": ["remediation", "mitigation", "recommendations", "fix"],
            "advice": "Provide clear code-level or configuration-level fixes for developers."
        }
    }
    
    analysis = {}
    score = 0
    for section, data in criteria.items():
        found = any(k in text for k in data["keywords"])
        analysis[section] = {"found": found, "advice": data["advice"]}
        if found: score += 25
        
    vulns = [v.upper() for v in ["sql injection", "xss", "rce", "idor", "brute force"] if v in text]
    return score, analysis, vulns

# 3. PDF Result Generator
def create_pdf_result(score, analysis, vulns, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Report-Check.ai: Pentest Audit Record", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"File: {filename}", ln=True)
    pdf.cell(200, 10, f"Final Score: {score}%", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Structure & Suggestions:", ln=True)
    for sec, data in analysis.items():
        status = "Present" if data['found'] else "MISSING"
        pdf.cell(200, 8, f"- {sec}: {status}", ln=True)
        if not data['found']:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(200, 6, f"  Suggestion: {data['advice']}", ln=True)
            pdf.set_font("Arial", size=12)
    return pdf.output(dest='S').encode('latin-1')

# 4. Main UI
st.title("🛡️ Report-Check.ai (
