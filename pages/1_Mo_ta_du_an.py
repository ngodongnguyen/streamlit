import streamlit as st
import requests
import html
import time

# --- Cấu hình API Key Groq ---
groq_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("api_keys", {}).get("GROQ_API_KEY")
if not groq_key:
    st.error("❌ Không tìm thấy GROQ_API_KEY trong secrets.")
    st.stop()

# --- Hàm gọi Groq API ---
def call_groq(prompt, model="llama3-70b-8192"):
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

# --- Hàm lấy toàn bộ HTML thô ---
def get_website_html(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text[:15000]  # Giới hạn để tránh token overflow
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
                content = get_website_html(url)

                if content:
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
Kết quả trả về sẽ là một dòng dữ liệu duy nhất với **5 cột**, ngăn cách bằng **tab (`\\t`)**.

| Cột dữ liệu | Mô tả yêu cầu |
| :---------- | :------------ |
| `Website` | URL đầy đủ của website được cung cấp – **giữ nguyên, không thay đổi.** |
| `Ngách` | Tên cụ thể của ngách/thị trường mà website/sản phẩm đó thuộc về. Ưu tiên các ngách thương mại điện tử (E-commerce) nếu có liên quan. Nếu không xác định được rõ ràng, ghi "Không xác định". |
| `Năm thành lập` | Cố gắng tìm kiếm các từ khóa như "founded", "established", "since", "năm thành lập". Nếu không xác định được từ nội dung, ghi "Không xác định". |
| `Địa chỉ trụ sở chính` | Chỉ ghi tên **Quốc gia** nơi đặt trụ sở pháp lý hiện tại. Nếu không xác định được rõ ràng từ nội dung, ghi "Không xác định". |
| `Mô tả` | Mô tả ngắn gọn về **sản phẩm hoặc dịch vụ chính**, dưới 15 từ, bắt đầu bằng một danh từ. Nếu không thể mô tả từ nội dung, ghi "Không xác định". |

---

Dưới đây là URL và NỘI DUNG TRANG WEB (HTML gốc):

URL ĐANG PHÂN TÍCH: {url}

NỘI DUNG HTML TRANG WEB:
{html.unescape(content)}
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
