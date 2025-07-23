import streamlit as st
import openai

# --- Cấu hình API key ---
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Khuyến nghị dùng secrets

# --- Giao diện ---
st.set_page_config(page_title="📄 Mô Tả Dự Án", layout="wide")
st.title("📄 Mô Tả Dự Án Từ URL")
st.caption("Nhập danh sách URL để AI tự động trích xuất mô tả sản phẩm/dịch vụ chính.")

urls = st.text_area("📥 Nhập danh sách URL (mỗi dòng 1 link):")

if st.button("🚀 Phân tích"):
    if not urls.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất 1 URL.")
    else:
        with st.spinner("🔍 Đang phân tích..."):
            prompt = f"""
Bạn là một chuyên gia trong lĩnh vực Affiliate Marketing, có nhiệm vụ phân tích và trích xuất thông tin từ các website.

Tôi sẽ cung cấp cho bạn một danh sách URL của các dự án hoặc website.

🎯 Nhiệm vụ của bạn:
- Truy cập từng website.
- Tìm hiểu và trích xuất **sản phẩm hoặc dịch vụ chính** mà website đó cung cấp.
- Trả về **mỗi mô tả dưới dạng 1 câu ngắn, không quá 15 từ**.

⚠️ Yêu cầu bắt buộc:
- **Chỉ sử dụng thông tin chính thức từ trang chủ, trang sản phẩm/dịch vụ, hoặc mô tả dự án.**
- **Không được suy đoán, không bịa đặt, không dựa vào tên miền hay suy diễn.**
- **Không được bỏ sót bất kỳ website nào.**
- **Luôn bắt đầu mỗi mô tả bằng danh từ (không dùng động từ hoặc mô tả cảm tính).**
- **Trả về kết quả theo đúng thứ tự URL đã nhập.**

📋 Định dạng đầu ra:
- Kết quả trả về gồm **2 cột**: `Tên miền` và `Mô tả`, ngăn cách bằng **tab (tab-separated)** để tôi dễ copy vào Google Sheets hoặc Excel.
- Mỗi dòng đúng chuẩn như ví dụ sau:

arzopa.com Màn hình di động và phụ kiện công nghệ
boathouse.com Quần áo và thiết bị thể thao nước

Dưới đây là danh sách URL:
{urls.strip()}
"""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1500,
                )
                output = response.choices[0].message.content
                st.success("✅ Đã hoàn tất.")
                st.text_area("📋 Kết quả mô tả", value=output, height=400)
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
