import streamlit as st
import pandas as pd
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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
    # Nếu không có file tải lên, tự động chạy Selenium để thu thập dữ liệu
    st.write("Không có file tải lên, bắt đầu thu thập dữ liệu từ web...")

    # Khởi tạo Selenium
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    service = Service('C:/chromedriver/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Truy cập trang đăng nhập và thu thập dữ liệu
    login_url = "https://marketplace.uppromote.com/login"
    driver.get(login_url)
    time.sleep(5)

    # Điền thông tin tài khoản
    email_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your email']")  # Tìm input email
    email_input.send_keys("nguyen@lldmedia.com")
    password_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")  # Tìm input password
    password_input.send_keys("Ngodongnguyen2004?")
    login_button = driver.find_element(By.XPATH, "//button/span[text()='Login']")  # Tìm nút Login
    login_button.click()
    time.sleep(5)  # Chờ trang load

    # Tiến hành thu thập dữ liệu từ các trang merchant
    start_url = "https://marketplace.uppromote.com/offers/find-offers?page=1&per_page=100&tab=all-offers"
    driver.get(start_url)
    time.sleep(5)  # Chờ trang load

    # Mở file CSV để ghi
    output_file = 'uppromote_merchants.csv'
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Tên thương hiệu", "Hoa hồng"])

        # Lặp qua các trang
        while True:
            merchant_names = driver.find_elements(By.CSS_SELECTOR, "div.styles_title__4_7RE")
            commissions = driver.find_elements(By.CSS_SELECTOR, "div.styles_productCommissions__aR3Vi span")

            for name, commission in zip(merchant_names, commissions):
                try:
                    merchant_name = name.text.strip()
                    commission_text = commission.text.strip()
                    writer.writerow([merchant_name, commission_text])
                    print(f"Đã lấy: {merchant_name} - {commission_text}")
                except Exception as e:
                    print(f"Lỗi khi xử lý merchant: {e}")

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "i.fa-angle-right")
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                time.sleep(1)
                next_button.click()
                print("Bấm Next...")
                time.sleep(5)  # Chờ trang mới load
            except Exception as e:
                print("Không tìm thấy nút Next nữa. Kết thúc.")
                break

    driver.quit()

    st.success("Đã thu thập và lưu dữ liệu mới từ trang web vào `uppromote_merchants.csv`.")

