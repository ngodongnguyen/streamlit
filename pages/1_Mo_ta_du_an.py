import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup # bs4 là module của beautifulsoup4
from urllib.parse import urlparse

# --- Cấu hình API Key ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Lỗi cấu hình API Key: {e}. Vui lòng kiểm tra lại Streamlit Secrets.")
    st.stop()

# --- Hàm hỗ trợ lấy nội dung trang web ---
def get_website_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Lấy văn bản từ các thẻ phổ biến chứa nội dung chính
        paragraphs = soup.find_all('p')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        list_items = soup.find_all('li')

        content_parts = []
        for tag in paragraphs + headings + list_items:
            text = tag.get_text(separator=' ', strip=True)
            if text:
                content_parts.append(text)

        # Giới hạn nội dung để tránh gửi quá nhiều token đến mô hình
        full_content = " ".join(content_parts)
        return full_content[:5000] # Giới hạn 5000 ký tự đầu tiên
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

            for url in urls:
                st.write(f"Đang xử lý: {url}...")
                content = get_website_content(url)
                domain = urlparse(url).netloc

                if content:
                    # Tạo prompt với nội dung trang web đã thu thập
                    prompt = f"""
                    ## 🧠 Bối cảnh công việc
                    Tôi là một chuyên gia nghiên cứu thị trường và triển khai affiliate marketing thực chiến, chuyên chọn lọc các ngách có AOV cao, tỷ lệ chuyển đổi tốt và ROI cao. Hiện tại, tôi đang xây dựng một hệ thống theo dõi ngách tăng trưởng và chọn lọc sản phẩm affiliate tiềm năng.

                    ---

                    ## 🎯 Mục tiêu của bạn
                    Bạn được cung cấp nội dung từ một trang web. Nhiệm vụ của bạn là **tra cứu và trích xuất thông tin chi tiết về trang web đó theo các tiêu chí đã định**.

                    ---

                    ## 🚨 Tiêu chuẩn & Kỹ thuật tra cứu chung
                    * **Không được suy diễn, không dựa vào “nghe giống như”, không tự tạo domain theo tên ngách.**
                    * **Chỉ sử dụng thông tin có trong nội dung trang web được cung cấp hoặc kiến thức phổ biến đáng tin cậy về trang web đó.**
                    * **Nếu không xác định được với bằng chứng cụ thể → ghi rõ “Không xác định”.**
                    * **Không tự suy luận hoặc bịa thêm thông tin.**

                    ---

                    ## ✅ Yêu cầu Đầu ra
                    Kết quả trả về sẽ là một dòng dữ liệu với **5 cột**, ngăn cách bằng **tab (`\t`)**.

                    | Cột dữ liệu | Mô tả yêu cầu |
                    | :---------- | :------------ |
                    | `Website` | URL đầy đủ của website đã cung cấp – **giữ nguyên, không thay đổi.** |
                    | `Ngách` | Tên cụ thể của ngách/thị trường mà website/sản phẩm đó thuộc về. **(Ví dụ: `E-commerce - Electronics`, `SaaS - Software Deals`, `AI - 3D Visualization`...).** Nếu không xác định được rõ ràng, ghi "Không xác định". |
                    | `Năm thành lập` | Năm thành lập doanh nghiệp. Ưu tiên năm thành lập thực tế; nếu không rõ, lấy năm đăng ký domain. Nếu không xác định được, ghi "Không xác định". |
                    | `Địa chỉ trụ sở chính` | Chỉ ghi tên **Quốc gia** nơi đặt trụ sở pháp lý hiện tại của công ty (legal entity location). Nếu không xác định được rõ ràng, ghi "Không xác định". Nếu công ty hoạt động remote hoặc founder ở nơi khác, **không thay đổi cột này, chỉ ghi quốc gia trụ sở pháp lý.** |
                    | `Mô tả` | Mô tả ngắn gọn về **sản phẩm hoặc dịch vụ chính** mà website đó cung cấp. **Mỗi mô tả dưới dạng 1 câu ngắn, không quá 15 từ, và luôn bắt đầu bằng một danh từ.** (Ví dụ: `Màn hình di động và phụ kiện công nghệ`, `Quần áo và thiết bị thể thao nước`). Nếu không thể mô tả, ghi "Không xác định". |

                    ---

                    URL ĐANG PHÂN TÍCH: {url}
                    NỘI DUNG TRANG WEB (đã trích xuất):
                    {content}
                    """
                    try:
                        response = model.generate_content(prompt)
                        results.append(response.text.strip())
                    except Exception as e:
                        st.warning(f"❌ Đã xảy ra lỗi khi gọi API của Gemini cho {url}: {e}")
                        results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")
                else:
                    results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")

        st.success("✅ Đã hoàn tất phân tích.")
        # Thêm tiêu đề cột vào kết quả cuối cùng
        header = "Website\tNgách\tNăm thành lập\tĐịa chỉ trụ sở chính\tMô tả"
        final_output = header + "\n" + "\n".join(results)
        st.text_area("📋 Kết quả phân tích", value=final_output, height=400)
