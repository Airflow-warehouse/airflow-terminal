import streamlit as st
import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Page Configuration for Airflow Enterprise
st.set_page_config(page_title="Airflow Cloud RFID Center", page_icon="💨", layout="wide")

# Airflow Corporate Theme Styling
st.markdown("""
    <style>
    .main-header { font-size:28pt !important; font-weight: bold; color: #0F172A; margin-bottom: 5px; font-family: 'Segoe UI', sans-serif; }
    .brand-sub { font-size:13pt !important; color: #2563EB; font-weight: 600; margin-bottom: 25px; letter-spacing: 1px; }
    .metric-box { padding: 20px; background-color: #F8FAFC; border-top: 4px solid #2563EB; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# --- FIREBASE INITIALIZATION ---
@st.cache_resource
def initialize_firebase():
    try:
        if not firebase_admin._apps:
            if hasattr(st, "secrets") and "firebase" in st.secrets:
                cred = credentials.Certificate(dict(st.secrets["firebase"]))
            else:
                try:
                    cred = credentials.Certificate("serviceAccountKey.json")
                except:
                    return None
            
            st.sidebar.info("Connecting to Airflow Cloud...")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://your-airflow-rtdb.firebaseio.com/'
            })
        return True
    except Exception as e:
        return None

firebase_ready = initialize_firebase()

def fetch_cloud_logs():
    if firebase_ready:
        ref = db.reference('rfid_logs')
        data = ref.get()
        if data:
            logs_list = [v for k, v in data.items()]
            df = pd.DataFrame(logs_list)
            return df.sort_values(by="Timestamp", ascending=False)
    return pd.DataFrame(columns=["Timestamp", "Tag_ID", "Product_Name", "Action", "Operator"])

def fetch_cloud_products():
    if firebase_ready:
        ref = db.reference('rfid_products')
        data = ref.get()
        if data:
            products_list = [v for k, v in data.items()]
            return pd.DataFrame(products_list)
    return pd.DataFrame(columns=["Tag_ID", "Product_Name", "Category", "Registered_On"])

def push_log_to_cloud(timestamp, tag_id, prod_name, action, operator):
    if firebase_ready:
        ref = db.reference('rfid_logs')
        ref.push({"Timestamp": timestamp, "Tag_ID": str(tag_id), "Product_Name": prod_name, "Action": action, "Operator": operator})

def push_product_to_cloud(tag_id, prod_name, category, registered_on):
    if firebase_ready:
        ref = db.reference('rfid_products')
        ref.child(str(tag_id)).set({"Tag_ID": str(tag_id), "Product_Name": prod_name, "Category": category, "Registered_On": registered_on})

# --- USER INTERFACE LOGIN STATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- AIRFLOW SECURE GATEWAY (LOGIN) ---
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>💨 AIRFLOW Systems</div>", unsafe_allowed_code=True)
    st.markdown("<div class='brand-sub'>SECURE INDUSTRIAL GATEWAY LOGIN</div>", unsafe_allowed_code=True)
    
    with st.form("login_form"):
        st.subheader("Authorized Personnel Only")
        username = st.text_input("Operator Username")
        password = st.text_input("Security Access Key", type="password")
        submit_login = st.form_submit_button("Authenticate System")
        
        # FIXED PASSWORD HERE
        if submit_login:
            if username == "admin" and password == "Airflow@123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Access Denied: Invalid Security Credentials.")
    st.stop()

# --- MAIN INDUSTRIAL DASHBOARD ---
df_logs = fetch_cloud_logs()
df_products = fetch_cloud_products()

st.markdown("<div class='main-header'>💨 AIRFLOW Asset Tracking Center</div>", unsafe_allowed_code=True)
st.markdown("<div class='brand-sub'>REAL-TIME ENTERPRISE RFID LOGISTICS CONTROL</div>", unsafe_allowed_code=True)

with st.sidebar:
    st.markdown("### 🔒 Airflow Security")
    st.caption("Terminal Status: **Secure Connection**")
    if st.button("Terminate Session"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📟 ESP32 Gateway Input")
    hardware_input = st.text_input("Hardware Receiver Buffer", key="hardware_scan")
    
    if hardware_input:
        if "-" in hardware_input:
            try:
                scanned_tag, action_status = hardware_input.split("-")
                scanned_tag = scanned_tag.strip()
                action_status = action_status.strip().upper()
                
                p_name = "Unregistered Cargo"
                if not df_products.empty:
                    prod_match = df_products[df_products["Tag_ID"].astype(str) == str(scanned_tag)]
                    if not prod_match.empty:
                        p_name = prod_match["Product_Name"].values[0]
                
                t_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                push_log_to_cloud(t_stamp, scanned_tag, p_name, action_status, "Airflow_ESP32_Node")
                st.success(f"Log Sync Success: {p_name}")
                st.rerun()
            except Exception as e:
                st.error("Data parse packet error.")
        else:
            st.warning("Invalid Hardware Protocol.")

tab1, tab2, tab3 = st.tabs(["📊 Live Floor Logistics", "📜 Central Audit Trails", "📦 Master Asset Registry"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><b>Airflow Registered Assets</b><br><span style='font-size:22pt; font-weight:bold; color:#2563EB;'>{len(df_products)}</span></div>", unsafe_allowed_code=True)
    with col2:
        st.markdown(f"<div class='metric-box'><b>Total Operations Processed</b><br><span style='font-size:22pt; font-weight:bold; color:#2563EB;'>{len(df_logs)}</span></div>", unsafe_allowed_code=True)
    with col3:
        status_text = "● Cloud Connected (Production)" if firebase_ready else "● Local Evaluation Sandbox"
        status_color = "#10B981" if firebase_ready else "#F59E0B"
        st.markdown(f"<div class='metric-box'><b>Network Infrastructure</b><br><span style='font-size:14pt; font-weight:bold; color:{status_color};'>{status_text}</span></div>", unsafe_allowed_code=True)
    
    st.markdown("<br>### Live Airflow Facility Inventory Map", unsafe_allowed_code=True)
    if df_logs.empty:
        st.info("System operational. Awaiting incoming scans from Airflow hardware nodes.")
    else:
        status_dict = {}
        for _, row in df_logs.sort_values("Timestamp").iterrows():
            status_dict[row["Product_Name"]] = row["Action"]
        
        current_inside = [k for k, v in status_dict.items() if v == "IN"]
        
        if current_inside:
            df_inside = pd.DataFrame({"Asset Identity": current_inside, "Current Sector": "Airflow Secure Bay 1"})
            st.dataframe(df_inside, use_container_width=True)
        else:
            st.warning("No physical assets currently detected inside Airflow tracking sectors.")

with tab2:
    st.markdown("### Official System Audit Sheets")
    st.dataframe(df_logs, use_container_width=True)
    if not df_logs.empty:
        st.download_button("Download Airflow Ledger (CSV)", df_logs.to_csv(index=False), "airflow_master_ledger.csv", "text/csv")

with tab3:
    st.markdown("### New Asset Authorization Form")
    with st.form("reg_form"):
        t_id = st.text_input("RFID Serial (Tag UID)")
        p_name = st.text_input("Asset Description / Cargo Name")
        p_cat = st.selectbox("Logistics Category", ["Heavy Machinery", "Electronics", "Raw Materials", "Finished Goods", "Office Equipment"])
        submit_reg = st.form_submit_button("Verify & Provision Asset")
        
        if submit_reg:
            if t_id and p_name:
                reg_date = datetime.now().strftime("%Y-%m-%d")
                push_product_to_cloud(t_id, p_name, p_cat, reg_date)
                st.success(f"Asset '{p_name}' has been successfully provisioned into Airflow Registry.")
                st.rerun()
            else:
                st.error("All security registry parameters are mandatory.")
                
    st.markdown("---")
    st.markdown("#### Authorized Corporate Assets List")
    st.dataframe(df_products, use_container_width=True)
