import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import pandas as pd

# 1. Page Configuration & Futuristic Theme
st.set_page_config(page_title="Report-Check.ai", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.15); padding: 20px; border-radius: 12px; border-left: 6px solid #ffa500; margin-bottom: 15px; }
    .success-card { background: rgba(0, 255, 128, 0.15); padding: 20px; border-radius: 12px; border-left: 6px solid #00ff80; margin-bottom: 15px; }
    .metric-container { background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; border-radius: 15px; padding: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Core Logic: Analysis Engine ---
def analyze_report(text):
    text = text.lower()
    # Combining all criteria and smart suggestions
    criteria = {
        "Executive Summary": {
            "keywords": ["executive summary", "overview", "introduction"],
            "advice": "Student ko kahein ke report ke shuru mein 'Executive Summary' likhen jo non-technical logon ko project ka maqsad samjhaye."
        },
        "Methodology": {
            "keywords": ["methodology", "testing approach", "reconnaissance", "scanning"],
            "advice": "Ismein testing ke steps (jaise Nmap scan, manual testing) aur tools ka zikr hona lazmi hai."
        },
        "Technical Findings": {
            "keywords": ["findings", "vulnerabilities", "results", "proof of concept"],
            "advice": "Har vulnerability ke saath uska Proof of Concept (Screenshot) aur detailed technical description shamil karein."
        },
        "Remediation": {
            "keywords": ["remediation", "mitigation", "recommendations", "solution"],
            "advice": "Sirf ghalti batana kafi nahi, developer ko theek karne ka tareeka (Step-by-step Solution) bhi batana zaruri hai."
        }
    }
    
    analysis_results = {}
    score = 0
    for section, data in criteria.items():
        found = any(k in text for k in data["keywords"])
        analysis_results[section] = {"found": found, "advice": data["advice"]}
        if found: score += 25
        
    # Vulnerability Detection
    vulns_list = ["sql injection", "xss", "rce", "idor", "brute force", "lfi", "broken access control"]
    detected_vulns = [v.upper() for v in vulns_list if v in text]
    
    return score, analysis_results, detected_vulns

# --- Core Logic: PDF Report Generator ---
def create_professional_pdf(score, results, vulns, filename):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(200, 20, "Report-Check.ai Audit Result", ln=True, align='C')
    
    # Summary Info
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 10, f"Analyzed Report: {filename}", ln=True)
    pdf.cell(100, 10, f"Overall Quality Score: {score}%", ln=True)
    pdf.cell(100, 10, f"Security Bugs Found: {len(vulns)}", ln=True)
    
    # Structure Audit
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Structure Audit & Teacher's Suggestions:", ln=True)
    pdf.set_font("Arial", size=11)
    
    for sec, data in results.items():
        status = "PASSED" if data['found'] else "FAILED (Missing)"
        pdf.set_text_color(0, 128, 0) if data['found'] else pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 8, f"- {sec}: {status}", ln=True)
        
        if not data['found']:
            pdf.set_text_color(100, 100, 100)
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 7, f"   Recommendation: {data['advice']}")
            pdf.set_font("Arial", size=11)
    
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Identified Vulnerabilities:", ln=True)
    pdf.set_font("Arial", size=11)
    vuln_text = ", ".join(vulns) if vulns else "No common vulnerability keywords detected."
    pdf.multi_cell(0, 10, vuln_text)
    
    return
