import streamlit as st
import pandas as pd
import gspread
import unicodedata
import re
from google.oauth2.service_account import Credentials
from rapidfuzz import fuzz, process

# --- Cài đặt ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1L_-FzunPRvx2Z7VlODivc4xQxaO8Won7nJxRWNq9RUg"
SHEET_NAME = "Tổng hợp dự án"
THRESHOLD = 90
PRE_FILTER_THRESHOLD = 80

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

# --- Hàm chuẩn hóa mạnh mẽ ---
def normalize(text):
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s-]', '', text)
    return text

# --- Tiền xử lý dữ liệu từ sheet, tránh lỗi dtype object ---
@st.cache_data
def preprocess_data(df):
    flat_list = []
    pos_map = []

    columns = df.columns.tolist()[:10]  # Chỉ lấy 10 cột đầu theo tên

    for idx, row in df.iterrows():
        for col in columns:
            try:
                val = row[col]
                if pd.isna(val): continue  # Bỏ qua ô rỗng

                val_str = str(val).strip()
                if val_str and val_str.lower() != "nan":
                    normalized = normalize(val_str)
                    flat_list.append(normalized)
                    pos_map.append((idx + 2, col))  # +2 để tính cả header + index từ 0
            except Exception as e:
                st.warning(f"⚠️ Lỗi tại dòng {idx+2}, cột {col}: {e}")

    return flat_list, pos_map

# --- Hàm so khớp tên có in debug ---
def check_name_fast(target, flat_list, pos_map):
    target_text = normalize(target)

    matches = process.extract(
        query=target_text,
        choices=flat_list,
        scorer=fuzz.partial_ratio,
        limit=3
    )

    best_score = 0
    best_text = ""
    best_index = -1
    debug_info = []

    st.markdown(f"#### 🔍 Kiểm tra tên: `{target}`")

    for match_text, partial_score, _ in matches:
        line = f"- So với: `{match_text}` → partial_ratio: **{partial_score}%**"
        if partial_score >= PRE_FILTER_THRESHOLD:
            full_score = fuzz.ratio(target_text, match_text)
            line += f" → ratio: **{full_score}%**"
            if full_score > best_score:
                best_score = full_score
                best_text = match_text
                best_index = flat_list.index(match_text)
        debug_info.append(line)

    for line in debug_info:
        st.markdown(line)
    st.markdown("---")

    if best_score >= THRESHOLD:
        row, col = pos_map[best_index]
        return ("✔️ Trùng", f"Dòng {row}, Cột {col}", best_score, best_text)
    else:
        return ("❌ Không trùng", "", 0, "")

# --- Giao diện chính ---
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

            # 🧾 In thử xem dữ liệu sheet có gì bất thường
            st.markdown("### 🧾 10 dòng đầu trong danh sách Google Sheet đã chuẩn hóa:")
            st.code("\n".join(flat_list[:10]))

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
