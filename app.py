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
        "Executive Summary": {
            "keywords": ["executive summary", "overview", "introduction"],
            "advice": "Summary add karein jo project ka maqsad aur high-level results bataye."
        },
        "Methodology": {
            "keywords": ["methodology", "testing approach", "reconnaissance", "scanning"],
            "advice": "Testing ke steps aur tools (Nmap, Burp Suite) ka zikr hona lazmi hai."
        },
        "Technical Findings": {
            "keywords": ["findings", "vulnerabilities", "results", "proof of concept"],
            "advice": "Har vulnerability ke saath screenshots aur technical details shamil karein."
        },
        "Remediation": {
            "keywords": ["remediation", "mitigation", "recommendations", "solution"],
            "advice": "Bugs ko theek karne ke liye proper 'Solution' ya 'Remediation' steps likhen."
        }
    }
    
    results = {}
    score = 0
    for section, data in criteria.items():
        found = any(k in text for k in data["keywords"])
        results[section] = {"found": found, "advice": data["advice"]}
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
    pdf.cell(200, 10, f"Student File: {filename}", ln=True)
    pdf.cell(200, 10, f"Overall Grade: {score}%", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Structure Audit & Feedback:", ln=True)
    pdf.set_font("Arial", size=11)
    for sec, data in results.items():
        status = "PASSED" if data['found'] else "MISSING"
        pdf.cell(200, 8, f"- {sec}: {status}", ln=True)
        if not data['found']:
            pdf.cell(200, 6, f"  Suggestion: {data['advice']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# 5. UI Layout
st.title("🛡️ Report-Check.ai (Batch Pro)")
st.write("Ek waqt mein 10 reports tak upload karein. Har report ka alag score aur suggestion milay ga.")

uploaded_files = st.file_uploader("Upload Student Reports", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

if uploaded_files:
    # Check if files are more than 10
    files_to_process = uploaded_files[:10]
    if len(uploaded_files) > 10:
        st.warning("⚠️ Sirf pehli 10 reports process ki ja rahi hain.")

    for uploaded_file in files_to_process:
        with st.container():
            st.markdown(f"<div class='report-box'>", unsafe_allow_html=True)
            st.subheader(f"📄 Report: {uploaded_file.name}")
            
            # Text Extraction
            content = ""
            try:
                if uploaded_file.name.endswith('.pdf'):
                    reader = PdfReader(uploaded_file)
                    content = "".join([page.extract_text() for page in reader.pages])
                elif uploaded_file.name.endswith('.docx'):
                    doc = Document(uploaded_file)
                    content = "\n".join([p.text for p in doc.paragraphs])
                else:
                    content = uploaded_file.read().decode("utf-8", errors="ignore")
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")

            if content:
                score, analysis, vulns = get_analysis_results(content)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.metric("Final Score",
