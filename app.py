import streamlit as st
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Airflow Systems Pro", page_icon="⚡", layout="centered")

@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        json_str = st.secrets["firebase"]["service_account_json"].strip()
        cred = credentials.Certificate(json.loads(json_str))
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://airflowsystem-9ac1c-default-rtdb.firebaseio.com/'})

initialize_firebase()

# --- LOGIN ---
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("⚡ Airflow Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "airflow77":
            st.session_state["logged_in"] = True
            st.rerun()
        else: st.error("Galat credentials!")
    st.stop()

# --- MAIN UI ---
st.title("⚡ Airflow Control Center")
menu = st.selectbox("Menu Chunne:", ["Dashboard", "Manage Inventory", "History Logs"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.subheader("Live Inventory")
    data = db.reference('RFID_Data').get()
    if data:
        df = pd.DataFrame.from_dict(data, orient='index')
        st.dataframe(df, use_container_width=True)
    else: st.info("Koi item nahi mila.")

# --- MANAGE ---
elif menu == "Manage Inventory":
    st.subheader("Inventory Control")
    action = st.radio("Kya karna hai?", ["Add/Update Item", "Delete Item (Remove)"])
    
    if action == "Add/Update Item":
        epc = st.text_input("EPC ID (Unique Code)")
        name = st.text_input("Product Name")
        if st.button("Save/Update"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {"EPC": epc, "Item_Name": name, "Status": "IN WAREHOUSE", "Timestamp": now}
            db.reference(f'RFID_Data/{epc}').set(data)
            db.reference('History').push({**data, "Action": "Added/Updated"})
            st.success("Item successfully update ho gaya!")
            
    else:
        del_epc = st.text_input("Delete karne ke liye EPC ID daalein")
        if st.button("Confirm Delete"):
            db.reference(f'RFID_Data/{del_epc}').delete()
            db.reference('History').push({"Action": "Deleted", "EPC": del_epc, "Time": str(datetime.now())})
            st.warning("Item database se hata diya gaya!")

# --- LOGS ---
elif menu == "History Logs":
    st.subheader("Saari Purani Activity")
    hist = db.reference('History').get()
    if hist:
        df_hist = pd.DataFrame.from_dict(hist, orient='index')
        st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True)

if st.sidebar.button("🔒 Logout"):
    st.session_state["logged_in"] = False
    st.rerun()
