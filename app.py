import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import base64

# --- CONFIGURATION & SESSION STATE ---
st.set_page_config(page_title="Student Academic Performance Optimizer", layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'org_name' not in st.session_state:
    st.session_state.org_name = ""
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        "Section A": {}, "Section B": {}, "Section C": {}, "Section D": {}, "Section E": {}
    }

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .report-header { text-align: center; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def generate_pdf(org_name, final_score, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Academic Performance Analysis Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Organization: {org_name}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Final Performance Score: {final_score}/200", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    for section, values in data.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"--- {section} ---", ln=True)
        pdf.set_font("Arial", size=10)
        for k, v in values.items():
            pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- PHASE 1: ACTIVATION & IDENTITY ---
if not st.session_state.authenticated:
    st.title("🔐 System Activation")
    with st.container():
        key = st.text_input("Enter Activation Key", type="password")
        org = st.text_input("Enter Organization Name")
        
        if st.button("Activate System"):
            # Set your preferred key here
            if key == "ADMIN2025" and org.strip() != "":
                st.session_state.authenticated = True
                st.session_state.org_name = org
                st.rerun()
            else:
                st.error("Invalid Key or Organization Name missing.")
    st.stop()

# --- PHASE 2: MAIN APP INTERFACE ---
st.title(f"📊 {st.session_state.org_name}")
st.subheader("Student Academic Performance Optimizer")

tabs = st.tabs([
    "Section A: Foundations", 
    "Section B: Effort", 
    "Section C: Method", 
    "Section D: Context",
    "Section E: Goals"
])

# --- SECTION A ---
with tabs[0]:
    st.header("Academic Foundations")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.data_store["Section A"]["Student ID"] = st.text_input("Student ID & Name", placeholder="e.g. #102 - John Doe")
        st.session_state.data_store["Section A"]["Monthly Score"] = st.slider("Monthly Test Avg", 0, 100, 75)
        st.session_state.data_store["Section A"]["Assignment Rate"] = st.number_input("Assignment Completion %", 0, 100, 85)
    with col2:
        st.session_state.data_store["Section A"]["GPA Trend"] = st.selectbox("GPA Trend", ["Improving", "Stable", "Declining"])
        uploaded_file = st.file_file_uploader("Upload Bulk Academic Data (CSV/Excel)", type=['csv', 'xlsx'], key="fileA")
        if uploaded_file:
            st.success("File Processed Successfully")

# --- SECTION B ---
with tabs[1]:
    st.header("Behavioral & Engagement")
    st.session_state.data_store["Section B"]["Attendance"] = st.slider("Attendance Percentage", 0, 100, 90)
    st.session_state.data_store["Section B"]["Participation"] = st.select_slider("Class Participation Score", options=list(range(1, 11)))
    st.session_state.data_store["Section B"]["Library Usage"] = st.number_input("Library Hours/Week", 0, 50, 5)

# --- SECTION C ---
with tabs[2]:
    st.header("Psychometric & Learning Style")
    st.session_state.data_store["Section C"]["Category"] = st.radio("Learning Category", ["Visual", "Auditory", "Kinesthetic"])
    st.session_state.data_store["Section C"]["Attention"] = st.number_input("Attention Span (Minutes)", 5, 120, 30)
    st.session_state.data_store["Section C"]["Strength"] = st.selectbox("Cognitive Strength", ["Logic", "Memory", "Creative"])

# --- SECTION D ---
with tabs[3]:
    st.header("Support Systems")
    st.session_state.data_store["Section D"]["Home Support"] = st.select_slider("Home Support Level", ["Low", "Medium", "High"])
    st.session_state.data_store["Section D"]["Extra Coaching"] = st.number_input("Weekly Tuition Hours", 0, 20, 2)

# --- SECTION E ---
with tabs[4]:
    st.header("Target Settings")
    st.session_state.data_store["Section E"]["Goal"] = st.number_input("Aspirational Goal (%)", 0, 100, 90)
    st.session_state.data_store["Section E"]["Study Hours"] = st.number_input("Daily Study Plan (Hours)", 0, 15, 3)

# --- PHASE 3: CALCULATION & OUTPUT ---
st.divider()
if st.button("Calculate Final Analytics"):
    try:
        # Simple weighted logic for demonstration (Scaling to 200)
        score_a = (st.session_state.data_store["Section A"]["Monthly Score"] * 0.8)
        score_b = (st.session_state.data_store["Section B"]["Attendance"] * 0.6)
        score_c = (st.session_state.data_store["Section C"]["Attention"] * 0.2)
        score_d = 20 if st.session_state.data_store["Section D"]["Home Support"] == "High" else 10
        
        final_score = min(200, round(score_a + score_b + score_c + score_d))
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Performance Index", f"{final_score} / 200")
            if final_score > 150: st.success("Status: High Potential")
            elif final_score > 100: st.warning("Status: Steady Progress")
            else: st.error("Status: Intervention Required")
            
        with col_res2:
            pdf_bytes = generate_pdf(st.session_state.org_name, final_score, st.session_state.data_store)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"Report_{st.session_state.org_name}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"An error occurred during calculation: {e}")

if st.button("Reset Application"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
