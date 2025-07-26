import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from rapidfuzz import fuzz

# --- Cài đặt ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1L_-FzunPRvx2Z7VlODivc4xQxaO8Won7nJxRWNq9RUg"
SHEET_NAME = "Tổng hợp dự án"
THRESHOLD = 90  # Độ tương đồng fuzzy để tính là trùng

# --- Hàm xác thực và tải dữ liệu từ Google Sheets ---
@st.cache_data
def load_data_from_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"], scopes=scope
    )

    gc = gspread.authorize(creds)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.worksheet(SHEET_NAME)
    data = worksheet.get_all_values()

    # Dòng 1 là tiêu đề, các dòng sau là dữ liệu
    if not data:
        return pd.DataFrame()  # Trống hoàn toàn

    header = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=header)

# --- Chuẩn hóa chuỗi ---
def normalize(text):
    return str(text).strip().lower().replace(" ", "")

# --- So sánh tên ---
def check_name(target, df):
    target_text = normalize(target)
    for idx, row in df.iterrows():
        for col in df.columns[:10]:  # chỉ kiểm tra 10 cột đầu
            value = normalize(row[col])
            if not value or value == "nan":
                continue
            score = fuzz.ratio(value, target_text)
            if score >= THRESHOLD:
                return ("✔️ Trùng", f"Dòng {idx+2}, Cột {col}")  # +2 vì pandas tính từ 0 và bỏ dòng header
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

        if df.empty:
            st.error("❌ Không thể đọc dữ liệu từ Google Sheet (có thể bị trống).")
        else:
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
