import streamlit as st
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Airflow Cloud RFID Center", page_icon="⚡", layout="wide")

# MOBILE RESPONSIVE CSS
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] { padding: 10px; font-size: 14px; }
    .metric-box { padding: 15px; background-color: #F8FAFC; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FIREBASE INIT ---
@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        json_str = st.secrets["firebase"]["service_account_json"].strip()
        service_account_info = json.loads(json_str)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://airflowsystem-9ac1c-default-rtdb.firebaseio.com/'})

try:
    initialize_firebase()
except Exception as e:
    st.error("Firebase Connection Error!")

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("⚡ Airflow Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "airflow77":
            st.session_state["logged_in"] = True
            st.rerun()
    st.stop()

# --- MAIN UI ---
st.title("⚡ Airflow Control")
tabs = st.tabs(["Dash", "Manage", "Log"])

# TAB 1: DASHBOARD
with tabs[0]:
    ref = db.reference('RFID_Data')
    data = ref.get()
    df = pd.DataFrame.from_dict(data, orient='index') if data else pd.DataFrame()
    
    col1, col2 = st.columns(2)
    with col1: st.markdown(f"<div class='metric-box'>📦 Total Items: {len(df) if not df.empty else 0}</div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='metric-box'>⚡ Status: {'ONLINE' if data else 'READY'}</div>", unsafe_allow_html=True)
    
    if not df.empty: st.dataframe(df, use_container_width=True)
    else: st.info("No data found.")

# TAB 2: MANAGE
with tabs[1]:
    st.subheader("Manage Inventory")
    item_id = st.text_input("Item ID")
    item_name = st.text_input("Item Name")
    
    if st.button("Update Inventory"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Update Main Data
        db.reference(f'RFID_Data/{item_id}').set({"Name": item_name, "Status": "IN WAREHOUSE", "Time": now})
        # Push to History
        db.reference('History').push({"Action": "Added/Updated", "ID": item_id, "Name": item_name, "Time": now})
        st.success("Item Updated and logged in History!")
        st.rerun()

# TAB 3: LOG
with tabs[2]:
    st.subheader("System History Log")
    hist = db.reference('History').get()
    if hist:
        hist_df = pd.DataFrame.from_dict(hist, orient='index')
        st.dataframe(hist_df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("No history logs available yet.")

if st.sidebar.button("🔒 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()
