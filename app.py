import streamlit as st

# 1. Page Configuration & Professional Branding
st.set_page_config(page_title="Report-Check.ai", page_icon="🛡️", layout="centered")

# 2. Advanced UI/UX (Glassmorphism + Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); 
        color: #0f172a; border-radius: 10px; height: 3.5em; width: 100%; 
        border: none; font-weight: 800; letter-spacing: 1px; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4); }
    .status-box { padding: 20px; border-radius: 15px; background: rgba(255, 255, 255, 0.03); border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# 3. Application Header
st.title("🛡️ Report-Check.ai")
st.write("### AI-Powered Pentest Report Analysis Engine")
st.info("Teacher's Dashboard: Upload a report in .txt format to get an instant security audit and grade.")

# 4. Core Logic (Features Intact)
def analyze_report(text):
    text = text.lower()
    # Sections to check
    criteria = {
        "Executive Summary": "executive summary",
        "Methodology": "methodology",
        "Technical Findings": "findings",
        "Remediation/Mitigation": "remediation"
    }
    
    found = []
    for display_name, keyword in criteria.items():
        if keyword in text:
            found.append(display_name)
            
    # Vulnerability Keywords Detection
    vulns = ["sql injection", "xss", "rce", "idor", "broken auth"]
    detected_vulns = [v.upper() for v in vulns if v in text]
    
    score = len(found) * 25
    return score, found, list(criteria.keys()), detected_vulns

# 5. File Upload Section
uploaded_file = st.file_uploader("Drop the Pentest Report Here", type=['txt'])

if uploaded_file:
    with st.spinner('Analyzing Report Security Posture...'):
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        score, found_sections, all_sections, vulns_found = analyze_report(content)
        
        st.divider()
        
        # Results Section
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Overall Grade", value=f"{score}%")
            st.progress(score / 100)
        
        with col2:
            if score >= 75:
                st.success("STATUS: SUBMISSION READY")
            else:
                st.error("STATUS: REVISION REQUIRED")

        # Detailed Feedback
        st.write("---")
        t1, t2 = st.tabs(["📝 Structure Audit", "🔥 Security Findings"])
        
        with t1:
            st.write("### Report Layout Check")
            for section in all_sections:
                if section in found_sections:
                    st.write(f"✅ **{section}**: Present")
                else:
                    st.write(f"❌ **{section}**: Missing or Not Defined")
        
        with t2:
            st.write("### Identified Vulnerabilities in Report")
            if vulns_found:
                for v in vulns_found:
                    st.markdown(f"🚩 `{v}`")
            else:
                st.write("No major vulnerability keywords detected.")

        # Final Advice for Teacher
        if score < 100:
            st.warning(f"💡 **Teacher's Note:** This report is missing {100-score}% of the essential framework. Suggest the student to add the missing sections.")
        else:
            st.balloons()
            st.success("💡 **Teacher's Note:** This is an industry-standard report. Excellent documentation.")
