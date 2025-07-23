import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# --- Cài đặt ---
threshold = 80
csv_file = "test.csv"

# --- Load CSV ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv(csv_file)
    except Exception as e:
        st.error(f"❌ Không thể đọc file CSV: {e}")
        st.stop()

df = load_data()
columns_to_check = df.columns[:10]

# --- Chuẩn hóa chuỗi ---
def normalize(text):
    return text.strip().lower().replace(" ", "")

# --- Hàm so sánh từng tên ---
def check_name(target):
    target_text = normalize(target)
    for idx, row in df.iterrows():
        for col in columns_to_check:
            raw_value = str(row[col])
            value = normalize(raw_value)
            if not value or value == "nan":
                continue
            score = fuzz.ratio(value, target_text)
            if score >= threshold:
                return ("✔️ Trùng", f"Dòng {idx+1}, Cột {col}")
    return ("❌ Không trùng", "")

# --- Giao diện ---
st.set_page_config(page_title="Kiểm Tra Trùng Tên", layout="wide")
st.title("🔎 Kiểm Tra Tên Trùng Với Dữ Liệu CSV")
st.caption("So sánh danh sách tên bạn nhập với dữ liệu trong 10 cột đầu của file CSV (`test.csv`).")

names_input = st.text_area("📥 Nhập danh sách tên cần kiểm tra (mỗi dòng 1 tên):")

if st.button("✅ Kiểm tra"):
    if not names_input.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất một tên.")
    else:
        target_names = [line.strip() for line in names_input.strip().splitlines() if line.strip()]
        results = []

        with st.spinner("🔄 Đang kiểm tra, vui lòng đợi..."):
            for name in target_names:
                status, position = check_name(name)
                results.append({
                    "Tên kiểm tra": name,
                    "Kết quả": status,
                    "Vị trí nếu trùng": position
                })

        st.success("✅ Đã kiểm tra xong.")
        st.markdown("### 📋 Kết quả kiểm tra")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
