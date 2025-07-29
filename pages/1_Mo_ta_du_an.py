import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import html
import time

# --- Cấu hình API Key Groq ---
groq_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("api_keys", {}).get("GROQ_API_KEY")
if not groq_key:
    st.error("❌ Không tìm thấy GROQ_API_KEY trong secrets.")
    st.stop()

# --- Hàm gọi Groq API ---
def call_groq(prompt, model="llama3-70b-8192"):  # ✅ Model hiện hành mạnh nhất
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Bạn là một trợ lý AI chuyên trích xuất thông tin từ nội dung web."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            st.warning(f"⚠️ Groq trả lỗi {response.status_code}: {response.text[:200]}...")
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Lỗi gọi Groq API: {e}"

# --- Hàm hỗ trợ lấy nội dung trang web ---
def get_website_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html',
            'Connection': 'keep-alive'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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

        full_content = " ".join(content_parts)
        return full_content[:7000]
    except Exception as e:
        st.warning(f"⚠️ Lỗi khi truy cập {url}: {e}")
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
        results.append("Website\tNgách\tNăm thành lập\tĐịa chỉ trụ sở chính\tMô tả")

        with st.spinner("🔍 Đang phân tích..."):
            for url in urls:
                st.write(f"🔗 Đang xử lý: {url}")
                content = get_website_content(url)

                if content:
                    safe_content = html.unescape(content[:5000])
                    prompt = f"""
Bạn là một chuyên gia phân tích trang web để chọn lọc ngách phù hợp cho affiliate marketing.

Nhiệm vụ của bạn là: từ nội dung trang web dưới đây, hãy **trả về duy nhất 1 dòng gồm 5 cột**, cách nhau bằng dấu tab (`\\t`):

| Website | Ngách | Năm thành lập | Địa chỉ trụ sở chính | Mô tả sản phẩm chính |

Nếu không rõ thông tin, ghi "Không xác định".

---
URL: {url}
Nội dung:
{safe_content}
                    """
                    try:
                        response_text = call_groq(prompt)
                        result_line = response_text.strip().split('\n')[-1]
                        results.append(result_line)
                    except Exception as e:
                        st.warning(f"❌ Lỗi xử lý {url}: {e}")
                        results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")
                else:
                    results.append(f"{url}\tKhông xác định\tKhông xác định\tKhông xác định\tKhông xác định")

                time.sleep(1)

        st.success("✅ Hoàn tất.")
        final_output = "\n".join(results)
        st.text_area("📋 Kết quả phân tích", value=final_output, height=400)
