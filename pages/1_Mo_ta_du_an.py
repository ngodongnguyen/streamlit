import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time # Thêm thư viện time để giới hạn tốc độ truy cập

# --- Cấu hình API Key ---
# Đảm bảo bạn đã thêm GEMINI_API_KEY vào secrets của Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Lỗi cấu hình API Key: {e}. Vui lòng kiểm tra lại Streamlit Secrets.")
    st.stop()

# --- Hàm hỗ trợ lấy nội dung trang web ---
def get_website_content(url):
    try:
        # Thêm nhiều headers để giả lập trình duyệt thật hơn
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1', # Do Not Track request header
        }
        # Tăng timeout để tránh lỗi khi trang web phản hồi chậm
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Gây ra lỗi HTTPError cho các phản hồi xấu (4xx hoặc 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy văn bản từ các thẻ phổ biến chứa nội dung chính
        # Thêm cả các thẻ meta description, title để tăng khả năng lấy tóm tắt
        content_parts = []
        if soup.title:
            content_parts.append(soup.title.get_text(strip=True))
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description and 'content' in meta_description.attrs:
            content_parts.append(meta_description['content'])

        paragraphs = soup.find_all('p')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        list_items = soup.find_all('li')

        for tag in paragraphs + headings + list_items:
            text = tag.get_text(separator=' ', strip=True)
            if text:
                content_parts.append(text)

        # Giới hạn nội dung để tránh gửi quá nhiều token đến mô hình
        full_content = " ".join(content_parts)
        return full_content[:8000] # Giới hạn 8000 ký tự đầu tiên để có nhiều thông tin hơn
    except requests.exceptions.RequestException as e:
        st.warning(f"Không thể truy cập hoặc tải nội dung từ {url}: {e}")
        return None
    except Exception as e:
        st.warning(f"Lỗi khi xử lý nội dung từ {url}: {e}")
        return None

# --- Giao diện ---
st.set_page_config(page_title="📄 Mô Tả Dự Án", layout="wide")
st.title("📄 Mô Tả Dự Án Từ URL")
st.caption("Nhập danh sách URL để AI trích xuất mô tả sản phẩm/dịch vụ chính và thông tin chi tiết.")

urls_input = st.text_area("📥 Nhập danh sách URL (mỗi dòng 1 link):", height=150)

if st.button("🚀 Phân tích"):
    if not urls_input.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất 1 URL.")
    else:
        urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
        results = []

        with st.spinner("🔍 Đang phân tích..."):
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Thêm tiêu đề cột vào kết quả đầu ra
            results.append("Website\tNgách\tNăm thành lập\tĐịa chỉ trụ sở chính\tMô tả")

            for url in urls:
                st.write(f"Đang xử lý: {url}...")
                content = get_website_content(url)
                domain = urlparse(url).netloc

                if content:
                    # Tạo prompt với nội dung trang web đã thu thập và hướng dẫn chi tiết
                    prompt = f"""
                    ## 🧠 Bối cảnh công việc
                    Bạn là một chuyên gia nghiên cứu thị trường và triển khai affiliate marketing thực chiến, chuyên chọn lọc các ngách có AOV cao, tỷ lệ chuyển đổi tốt và ROI cao. Hiện tại, bạn đang xây dựng một hệ thống theo dõi ngách tăng trưởng và chọn lọc sản phẩm affiliate tiềm năng.

                    ---

                    ## 🎯 Mục tiêu của bạn
                    Bạn được cung cấp nội dung từ một trang web. Nhiệm vụ của bạn là **tra cứu và trích xuất thông tin chi tiết về trang web đó theo các tiêu chí đã định**.

                    ---

                    ## 🚨 Tiêu chuẩn & Kỹ thuật tra cứu chung
                    * **KHÔNG ĐƯỢC suy diễn, KHÔNG DỰA VÀO “nghe giống như”, KHÔNG TỰ TẠO domain theo tên ngách.**
                    * **CHỈ sử dụng thông tin CÓ TRONG NỘI DUNG TRANG WEB được cung cấp** hoặc kiến thức phổ biến đáng tin cậy về trang web đó.
                    * **Nếu KHÔNG XÁC ĐỊNH được với bằng chứng cụ thể từ nội dung trang web → ghi rõ “Không xác định”.**
                    * **KHÔNG TỰ SUY LUẬN hoặc bịa thêm thông tin.**

                    ---

                    ## ✅ Yêu cầu Đầu ra
                    Kết quả trả về sẽ là một dòng dữ liệu duy nhất với **5 cột**, ngăn cách bằng **tab (`\t`)**.

                    | Cột dữ liệu | Mô tả yêu cầu |
                    | :---------- | :------------ |
                    | `Website` | URL đầy đủ của website được cung cấp – **giữ nguyên, không thay đổi.** |
                    | `Ngách` | Tên cụ thể của ngách/thị trường mà website/sản phẩm đó thuộc về. **Ưu tiên các ngách thương mại điện tử (E-commerce) nếu có liên quan.** Ví dụ: `E-commerce - Photo Printing`, `E-commerce - Home Security`, `Software - Photo Editing`, `E-commerce - Photography Accessories`, `E-commerce - Pet Supplies`, `E-commerce - Instant Cameras`, `E-commerce - Camera Filters`, `E-commerce - Dash Cams`, `E-commerce - Gaming Furniture`. Nếu không xác định được rõ ràng, ghi "Không xác định". |
                    | `Năm thành lập` | Năm thành lập doanh nghiệp. **Cố gắng tìm kiếm các từ khóa như "founded", "established", "since", "năm thành lập" trong nội dung.** Ưu tiên năm thành lập thực tế; nếu không rõ, lấy năm đăng ký domain (nếu biết, nhưng mô hình không tra cứu được domain). Nếu không xác định được từ nội dung, ghi "Không xác định". |
                    | `Địa chỉ trụ sở chính` | Chỉ ghi tên **Quốc gia** nơi đặt trụ sở pháp lý hiện tại của công ty. **Cố gắng tìm kiếm các từ khóa như "headquarters", "address", "location", "country" trong nội dung.** Nếu không xác định được rõ ràng từ nội dung, ghi "Không xác định". |
                    | `Mô tả` | Mô tả ngắn gọn về **sản phẩm hoặc dịch vụ chính** mà website đó cung cấp. **Mỗi mô tả dưới dạng 1 câu ngắn, không quá 15 từ, và luôn bắt đầu bằng một danh từ.** (Ví dụ: `Màn hình di động và phụ kiện công nghệ`, `Quần áo và thiết bị thể thao nước`). Nếu không thể mô tả từ nội dung, ghi "Không xác định". |

                    ---

                    Dưới đây là URL và NỘI DUNG TRANG WEB (đã trích xuất) để bạn phân tích:

                    URL ĐANG PHÂN TÍCH: {url}
                    NỘI DUNG TRANG WEB (đã trích xuất, giới hạn 8000 ký tự đầu tiên):
                    {content}
                    """
                    try:
                        response = model.generate_content(prompt)
                        # Đảm bảo chỉ lấy 1 dòng kết quả từ phản hồi của mô hình
                        result_line = response.text.strip().split('\n')[-1]
                        results.append(result_line)
                    except Exception as e:
                        st.warning(f"❌ Đã xảy ra lỗi khi gọi API của Gemini cho {url}: {e}")
                        results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")
                else:
                    results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")

                time.sleep(1) # Thêm khoảng dừng 1 giây giữa các yêu cầu để tránh bị chặn

        st.success("✅ Đã hoàn tất phân tích.")
        final_output = "\n".join(results)
        st.text_area("📋 Kết quả phân tích", value=final_output, height=400)
