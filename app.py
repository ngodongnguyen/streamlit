import streamlit as st
import pandas as pd
import gspread
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from rapidfuzz import fuzz
import argparse

# --- Cài đặt ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZIz_KKkpEHAa83je30Q73z6dKWWGicbMQsqM0PKqn3Q"
SHEET_NAME = "Tổng hợp dự án"
CREDENTIAL_FILE = "client_secret.json"
TOKEN_FILE = "token.json"
THRESHOLD = 90  # Độ tương đồng fuzzy để tính là trùng

# --- Hàm xác thực và tải dữ liệu từ Google Sheets ---
@st.cache_data
def load_data_from_gsheet():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

    store = Storage(TOKEN_FILE)
    creds = store.get()

    if not creds or creds.invalid:
        flow = flow_from_clientsecrets(CREDENTIAL_FILE, scope)
        flags = argparse.Namespace(
            auth_host_name='localhost',
            auth_host_port=[8080, 8090],
            noauth_local_webserver=False,
            logging_level='ERROR'
        )
        creds = run_flow(flow, store, flags)

    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet(SHEET_NAME)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# --- Chuẩn hóa chuỗi ---
def normalize(text):
    return str(text).strip().lower().replace(" ", "")

# --- So sánh tên ---
def check_name(target, df):
    target_text = normalize(target)
    for idx, row in df.iterrows():
        for col in df.columns[:10]:
            value = normalize(row[col])
            if not value or value == "nan":
                continue
            score = fuzz.ratio(value, target_text)
            if score >= THRESHOLD:
                return ("✔️ Trùng", f"Dòng {idx+1}, Cột {col}")
    return ("❌ Không trùng", "")

# --- Giao diện Streamlit ---
st.set_page_config(page_title="Kiểm Tra Trùng Tên", layout="wide")
st.title("🔍 Kiểm Tra Tên Trùng Trong Google Sheet")
st.caption("Tìm kiếm tên trùng trong 10 cột đầu của sheet 'Tổng hợp dự án'.")

names_input = st.text_area("📥 Nhập danh sách tên cần kiểm tra (mỗi dòng 1 tên):")

if st.button("✅ Kiểm tra"):
    if not names_input.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất một tên.")
    else:
        with st.spinner("🔄 Đang tải dữ liệu từ Google Sheet..."):
            df = load_data_from_gsheet()

        target_names = [line.strip() for line in names_input.strip().splitlines() if line.strip()]
        results = []

        with st.spinner("🔍 Đang kiểm tra trùng tên..."):
            for name in target_names:
                status, position = check_name(name, df)
                results.append({
                    "Tên kiểm tra": name,
                    "Kết quả": status,
                    "Vị trí nếu trùng": position
                })

        st.success("✅ Đã kiểm tra xong.")
        st.markdown("### 📋 Kết quả")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
