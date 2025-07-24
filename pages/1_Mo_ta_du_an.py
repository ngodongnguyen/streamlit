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
st.caption("Nhập danh sách URL để AI trích xuất mô tả sản phẩm/dịch vụ chính và thông tin chi tiết.")

urls = st.text_area("📥 Nhập danh sách URL (mỗi dòng 1 link):", height=150)

if st.button("🚀 Phân tích"):
    if not urls.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất 1 URL.")
    else:
        with st.spinner("🔍 Đang phân tích..."):
            # Tạo prompt với hướng dẫn chi tiết (đã được cập nhật)
            prompt = f"""
## 🧠 Bối cảnh công việc
Tôi là một chuyên gia nghiên cứu thị trường và triển khai affiliate marketing thực chiến, chuyên chọn lọc các ngách có AOV cao, tỷ lệ chuyển đổi tốt và ROI cao. Hiện tại, tôi đang xây dựng một hệ thống theo dõi ngách tăng trưởng và chọn lọc sản phẩm affiliate tiềm năng.

---

## 🎯 Mục tiêu của bạn
Tôi sẽ cung cấp cho bạn một danh sách các URL website. Nhiệm vụ của bạn là **tra cứu và trích xuất thông tin chi tiết cho từng URL theo các tiêu chí đã định**.

---

## 🚨 Tiêu chuẩn & Kỹ thuật tra cứu chung
* **Không được suy diễn, không dựa vào “nghe giống như”, không tự tạo domain theo tên ngách.**
* **Phải tra cứu rõ ràng từng URL** bằng cách sử dụng: Google Search, ProductHunt, AppSumo, G2, LinkedIn, Crunchbase, WHOIS domain, và website chính thức của công ty.
* **Nếu là tên sản phẩm/dịch vụ:** Xác minh "Đây là gì?", "Làm gì?", "Phục vụ ai?", "Trang chính thức là gì?".
* **Nếu không xác định được với bằng chứng cụ thể → ghi rõ “Không xác định”.**
* **Tất cả kết quả cần được double-check thủ công hoặc qua công cụ phụ trợ đáng tin cậy.**
* **Không được bỏ sót bất kỳ website nào.**
* **Không tự suy luận hoặc bịa thêm thông tin.**

---

## ✅ Yêu cầu Đầu ra
Kết quả trả về sẽ là một bảng với **5 cột dữ liệu**, ngăn cách bằng **tab (`\t`)** để dễ dàng copy vào Google Sheets hoặc Excel. Mỗi dòng sẽ tương ứng với một URL bạn cung cấp.

| Cột dữ liệu | Mô tả yêu cầu |
| :---------- | :------------ |
| `Website` | URL đầy đủ của website đã cung cấp – **giữ nguyên, không thay đổi.** |
| `Ngách` | Tên cụ thể của ngách/thị trường mà website/sản phẩm đó thuộc về. **(Ví dụ: `E-commerce - Electronics`, `SaaS - Software Deals`, `AI - 3D Visualization`...).** Nếu không xác định được rõ ràng, ghi "Không xác định". |
| `Năm thành lập` | Năm thành lập doanh nghiệp. Ưu tiên năm thành lập thực tế; nếu không rõ, lấy năm đăng ký domain. Nếu không xác định được, ghi "Không xác định". |
| `Địa chỉ trụ sở chính` | Chỉ ghi tên **Quốc gia** nơi đặt trụ sở pháp lý hiện tại của công ty (legal entity location). Nếu không xác định được rõ ràng, ghi "Không xác định". Nếu công ty hoạt động remote hoặc founder ở nơi khác, **không thay đổi cột này, chỉ ghi quốc gia trụ sở pháp lý.** |
| `Mô tả` | Mô tả ngắn gọn về **sản phẩm hoặc dịch vụ chính** mà website đó cung cấp. **Mỗi mô tả dưới dạng 1 câu ngắn, không quá 15 từ, và luôn bắt đầu bằng một danh từ.** (Ví dụ: `Màn hình di động và phụ kiện công nghệ`, `Quần áo và thiết bị thể thao nước`). Nếu không thể mô tả, ghi "Không xác định". |

---

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
