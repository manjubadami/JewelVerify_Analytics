import ast
from datetime import date

import google.generativeai as genai
import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta
from PIL import Image

# ==========================================
# 1. CONFIGURATION & MODELS
# ==========================================

# Access secrets via Streamlit's secure storage
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key not found. Please set GEMINI_API_KEY in Streamlit Secrets.")

# Initialize the Gemini model (using the 1.5-flash for speed/cost on mobile)
model = genai.GenerativeModel('gemini-3-flash-preview')

# Page Configuration for Mobile
st.set_page_config(
    layout="centered", 
    page_title="Glint AI: Smart Pricing",
    page_icon="💍"
)

# Custom CSS for enhanced mobile UI
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        height: 3.5em;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #007BFF;
    }
    </style>
    """, unsafe_allow_html=True)


# ==========================================
# 2. CORE UTILITY FUNCTIONS
# ==========================================

def extract_values_with_llm(uploaded_file):
    """
    Uses Computer Vision to extract specific weight and value addition 
    fields from a physical jewelry tag image.
    """
    img = Image.open(uploaded_file)
    prompt = """
    Analyze this jewelry tag and extract these three specific fields:
    - Nw (Net Weight as float)
    - VA (Value Addition as integer)
    - StAmt (Stone Amount as float)
    
    Return ONLY a valid Python dictionary, e.g.:
    {"Nw": 5.25, "VA": 18, "StAmt": 1200.0}
    """
    
    try:
        response = model.generate_content([prompt, img])
        # Using literal_eval is safer than eval() for string-to-dict conversion
        return ast.literal_eval(response.text.strip())
    except Exception as e:
        st.error(f"Extraction Error: {e}")
        return {"Nw": 0.0, "VA": 0, "StAmt": 0.0}


def get_breakdown(nw: float, gold_rate: float, va: float, st_amt: float):
    """
    Calculates the detailed financial breakdown including Making charges and GST.
    """
    gold_amt = nw * gold_rate
    making_amt = gold_amt * (va / 100)
    # GST calculation (Standard 3% for Jewelry in India)
    gst = (gold_amt + making_amt + st_amt) * 0.03
    total = gold_amt + making_amt + st_amt + gst
    
    df = pd.DataFrame({
        "Description": ["Gold Value", "Making (VA)", "Stone Amt", "GST (3%)", "Total"],
        "Amount": [gold_amt, making_amt, st_amt, gst, total]
    })
    return df, total


def calculate_plan_va(base_va: int, plan_date: date) -> int:
    """
    Calculates the adjusted Value Addition based on the maturity of 
    the gold savings plan.
    """
    diff = relativedelta(date.today(), plan_date)
    months = diff.years * 12 + diff.months
    
    if months < 6:
        return base_va
    elif 6 <= months < 9:
        return max(0, base_va - 16)
    elif 9 <= months < 12:
        return max(0, base_va - 18)
    else:
        return 0


# ==========================================
# 3. STREAMLIT UI & APP LOGIC
# ==========================================

def main():
    st.title("💍 Glint AI Pricing")
    st.caption("Professional Gold Tag Digitization & Benefit Analysis")

    # Mobile-optimized mode selector
    view_mode = st.segmented_control(
        "Analysis Mode", 
        ["Current", "Compare"], 
        default="Current"
    )

    uploaded_file = st.file_uploader("📸 Scan Jewelry Tag", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        # Cache results in Session State to prevent unnecessary API calls
        if "data" not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
            with st.spinner("AI Scanning Tag..."):
                st.session_state.data = extract_values_with_llm(uploaded_file)
                st.session_state.last_file = uploaded_file.name
                st.session_state.calculated = False

        data = st.session_state.data
        
        # Summary Header
        st.info(f"**Weight:** {data['Nw']}g | **Tag VA:** {data['VA']}% | **Stone:** {data['StAmt']}")

        # Input Form - Bundles inputs for "Apply" button logic
        with st.form("price_inputs"):
            col1, col2 = st.columns(2)
            
            with col1:
                current_rate = st.number_input("Today's Rate", min_value=0.0, step=100.0)
            
            if view_mode == "Compare":
                with col2:
                    plan_rate = st.number_input("Plan Rate", min_value=0.0, step=100.0)
                plan_date = st.date_input("Plan Start Date", value=date.today() - relativedelta(months=7))
            else:
                plan_rate, plan_date = 0.0, None

            submitted = st.form_submit_button("Apply Calculation")

        if submitted:
            st.session_state.calculated = True

        # Result Display Logic
        if st.session_state.get("calculated"):
            if view_mode == "Current" and current_rate > 0:
                df_cur, _ = get_breakdown(data['Nw'], current_rate, data['VA'], data['StAmt'])
                st.subheader("Current Pricing Breakdown")
                st.table(df_cur.style.format({"Amount": "{:,.2f}"}))
                
            elif view_mode == "Compare" and current_rate > 0 and plan_rate > 0:
                # Logic for plan benefit
                p_va = calculate_plan_va(data['VA'], plan_date)
                
                df_c, c_tot = get_breakdown(data['Nw'], current_rate, data['VA'], data['StAmt'])
                df_p, p_tot = get_breakdown(data['Nw'], plan_rate, p_va, data['StAmt'])

                # Tabbed view saves vertical space on mobile
                tab_now, tab_plan = st.tabs(["📉 Current Price", "🎁 Plan Benefit"])
                
                with tab_now:
                    st.dataframe(df_c, use_container_width=True, hide_index=True)
                
                with tab_plan:
                    st.write(f"**Adjusted VA for Plan:** {p_va}%")
                    st.dataframe(df_p, use_container_width=True, hide_index=True)

                st.divider()
                st.metric(label="Estimated Total Savings", value=f"₹ {round(c_tot - p_tot, 2)}")

if __name__ == "__main__":
    main()