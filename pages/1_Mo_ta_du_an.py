import streamlit as st
import google.generativeai as genai

# --- Cấu hình API Key ---
# Đảm bảo bạn đã thêm GEMINI_API_KEY vào secrets của Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Lỗi cấu hình API Key: {e}. Vui lòng kiểm tra lại Streamlit Secrets.")
    st.stop()


# --- Giao diện ---
st.set_page_config(page_title="📄 Mô Tả Dự Án", layout="wide")
st.title("📄 Mô Tả Dự Án Từ URL")
st.caption("Nhập danh sách URL để AI trích xuất mô tả sản phẩm/dịch vụ chính.")

urls = st.text_area("📥 Nhập danh sách URL (mỗi dòng 1 link):", height=150)

if st.button("🚀 Phân tích"):
    if not urls.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất 1 URL.")
    else:
        with st.spinner("🔍 Đang phân tích..."):
            # Tạo prompt với hướng dẫn chi tiết
            prompt = f"""
Bạn là một chuyên gia trong lĩnh vực Affiliate Marketing.
Dựa vào kiến thức của bạn về các website sau đây, hãy thực hiện nhiệm vụ sau:

🎯 Nhiệm vụ:
- Với mỗi website trong danh sách, hãy mô tả **sản phẩm hoặc dịch vụ chính** mà nó cung cấp.
- Trả về **mỗi mô tả chỉ trong 1 câu ngắn, không quá 15 từ**.

⚠️ Yêu cầu bắt buộc:
- **Chỉ dựa vào kiến thức phổ biến, đáng tin cậy về các trang web này.**
- **Không suy đoán hoặc bịa đặt thông tin.**
- **Luôn bắt đầu mỗi mô tả bằng danh từ (ví dụ: "Nền tảng...", "Dịch vụ...", "Công cụ...").**
- **Trả về kết quả theo đúng thứ tự URL đã nhập.**
- **Không được bỏ sót bất kỳ website nào.**

📋 Định dạng đầu ra:
- Kết quả gồm 2 cột: `Tên miền` và `Mô tả`, ngăn cách bằng một dấu tab.

DANH SÁCH URL:
{urls.strip()}
"""

            try:
                # --- SỬA ĐỔI CHÍNH ---
                # 1. Chọn mô hình phù hợp cho văn bản (gemini-1.5-flash là lựa chọn tốt, nhanh và rẻ)
                model = genai.GenerativeModel("gemini-1.5-flash")

                # 2. Sử dụng phương thức `generate_content`
                response = model.generate_content(prompt)

                # Hiển thị kết quả
                st.success("✅ Đã hoàn tất.")
                st.text_area("📋 Kết quả mô tả", value=response.text, height=400)

            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi khi gọi API của Gemini: {e}")