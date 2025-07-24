import streamlit as st
import pandas as pd
import csv
import os
import requests
from bs4 import BeautifulSoup

# --- Cấu hình giao diện Streamlit ---
st.set_page_config(page_title="📁 Công cụ Dữ liệu Uppromote", layout="wide")
st.title("📁 Công cụ Dữ liệu Uppromote: Đào và Kiểm tra")

# Tên file CSV sẽ được sử dụng để lưu trữ dữ liệu
CSV_FILE_NAME = "uppromote_merchants.csv"

# --- Hàm thu thập dữ liệu từ trang web ---
@st.cache_data(ttl=3600) # Cache dữ liệu đã thu thập trong 1 giờ để tránh gọi lại nhiều lần
def scrape_data_from_web():
    """
    Thu thập tên thương hiệu và hoa hồng từ trang marketplace.uppromote.com.
    Hiển thị thông báo tiến trình và xử lý lỗi.
    """
    url = "https://marketplace.uppromote.com/offers/find-offers?page=1&per_page=100&tab=all-offers"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Sử dụng st.spinner để hiển thị thông báo "đang trong quá trình"
    with st.spinner("Đang trong quá trình lấy dữ liệu từ web... Vui lòng chờ."):
        try:
            response = requests.get(url, headers=headers, timeout=10) # Thêm timeout
            response.raise_for_status()  # Ném HTTPError cho các phản hồi lỗi (4xx hoặc 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Chọn các thẻ chứa tên thương hiệu và hoa hồng
            merchant_names = soup.select("div.styles_title__4_7RE")
            commissions = soup.select("div.styles_productCommissions__aR3Vi span")

            data = []
            # Lặp qua các thẻ và trích xuất dữ liệu
            for name, commission in zip(merchant_names, commissions):
                merchant_name = name.get_text(strip=True)
                commission_text = commission.get_text(strip=True)
                data.append([merchant_name, commission_text])

            if not data:
                st.warning("Không tìm thấy dữ liệu nào từ trang web. Có thể cấu trúc trang đã thay đổi.")
                return pd.DataFrame(columns=["Tên thương hiệu", "Hoa hồng"]) # Trả về DataFrame rỗng

            return pd.DataFrame(data, columns=["Tên thương hiệu", "Hoa hồng"])

        except requests.exceptions.RequestException as e:
            st.error(f"Lỗi khi truy cập trang web: {e}. Vui lòng kiểm tra kết nối internet hoặc URL.")
            return None # Trả về None nếu có lỗi mạng
        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình thu thập dữ liệu: {e}")
            return None # Trả về None nếu có lỗi khác

# --- Logic chính của ứng dụng ---

# Tạo 2 cột để đặt các nút
col1, col2 = st.columns(2)

with col1:
    scrape_new_data_button = st.button("Đào dữ liệu mới")

with col2:
    check_data_button = st.button("Kiểm tra dữ liệu")

# Xử lý khi nút "Đào dữ liệu mới" được nhấn
if scrape_new_data_button:
    st.info("Bắt đầu đào dữ liệu mới từ trang web...")
    scraped_df = scrape_data_from_web() # Gọi hàm thu thập dữ liệu

    if scraped_df is not None: # Chỉ xử lý nếu việc thu thập dữ liệu thành công
        # Lưu dữ liệu mới vào file CSV, ghi đè nếu file đã tồn tại
        scraped_df.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8')
        st.success(f"Đã đào và lưu dữ liệu mới vào file `{CSV_FILE_NAME}` thành công.")
        st.write("Dữ liệu mới đã đào:")
        st.write(scraped_df)

# Xử lý khi nút "Kiểm tra dữ liệu" được nhấn
elif check_data_button:
    st.info("Bắt đầu kiểm tra dữ liệu...")
    current_scraped_data = scrape_data_from_web() # Thu thập dữ liệu mới nhất để so sánh

    if current_scraped_data is not None: # Chỉ xử lý nếu việc thu thập dữ liệu thành công
        if os.path.exists(CSV_FILE_NAME):
            st.write("Đang so sánh với dữ liệu cũ đã lưu...")
            try:
                old_data = pd.read_csv(CSV_FILE_NAME, encoding='utf-8')

                # Đảm bảo các cột của dữ liệu mới và cũ khớp nhau để so sánh chính xác
                if not current_scraped_data.columns.equals(old_data.columns):
                    st.warning("Cột dữ liệu mới và cũ không khớp. Không thể so sánh chính xác.")
                    st.write("Dữ liệu mới (từ web):")
                    st.write(current_scraped_data)
                    st.write("Dữ liệu cũ (từ file):")
                    st.write(old_data)
                else:
                    # Tìm các hàng mới không có trong dữ liệu cũ
                    # Chuyển đổi DataFrame thành tập hợp các tuple để so sánh hiệu quả
                    new_entries_mask = ~current_scraped_data.apply(tuple, axis=1).isin(old_data.apply(tuple, axis=1))
                    new_entries = current_scraped_data[new_entries_mask]

                    if not new_entries.empty:
                        st.write("Có dữ liệu mới được tìm thấy (chưa có trong file cũ):")
                        st.write(new_entries)

                        # Nút để thêm dữ liệu mới vào file cũ
                        if st.button("Thêm dữ liệu mới vào file hiện có"):
                            with open(CSV_FILE_NAME, mode='a', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                # Ghi từng hàng dữ liệu mới vào file
                                for row in new_entries.values:
                                    writer.writerow(row)
                            st.success("Dữ liệu mới đã được thêm vào file thành công!")
                            st.experimental_rerun() # Chạy lại ứng dụng để cập nhật trạng thái
                    else:
                        st.write("Không có dữ liệu mới nào được tìm thấy.")
            except pd.errors.EmptyDataError:
                st.warning(f"File `{CSV_FILE_NAME}` trống. Đang tạo file mới với dữ liệu hiện tại.")
                current_scraped_data.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8')
                st.success(f"Dữ liệu mới đã được lưu vào file `{CSV_FILE_NAME}`.")
                st.write("Dữ liệu đã lưu:")
                st.write(current_scraped_data)
            except Exception as e:
                st.error(f"Lỗi khi đọc hoặc xử lý file `{CSV_FILE_NAME}`: {e}")
        else:
            st.write(f"Không tìm thấy file `{CSV_FILE_NAME}`. Đang tạo file mới với dữ liệu vừa thu thập...")
            current_scraped_data.to_csv(CSV_FILE_NAME, index=False, encoding='utf-8')
            st.success(f"Dữ liệu mới đã được lưu vào file `{CSV_FILE_NAME}`.")
            st.write("Dữ liệu đã lưu:")
            st.write(current_scraped_data)

# Thông báo ban đầu khi ứng dụng mới khởi động và chưa có nút nào được nhấn
if not scrape_new_data_button and not check_data_button:
    st.info("Vui lòng chọn một tùy chọn để bắt đầu.")
