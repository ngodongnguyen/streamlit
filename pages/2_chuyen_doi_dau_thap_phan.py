# Tệp này sẽ nằm trong thư mục 'pages/' với tên: 2_chuyen_doi_dau_thap_phan.py

import streamlit as st
from streamlit.components.v1 import html

def convert_and_divide(numbers_str, divisor=25000):
    """
    Chuyển đổi danh sách số: chia cho divisor, rồi thay dấu chấm thập phân thành dấu phẩy.

    Args:
        numbers_str (str): Một chuỗi chứa các số, mỗi số trên một dòng.
        divisor (float): Số để chia, mặc định 25000.

    Returns:
        str: Các số đã được chia và chuyển đổi, mỗi số trên một dòng.
    """
    lines = numbers_str.strip().split('\n')
    converted_numbers = []
    for line in lines:
        if line.strip():  # Đảm bảo không xử lý dòng trống
            try:
                num = float(line.strip().replace(',', ''))  # Xử lý nếu input có dấu phẩy
                result = num / divisor
                # Format với dấu chấm, rồi thay bằng phẩy
                result_str = f"{result:.10f}".rstrip('0').rstrip('.') if '.' in f"{result:.10f}" else f"{result}"
                converted_numbers.append(result_str.replace('.', ','))
            except ValueError:
                converted_numbers.append("Lỗi: Không phải số hợp lệ")
    return "\n".join(converted_numbers)

# Thay thế hàm copy_button() bằng phiên bản mới này
def copy_button():
    html("""
    <script>
    function copyToClipboard() {
        // Thử nhiều cách chọn textarea khác nhau
        var textarea = document.querySelector('textarea[key="output_area"]') || 
                      document.querySelector('textarea[aria-label*="Danh sách số với dấu phẩy"]') ||
                      document.querySelectorAll('textarea')[1];
        
        if (textarea) {
            textarea.select();
            document.execCommand('copy');
            setTimeout(function() {
                alert('Đã copy kết quả vào clipboard!');
            }, 100);
        } else {
            alert('Không tìm thấy ô kết quả! Vui lòng thử bôi đen và copy thủ công.');
        }
    }
    </script>
    <button onclick="copyToClipboard()" style="
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    ">📋 Copy kết quả</button>
    """)
st.title("Chuyển đổi tiền Việt: Chia cho 25.000 và đổi dấu thập phân sang phẩy")

st.write("Dán danh sách các số tiền Việt của bạn vào ô văn bản dưới đây. Mỗi số nên ở một dòng riêng biệt.")

# Ô nhập liệu cho người dùng dán danh sách số, không có ví dụ mặc định
input_numbers = st.text_area("Nhập danh sách số tiền:", height=200, value="", key="input_area")

if st.button("Chuyển đổi", type="primary"):
    if input_numbers:
        output_numbers = convert_and_divide(input_numbers)
        st.subheader("Kết quả đã chuyển đổi:")
        st.text_area("Danh sách số với dấu phẩy:", value=output_numbers, height=200, key="output_area")
        
        # Thêm nút copy
        copy_button()
    else:
        st.warning("Vui lòng nhập danh sách số để chuyển đổi.")

st.markdown("""
---
**Hướng dẫn sử dụng:**
1. Sao chép danh sách các số tiền của bạn (mỗi số một dòng)
2. Dán vào ô "Nhập danh sách số tiền:"
3. Nhấn nút "Chuyển đổi"
4. Kết quả sẽ hiển thị trong ô "Danh sách số với dấu phẩy:"
5. Nhấn nút "📋 Copy kết quả" để sao chép

**Lưu ý:**
- Nếu dùng trình duyệt Safari, có thể cần cho phép quyền copy
- Kết quả sẽ được chuyển đổi từ VND sang đơn vị khác bằng cách chia cho 25.000
- Dấu thập phân sẽ được chuyển từ chấm sang phẩy
- Các dòng trống sẽ được bỏ qua
""")