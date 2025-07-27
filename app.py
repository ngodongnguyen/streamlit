import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from rapidfuzz import fuzz, process

# --- Cài đặt ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1L_-FzunPRvx2Z7VlODivc4xQxaO8Won7nJxRWNq9RUg"
SHEET_NAME = "Tổng hợp dự án"
THRESHOLD = 90  # Ngưỡng fuzzy

# --- Load dữ liệu từ Google Sheet ---
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

    if not data:
        return pd.DataFrame()
    header = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=header)

# --- ✅ FIX: Không xóa dấu cách nữa ---
def normalize(text):
    return str(text).strip().lower()

# --- Chuẩn hóa dữ liệu từ sheet để so sánh nhanh ---
@st.cache_data
def preprocess_data(df):
    flat_list = []
    pos_map = []
    for idx, row in df.iterrows():
        for col in df.columns[:10]:
            val = str(row[col]).strip()
            if val and val.lower() != "nan":
                normalized = normalize(val)
                flat_list.append(normalized)
                pos_map.append((idx + 2, col))  # Lưu dòng + cột
    return flat_list, pos_map

# --- Kiểm tra từng tên ---
def check_name_fast(target, flat_list, pos_map):
    target_text = normalize(target)
    matches = process.extract(
        query=target_text,
        choices=flat_list,
        scorer=fuzz.partial_ratio,
        score_cutoff=THRESHOLD,
        limit=1
    )
    if matches:
        best_match_text, score, _ = matches[0]
        i = flat_list.index(best_match_text)
        return (
            "✔️ Trùng",
            f"Dòng {pos_map[i][0]}, Cột {pos_map[i][1]}",
            score,
            best_match_text
        )
    else:
        return ("❌ Không trùng", "", 0, "")

# --- Giao diện ---
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
            st.error("❌ Không thể đọc dữ liệu từ Google Sheet.")
        else:
            flat_list, pos_map = preprocess_data(df)
            target_names = [line.strip() for line in names_input.strip().splitlines() if line.strip()]
            results = []

            # --- Thanh tiến trình ---
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, name in enumerate(target_names):
                status, position, score, matched_text = check_name_fast(name, flat_list, pos_map)
                results.append({
                    "Tên kiểm tra": name,
                    "Kết quả": status,
                    "Vị trí nếu trùng": position,
                    "Giống bao nhiêu %": score if score > 0 else "",
                    "Giống với từ nào": matched_text if matched_text else ""
                })

                percent_complete = int((i + 1) / len(target_names) * 100)
                progress_bar.progress(percent_complete / 100)
                status_text.text(f"⏳ Đang xử lý {i + 1}/{len(target_names)} tên...")

            status_text.text("✅ Đã kiểm tra xong.")
            st.markdown("### 📋 Kết quả")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
