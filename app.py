import streamlit as st
import pandas as pd
import sys
import time
import firebase_admin
from firebase_admin import credentials, db

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="Airflow Cloud RFID Center", page_icon="⚡", layout="wide")

# Custom CSS for Corporate Industrial UI
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
            if hasattr(st, "secrets") and "firebase" in st.secrets:
                cred = credentials.Certificate(dict(st.secrets["firebase"]))
                return firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase"]["databaseURL"]})
            else:
                try:
                    cred = credentials.Certificate("serviceAccountKey.json")
                    return firebase_admin.initialize_app(cred, {'databaseURL': 'https://airflow-rfid-default-rtdb.firebaseio.com/'})
                except:
                    return None
    except Exception as e:
        st.error(f"Firebase Init Error: {e}")
    return None

initialize_firebase()

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in sys.modules and "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- LOGIN SCREEN ---
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
                st.error("Invalid Security Credentials. Access Denied.")
    st.stop()

# --- MAIN DASHBOARD (If Logged In) ---
st.markdown("<div class='main-header'>⚡ AIRFLOW SYSTEMS CONTROL CENTER</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-sub'>REAL-TIME INVENTORY & OPERATIONS TERMINAL</div>", unsafe_allow_html=True)

# Logout button in sidebar
if st.sidebar.button("🔒 Lock Terminal"):
    st.session_state["logged_in"] = False
    st.rerun()

# --- READ REAL-TIME DATA FROM FIREBASE ---
try:
    ref = db.reference('RFID_Data')
    data = ref.get()
except Exception as e:
    data = None
    st.warning("Running in local demo mode. Cloud database disconnected.")

# Mock data fallback if firebase is empty or errors out
if not data:
    data = {
        "item1": {"EPC": "E280113020005781", "Item_Name": "Aluminium Tube Heavy", "Timestamp": "2026-06-15 14:10:22", "Status": "IN WAREHOUSE"},
        "item2": {"EPC": "E280113020009245", "Item_Name": "Compressor Unit V3", "Timestamp": "2026-06-15 14:12:05", "Status": "DISPATCHED"}
    }

# Convert to DataFrame
df = pd.DataFrame.from_dict(data, orient='index')

# Top Metrics Row
total_scans = len(df)
active_items = len(df[df['Status'] == 'IN WAREHOUSE']) if 'Status' in df.columns else total_scans

m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(f"<div class='metric-box'><h5>📦 Total Registered Items</h5><h2>{total_scans}</h2></div>", unsafe_allow_html=True)
with m_col2:
    st.markdown(f"<div class='metric-box' style='border-left-color: #10B981;'><h5>✅ Active Inventory</h5><h2>{active_items}</h2></div>", unsafe_allow_html=True)
with m_col3:
    st.markdown(f"<div class='metric-box' style='border-left-color: #F59E0B;'><h5>⚡ System Status</h5><h2>ONLINE</h2></div>", unsafe_allow_html=True)

st.write("---")

# Main Section
st.subheader("📋 Real-Time RFID Scans Log")
st.dataframe(df, use_container_width=True)

# Footer
st.markdown("<br><hr><p style='text-align: center; color: gray; font-size: 11px;'>Airflow Warehouse Terminal v2.1 • Secured via Snowflake Cloud</p>", unsafe_allow_html=True)
