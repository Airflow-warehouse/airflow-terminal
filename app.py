import streamlit as st
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION ---
st.set_page_config(page_title="Airflow Operations", page_icon="⚡", layout="wide")

# PROFESSIONAL UI STYLING
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    .status-card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTION FOR IST TIME ---
def get_ist_time():
    # Indian Standard Time (IST) is UTC + 5:30
    ist_zone = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_zone).strftime("%Y-%m-%d %H:%M:%S")

# --- FIREBASE INIT ---
@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        json_str = st.secrets["firebase"]["service_account_json"].strip()
        cred = credentials.Certificate(json.loads(json_str))
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://airflowsystem-9ac1c-default-rtdb.firebaseio.com/'})

try:
    initialize_firebase()
except Exception as e:
    st.error("Database connection failed. Please verify your Secrets configuration.")

# --- AUTH ---
if "logged_in" not in st.session_state: 
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("⚡ Airflow Operations Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Login"):
            if user == "admin" and pwd == "airflow77":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")
                
    st.markdown("---")
    st.markdown("⚙️ **Forgot Password?**")
    st.info("To reset your password, please contact your system administrator at **support@airflow.com** with your registered details.")
    st.stop()

# --- MAIN DASHBOARD ---
st.title("⚡ Airflow Operations Center")
menu = st.selectbox("Navigation Menu", ["Live Dashboard", "Inventory Management", "System History"])

# 1. LIVE DASHBOARD
if menu == "Live Dashboard":
    st.subheader("Real-time ESP32 Feed")
    data = db.reference('RFID_Data').get()
    if data:
        df = pd.DataFrame.from_dict(data, orient='index')
        # Reordering columns for professional look
        cols = [c for c in ["EPC", "Item_Name", "Status", "Timestamp"] if c in df.columns]
        if cols:
            df = df[cols]
        st.dataframe(df, use_container_width=True)
        st.success("ESP32 Connection Status: ONLINE & Streaming")
    else: 
        st.warning("No active items found. Waiting for ESP32 reader broadcast...")

# 2. INVENTORY MANAGEMENT
elif menu == "Inventory Management":
    st.subheader("Inventory Control Management")
    
    action = st.radio("Select Action", ["Add / Update Item", "Remove Item (Delete)"])
    
    if action == "Add / Update Item":
        epc = st.text_input("EPC ID", help="Scan or type the unique RFID Tag EPC")
        name = st.text_input("Item Name")
        if st.button("Update Inventory"):
            if epc and name:
                now = get_ist_time()  # Indian Standard Time (IST) use kiya hai
                # Save to main data node
                item_data = {"EPC": epc, "Item_Name": name, "Status": "IN WAREHOUSE", "Timestamp": now}
                db.reference(f'RFID_Data/{epc}').set(item_data)
                # Log to history
                db.reference('History').push({"Action": "Added/Updated", "EPC": epc, "Item_Name": name, "Timestamp": now})
                st.success(f"Item '{name}' successfully updated in inventory and logged.")
            else:
                st.error("Please fill in both EPC ID and Item Name.")
                
    elif action == "Remove Item (Delete)":
        del_epc = st.text_input("Enter EPC to Delete")
        if st.button("Confirm Delete"):
            if del_epc:
                # Check if item exists before deleting
                existing_item = db.reference(f'RFID_Data/{del_epc}').get()
                item_name = existing_item.get("Item_Name", "Unknown Item") if existing_item else "Unknown Item"
                
                # Perform Delete
                db.reference(f'RFID_Data/{del_epc}').delete()
                # Log action to history
                now = get_ist_time()  # Indian Standard Time (IST) use kiya hai
                db.reference('History').push({"Action": "Deleted", "EPC": del_epc, "Item_Name": item_name, "Timestamp": now})
                st.warning(f"Item with EPC '{del_epc}' removed from inventory.")
            else:
                st.error("Please enter a valid EPC ID to delete.")

# 3. SYSTEM HISTORY
elif menu == "System History":
    st.subheader("System Activity Logs")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Clear Activity History"):
            db.reference('History').delete()
            st.success("History log successfully cleared.")
            st.rerun()
            
    hist = db.reference('History').get()
    if hist:
        df_hist = pd.DataFrame.from_dict(hist, orient='index')
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True)
    else: 
        st.info("No activity logs available yet.")

# LOGOUT
if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()
