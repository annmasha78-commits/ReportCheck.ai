import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Page Configuration
st.set_page_config(page_title="Report-Check.ai", layout="wide", page_icon="🛡️")

# 2. Styling (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.15); padding: 15px; border-radius: 10px; border-left: 6px solid #ffa500; margin-bottom: 10px; }
    .success-card { background: rgba(0, 255, 128, 0.15); padding: 15px; border-radius: 10px; border-left: 6px solid #00ff80; margin-bottom: 10px; }
    .metric-container { background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; border-radius: 15px; padding: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. Analysis Logic
def get_analysis_results(text):
    text = text.lower()
    criteria = {
        "Executive Summary": {
            "keywords": ["executive summary", "overview", "introduction"],
            "advice": "Student ko kahein ke report ke shuru mein 'Executive Summary' likhen jo project ka maqsad samjhaye."
        },
        "Methodology": {
            "keywords": ["methodology", "testing approach", "reconnaissance", "scanning"],
            "advice": "Ismein testing ke steps (jaise Nmap scan, tools use) ka zikr hona lazmi hai."
        },
        "Technical Findings": {
            "keywords": ["findings", "vulnerabilities", "results", "proof of concept"],
            "advice": "Har vulnerability ke saath uska Proof of Concept (Screenshot) shamil karein."
        },
        "Remediation": {
            "keywords": ["remediation", "mitigation", "recommendations", "solution"],
            "advice": "Sirf ghalti na bataein, developer ko theek karne ka tareeka (Solution) bhi bataein."
        }
    }
    
    results = {}
    score = 0
    for section, data in criteria.items():
        found = any(k in text for k in data["keywords"])
        results[section] = {"found": found, "advice": data["advice"]}
        if found: score += 25
        
    vulns_list = ["sql injection", "xss", "rce", "idor", "brute force", "lfi"]
    detected_vulns = [v.upper() for v in vulns_list if v in text]
    
    return score, results, detected_vulns

# 4. PDF Generation Function
def generate_pdf(score, results, vulns, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 15, "Report-Check.ai Audit Result", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"File Name: {filename}", ln=True)
    pdf.cell(200, 10, f"Overall Score: {score}%", ln=True)
    pdf.ln(5)
