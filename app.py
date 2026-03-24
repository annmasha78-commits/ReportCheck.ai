import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
from fpdf import FPDF
import pandas as pd

# 1. Page Config & Professional Theme
st.set_page_config(page_title="Report-Check.ai", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b101a; color: white; }
    .suggestion-card { background: rgba(255, 165, 0, 0.1); padding: 20px; border-radius: 12px; border-left: 6px solid #ffa500; margin-bottom: 15px; }
    .success-card { background: rgba(0, 255, 128, 0.1); padding: 20px; border-radius: 12px; border-left: 6px solid #00ff80; margin-bottom: 15px; }
    .metric-container { background: rgba(56, 189, 248, 0.05); border: 1px solid #38bdf8; border-radius: 15px; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- Logic: Analysis Engine ---
def analyze_report(text):
    text = text.lower()
    # Sections to scan
    criteria = {
        "Executive Summary": ["executive summary", "overview", "introduction"],
        "Methodology": ["methodology", "testing approach", "reconnaissance"],
        "Technical Findings": ["findings", "vulnerabilities", "results"],
        "Remediation": ["remediation", "mitigation", "recommendations"]
    }
    
    analysis = {}
    score = 0
    for section, keywords in criteria.items():
        found = any(k in text for k in keywords)
        analysis[section] = found
        if found: score += 25
        
    # Security vulnerability scanning
    vulns_list = ["sql injection", "xss", "rce", "idor", "brute force", "lfi"]
    detected_vulns = [v.upper() for v in vulns_list if v in text]
    
    return score, analysis, detected_vulns

# --- Logic: PDF Generator ---
def create_pdf_report(score, analysis, filename, vulns):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 15, "Report-Check.ai: Professional Audit Result", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Analyzed Report: {filename}", ln=True)
    pdf.cell(200, 10, f"Overall Perfection Score: {score}%", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Structure Analysis:", ln=True)
    pdf.set_font("Arial", size=12)
    for sec, status in analysis.items():
        res = "✓ Detected" if status else "X Missing"
        pdf.cell(200, 10, f"- {sec}: {res}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, f"Critical Vulnerabilities Identified: {len(vulns)}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- UI Interface ---
st.title("🛡️ Report-Check.ai (Ultimate Edition)")
st.write("Analyze Pentest Reports: PDF, DOCX, & TXT supported.")

uploaded_file = st.file_uploader("Drop the Pentest Report Here", type=['pdf', 'docx', 'txt'])

if uploaded_file:
    with st.spinner('🔍 AI Engine scanning report structure...'):
        # Text Extraction
        text = ""
        try:
            if uploaded_file.name.endswith('.pdf'):
                reader = PdfReader(uploaded_file)
                for page in reader.pages: text += page.extract_text()
            elif uploaded_file.name.endswith('.docx'):
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
            else:
                text = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"File reading error: {e}")

        if text:
            score, analysis_results, found_vulns = analyze_report(text)
            
            # 1. Visual Metrics (Like the Picture)
            st.divider()
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                st.metric("Report Grade", f"{score}%")
                st.markdown("</div>", unsafe_allow_html=True)
            with m2:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                count = sum(analysis_results.values())
                st.metric("Sections Detected", f"{count}/4")
                st.markdown("</div>", unsafe_allow_html=True)
            with m3:
                st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
                st.metric("Critical Vulns Found", len(found_vulns))
                st.markdown("</div>", unsafe_allow_html=True)

            st.progress(score / 100)

            # 2. Advanced Tabs
            t1, t2, t3 = st.tabs(["📋 Analysis & Scoring", "💡 Improvements", "📥 Download Record"])

            with t1:
                st.subheader("Structure Audit")
                for section, status in analysis_results.items():
                    if status:
                        st.success(f"✅ **{section}**: Properly Documented")
                    else:
                        st.error(f"❌ **{s}**: This section is missing!")
                
                if found_vulns:
                    st.subheader("Identified Vulnerabilities")
                    st.info(", ".join(found_vulns))

            with t2:
                st.subheader("Expert Feedback & Suggestions")
                for section, status in analysis_results.items():
                    if not status:
                        st.markdown(f"""<div class='suggestion-card'>
                        <b>⚠️ Fix Needed: {section}</b><br>
                        Student ko kahein ke report mein '{section}' ka section shamil karein. Ismein screenshots aur step-by-step methodology honi chahiye taake teacher ko samajh aa sake.
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='success-card'>✅ <b>{section}</b> is perfect. No changes needed.</div>", unsafe_allow_html=True)

            with t3:
                st.write("### Generate Professional Result")
                st.write("Teacher can download this analysis as a PDF for grading records.")
                pdf_bytes = create_pdf_report(score, analysis_results, uploaded_file.name, found_vulns)
                st.download_button(
                    label="📥 Download Result PDF",
                    data=pdf_bytes,
                    file_name=f"Result_{uploaded_file.name}.pdf",
                    mime="application/pdf"
                )
