import streamlit as st
import pandas as pd
import csv
import os
import requests
from bs4 import BeautifulSoup

# --- Giao diện ---
st.set_page_config(page_title="📁 Tải lên và Kiểm tra Dữ liệu", layout="wide")
st.title("📁 Tải lên và Kiểm tra Dữ liệu Mới")

# Hiển thị nút tải lên file
uploaded_file = st.file_uploader("Chọn file CSV để tải lên", type=["csv"])

# Kiểm tra nếu người dùng đã tải file lên
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
    # Nếu không có file tải lên, tự động chạy requests/BeautifulSoup để thu thập dữ liệu
    st.write("Không có file tải lên, bắt đầu thu thập dữ liệu từ web...")

    # URL để lấy thông tin từ trang web
    url = "https://marketplace.uppromote.com/offers/find-offers?page=1&per_page=100&tab=all-offers"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Gửi yêu cầu GET đến trang web
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        st.write("Đang thu thập dữ liệu từ trang web...")

        # Phân tích cú pháp HTML bằng BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tìm tất cả các thẻ chứa tên thương hiệu và hoa hồng
        merchant_names = soup.select("div.styles_title__4_7RE")
        commissions = soup.select("div.styles_productCommissions__aR3Vi span")

        # Mở file CSV để ghi
        output_file = 'uppromote_merchants.csv'
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Tên thương hiệu", "Hoa hồng"])

            # Lặp qua các thẻ và ghi dữ liệu vào file CSV
            for name, commission in zip(merchant_names, commissions):
                try:
                    merchant_name = name.get_text(strip=True)
                    commission_text = commission.get_text(strip=True)
                    writer.writerow([merchant_name, commission_text])
                    st.write(f"Đã lấy: {merchant_name} - {commission_text}")
                except Exception as e:
                    st.write(f"Lỗi khi xử lý merchant: {e}")

        st.success("Đã thu thập và lưu dữ liệu mới từ trang web vào `uppromote_merchants.csv`.")
    else:
        st.error("Không thể truy cập trang web, vui lòng thử lại sau.")
