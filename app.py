import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import io

# -- Basic Page Setup --
st.set_page_config(page_title="Report-Check.ai", layout="wide")

# -- Styling --
st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #ffa500; margin-bottom: 10px; }
    .success-card { background: rgba(0, 255, 128, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #00ff80; }
    </style>
    """, unsafe_allow_html=True)

# -- Analysis Logic --
def run_analysis(text):
    text = text.lower()
    sections = {
        "Executive Summary": ["executive", "overview", "introduction"],
        "Methodology": ["methodology", "testing", "recon"],
        "Findings": ["findings", "vulnerabilities", "results"],
        "Remediation": ["remediation", "mitigation", "fix"]
    }
    advices = {
        "Executive Summary": "Summary add karein jo project ka maqsad bataye.",
        "Methodology": "Tools (Nmap, Burp) aur steps ka zikr karein.",
        "Findings": "Screenshots aur Proof of Concept (PoC) lazmi shamil karein.",
        "Remediation": "Har ghalti ka solution (Fix) bhi likhen."
    }
    
    results = {}
    score = 0
    for sec, keys in sections.items():
        found = any(k in text for k in keys)
        results[sec] = {"found": found, "advice": advices[sec]}
        if found: score += 25
        
    vulns = [v.upper() for v in ["sql injection", "xss", "rce", "idor"] if v in text]
    return score, results, vulns

# -- PDF Generator --
def make_pdf(score, results, vulns):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Report-Check.ai Audit Result", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Final Score: {score}%", ln=True)
    for s, d in results.items():
        status = "Present" if d['found'] else "Missing"
        pdf.cell(200, 10, f"- {s}: {status}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# -- Main App UI --
st.title("🛡️ Report-Check.ai (Pro)")
st.write("Upload a Pentest Report to see the score and download result.")

file = st.file_uploader("Upload File", type=['pdf', 'docx', 'txt'])

if file:
    text = ""
    if file.name.endswith('.pdf'):
