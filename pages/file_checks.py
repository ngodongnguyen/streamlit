import streamlit as st
import pandas as pd
import csv
import os

# --- Giao diện ---
st.set_page_config(page_title="📁 Tải lên và Kiểm tra Dữ liệu", layout="wide")
st.title("📁 Tải lên và Kiểm tra Dữ liệu Mới")

# Hiển thị nút tải lên file
uploaded_file = st.file_uploader("Chọn file CSV để tải lên", type=["csv"])

# Kiểm tra xem người dùng đã tải file lên chưa
if uploaded_file is not None:
    # Đọc file CSV tải lên và hiển thị
    new_data = pd.read_csv(uploaded_file)
    st.write("Dữ liệu mới đã tải lên:")
    st.write(new_data)

    # Kiểm tra xem có dữ liệu cũ không
    if os.path.exists("uppromote_merchants.csv"):
        st.write("Đang so sánh với dữ liệu cũ...")

        # Đọc dữ liệu cũ từ file CSV
        old_data = pd.read_csv("uppromote_merchants.csv")

        # Kiểm tra các dữ liệu mới không có trong dữ liệu cũ
        new_entries = new_data[~new_data.apply(tuple, 1).isin(old_data.apply(tuple, 1))]

        if not new_entries.empty:
            st.write("Có dữ liệu mới:")
            st.write(new_entries)

            # Nút để thêm dữ liệu mới vào file cũ
            if st.button("Thêm dữ liệu mới vào file"):
                # Thêm dữ liệu mới vào file cũ
                with open("uppromote_merchants.csv", mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for row in new_entries.values:
                        writer.writerow(row)

                st.success("Dữ liệu mới đã được thêm vào file!")
        else:
            st.write("Không có dữ liệu mới.")
    else:
        st.write("Không có dữ liệu cũ. Tạo file mới...")
        # Xuất dữ liệu mới ra một file CSV mới
        new_data.to_csv("uppromote_merchants.csv", index=False)
        st.success("Dữ liệu mới đã được xuất ra file `uppromote_merchants.csv`.")

else:
    st.write("Chưa có file được tải lên.")
