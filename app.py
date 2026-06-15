import streamlit as st
import pandas as pd
import sys
import time
import json
import firebase_admin
from firebase_admin import credentials, db

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="Airflow Cloud RFID Center", page_icon="⚡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size:28px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .brand-sub { font-size:13px !important; color: #2563EB; font-weight: 600; text-align: center; margin-bottom: 25px; letter-spacing: 1px; }
    .metric-box { padding: 20px; background-color: #F8FAFC; border-radius: 10px; border-left: 5px solid #2563EB; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- FIREBASE INITIALIZATION ---
@st.cache_resource
def initialize_firebase():
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets and "service_account_json" in st.secrets["firebase"]:
                service_account_info = json.loads(st.secrets["firebase"]["service_account_json"])
                cred = credentials.Certificate(service_account_info)
                return firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://airflowsystem-9ac1c-default-rtdb.firebaseio.com/'
                })
    except Exception as e:
        st.error(f"Firebase Connection Error: {e}")
    return None

initialize_firebase()

# --- LOGIN SCREEN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("<div class='main-header'>⚡ AIRFLOW SYSTEMS</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>CLOUD RFID LOGISTICS & TERMINAL MANAGER</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔒 Terminal Authentication")
        username = st.text_input("Username / Terminal ID")
        password = st.text_input("Access Security Key", type="password")
        
        if st.button("Authorize Terminal", use_container_width=True):
            if username == "admin" and password == "airflow77":
                st.session_state["logged_in"] = True
                st.success("Access Granted! Loading cloud modules...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Security Credentials.")
    st.stop()

# --- MAIN DASHBOARD ---
st.markdown("<div class='main-header'>⚡ AIRFLOW SYSTEMS CONTROL CENTER</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-sub'>REAL-TIME INVENTORY & OPERATIONS TERMINAL</div>", unsafe_allow_html=True)

if st.sidebar.button("🔒 Lock Terminal"):
    st.session_state["logged_in"] = False
    st.rerun()

# --- DATA FETCHING ---
try:
    ref = db.reference('RFID_Data')
    data = ref.get()
except Exception as e:
    data = None
    st.error("Failed to connect to Cloud Database.")

# Data processing
df = pd.DataFrame.from_dict(data, orient='index') if data else pd.DataFrame()

# Metrics
total_scans = len(df) if not df.empty else 0
active_items = len(df[df['Status'] == 'IN WAREHOUSE']) if not df.empty and 'Status' in df.columns else 0

m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(f"<div class='metric-box'><h5>📦 Total Items</h5><h2>{total_scans}</h2></div>", unsafe_allow_html=True)
with m_col2:
    st.markdown(f"<div class='metric-box' style='border-left-color: #10B981;'><h5>✅ Active</h5><h2>{active_items}</h2></div>", unsafe_allow_html=True)
with m_col3:
    st.markdown(f"<div class='metric-box' style='border-left-color: #F59E0B;'><h5>⚡ Status</h5><h2>{'ONLINE' if data else 'OFFLINE'}</h2></div>", unsafe_allow_html=True)

st.write("---")
st.subheader("📋 Real-Time RFID Scans Log")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No scan data available in the Cloud Database.")
