import streamlit as st

st.title("📌 Mô Tả Dự Án")
st.caption("Nhập danh sách URL để trích xuất mô tả sản phẩm hoặc dịch vụ.")

urls = st.text_area("🌐 Nhập danh sách URL (mỗi dòng 1 URL):")

if st.button("🚀 Phân tích mô tả"):
    if not urls.strip():
        st.warning("⚠️ Vui lòng nhập ít nhất một URL.")
    else:
        st.info("⚙️ Tính năng đang chờ tích hợp API GPT/Grok để tự động phân tích.")
        st.markdown("📌 Bạn có thể tích hợp với OpenAI hoặc Grok API tại đây.")
