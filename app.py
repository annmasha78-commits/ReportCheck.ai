import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
import io

# Page Configuration
st.set_page_config(page_title="Report-Check.ai", page_icon="🛡️", layout="wide")

# Futuristic UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border-radius: 5px; padding: 10px 20px; color: white; }
    .stMetric { background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Report-Check.ai (Stable Edition)")
st.write("Analyze Pentest Reports: PDF, DOCX, & TXT supported.")

# --- Extraction Functions (Simplified - No OCR Error) ---
def extract_text(file):
    fname = file.name.lower()
    text = ""
    try:
        if fname.endswith('.txt'):
            text = file.read().decode("utf-8")
        elif fname.endswith('.pdf'):
            pdf = PdfReader(file)
            for page in pdf.pages:
                text += page.extract_text() or ""
        elif fname.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error: {str(e)}"

# --- Analysis Engine ---
def analyze_content(text):
    text = text.lower()
    criteria = {
        "Executive Summary": ["executive summary", "overview", "introduction"],
        "Methodology": ["methodology", "testing approach", "reconnaissance"],
        "Technical Findings": ["findings", "vulnerabilities", "results"],
        "Remediation": ["remediation", "mitigation", "recommendations"]
    }
    
    found = [name for name, keywords in criteria.items() if any(k in text for k in keywords)]
    score = len(found) * 25
    
    vulnerabilities = ["sql injection", "xss", "rce", "idor", "brute force", "broken access control"]
    detected_vulns = [v.upper() for v in vulnerabilities if v in text]
    
    return score, found, list(criteria.keys()), detected_vulns

# --- Main App Interface ---
uploaded_file = st.file_uploader("Drop report file (PDF, Word, TXT)", type=['txt', 'pdf', 'docx'])

if uploaded_file:
    with st.spinner('🚀 Deep Scanning Report...'):
        text_content = extract_text(uploaded_file)
        
        if not text_content or text_content.strip() == "" or "Error:" in text_content:
            st.error("Text extract nahi ho saka. File check karein.")
        else:
            score, found_sections, all_sections, vulns = analyze_content(text_content)
            
            st.divider()
            
            # Dashboard Overview
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Report Grade", f"{score}%")
            with c2: st.metric("Sections Detected", f"{len(found_sections)}/4")
            with c3: st.metric("Critical Vulns Found", len(vulns))
            
            st.progress(score / 100)

            # Detailed Analysis Tabs
            t1, t2, t3 = st.tabs(["📋 Analysis & Scoring", "💡 Improvements", "📝 Extracted Text Preview"])
            
            with t1:
                st.subheader("Structure Audit")
                for s in all_sections:
                    if s in found_sections:
                        st.success(f"✅ **{s}**: Included")
                    else:
                        st.error(f"❌ **{s}**: Missing")
                
                st.subheader("Detected Security Findings")
                if vulns:
                    st.write(", ".join(vulns))
                else:
                    st.info("No common vulnerability keywords found.")

            with t2:
                st.subheader("How to improve this report?")
                if score < 100:
                    st.warning("Professional report ke liye missing sections add karein.")
                else:
                    st.balloons()
                    st.success("Perfect! Report tayyar hai.")

            with t3:
                st.text_area("Content Preview", text_content[:2000] + "...", height=300)
