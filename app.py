import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import io

# 1. Page & Theme Config
st.set_page_config(page_title="Report-Check.ai", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 20px; border-radius: 12px; border-left: 6px solid #ffa500; margin-bottom: 15px; }
    .success-card { background: rgba(0, 255, 128, 0.1); padding: 20px; border-radius: 12px; border-left: 6px solid #00ff80; margin-bottom: 15px; }
    .metric-box { background: rgba(56, 189, 248, 0.1); border: 1px solid #38bdf8; border-radius: 15px; padding: 20px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Analysis & Logic ---
def get_analysis(text):
    text = text.lower()
    # Sections and their specific advice
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
            "advice": "Har vulnerability ke saath uska Proof of Concept (Screenshot) aur description shamil karein."
        },
        "Remediation": {
            "keywords": ["remediation", "mitigation", "recommendations", "solution"],
            "advice": "Sirf ghalti batana kafi nahi, developer ko theek karne ka tareeka (Solution) bhi batana zaruri hai."
        }
    }
    
    results = {}
    score = 0
    for section, data in criteria.items():
        found = any(k in text for k in data["keywords"])
        results[section] = {"found": found, "advice": data["advice"]}
        if found: score += 25
        
    vulns_list = ["sql injection", "xss", "rce", "idor", "brute force"]
    detected_vulns = [v.upper() for v in vulns_list if v in text]
    
    return score, results, detected_vulns

# --- PDF Generation (With Detailed Summary) ---
def generate_pdf_report(score, results, vulns, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 15, "Report-Check.ai | Pentest Audit Summary", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, f"File Name: {filename}", ln=True)
    pdf.cell(100, 10, f"Total Score: {score}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Structure Audit & Suggestions:", ln=True)
    pdf.set_font("Arial", size=11)
    for sec, data in results.items():
        status = "PASSED" if data['found'] else "FAILED"
        pdf.set_text_color(0, 128, 0) if data['found'] else pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 8, f"- {sec}: {status}", ln=True)
        pdf.set_text_color(0, 0, 0)
        if not data['found']:
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 7, f"   Suggestion: {data['advice']}")
            pdf.set_font("Arial", size=11)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Security Findings:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, f"Vulnerabilities Detected: {', '.join(vulns) if vulns else 'None'}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- UI Interface ---
st.title("🛡️ Report-Check.ai Pro")
st.write("Scan Reports & Generate Professional Results for Teachers")

file = st.file_uploader("Upload Student Report", type=['pdf', 'docx', 'txt'])

if file:
    # Extraction
    text = ""
    if file.name.endswith('.pdf'):
        reader = PdfReader(file); text = "".join([p.extract_text() for p in reader.pages])
    elif file.name.endswith('.docx'):
        doc = Document(file); text = "\n".join([p.text for p in doc.paragraphs])
    else:
        text = file.read().decode("utf-8", errors="ignore")

    score, analysis, vulns = get_analysis(text)
    
    # 1. Metrics Dashboard
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Overall Score", f"{score}%")
    with c2: st.metric("Vulnerabilities", len(vulns))
    with c3:
        status = "✅ Ready" if score > 75 else "❌ Needs Work"
        st.subheader(status)
    
    st.progress(score / 100)

    # 2. Results & Detailed Suggestions Tabs
    tab1, tab2 = st.tabs(["📋 Detailed Analysis", "📥 Download PDF Result"])

    with tab1:
        st.subheader("Structure Audit & Smart Suggestions")
        for sec, data in analysis.items():
            if data['found']:
                st.markdown(f"<div class='success-card'>✅ <b>{sec}</b> is present. Structure is good.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='suggestion-card'>
                <b>❌ Missing: {sec}</b><br>
                <b>How to fix:</b> {data['advice']}
                </div>""", unsafe_allow_html=True)
        
        st.subheader("Summary Report")
        st.write(f"Is report mein total **{len(vulns)}** bugs mile hain. Overall quality **{score}%** hai.")

    with tab2:
        st.write("### Generate & Save Final Report")
        st.info("Teacher is button par click kar ke poora result PDF form mein save kar sakti hain.")
        pdf_file = generate_pdf_report(score, analysis, vulns, file.name)
        st.download_button(
            label="📄 Download Result as PDF",
            data=pdf_file,
            file_name=f"Result_{file.name}.pdf",
            mime="application/pdf"
        )
