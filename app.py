import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import base64

# Page Config
st.set_page_config(page_title="Report-Check.ai", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #ffa500; margin-bottom: 10px; }
    .success-card { background: rgba(0, 255, 0, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- Analysis Helper ---
def analyze_report(text):
    text = text.lower()
    criteria = {
        "Executive Summary": ["executive summary", "overview"],
        "Methodology": ["methodology", "testing approach"],
        "Technical Findings": ["findings", "vulnerabilities"],
        "Remediation": ["remediation", "mitigation"]
    }
    
    analysis = {}
    score = 0
    for section, keywords in criteria.items():
        found = any(k in text for k in keywords)
        analysis[section] = found
        if found: score += 25
        
    return score, analysis

# --- PDF Result Generator ---
def create_pdf_report(score, analysis, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Report-Check.ai: Pentest Analysis Result", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Analyzed File: {filename}", ln=True)
    pdf.cell(200, 10, f"Final Score: {score}/100", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Structure Audit:", ln=True)
    for sec, status in analysis.items():
        res = "Present" if status else "Missing"
        pdf.cell(200, 10, f"- {sec}: {res}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- UI ---
st.title("🛡️ Report-Check.ai (Pro)")
uploaded_file = st.file_uploader("Upload Report", type=['pdf', 'docx', 'txt'])

if uploaded_file:
    # (Text extraction logic same as before)
    text = ""
    if uploaded_file.name.endswith('.pdf'):
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages: text += page.extract_text()
    else: text = uploaded_file.read().decode("utf-8", errors="ignore")

    score, analysis = analyze_report(text)
    
    # Dashboard
    st.metric("Final Perfection Score", f"{score}%")
    st.progress(score / 100)

    t1, t2 = st.tabs(["📊 Analysis Result", "📥 Download Record"])

    with t1:
        st.subheader("What to Improve?")
        for section, status in analysis.items():
            if not status:
                st.markdown(f"""<div class='suggestion-card'>
                <b>⚠️ Missing: {section}</b><br>
                <i>Suggestion:</i> Student ko kahein ke is section mein technical details aur images add karein taake report professional lage.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='success-card'>✅ {section} is well-documented.</div>", unsafe_allow_html=True)

    with t2:
        st.write("Teacher can download this result as a PDF record.")
        pdf_data = create_pdf_report(score, analysis, uploaded_file.name)
        st.download_button(label="Download Full Result PDF", data=pdf_data, file_name="Analysis_Result.pdf", mime="application/pdf")
