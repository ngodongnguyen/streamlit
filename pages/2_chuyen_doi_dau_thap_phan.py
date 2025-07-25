# Tệp này sẽ nằm trong thư mục 'pages/' với tên: 2_chuyen_doi_dau_thap_phan.py

import streamlit as st

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

st.title("Chuyển đổi tiền Việt: Chia cho 25.000 và đổi dấu thập phân sang phẩy")

st.write("Dán danh sách các số tiền Việt của bạn vào ô văn bản dưới đây. Mỗi số nên ở một dòng riêng biệt.")

# Ô nhập liệu cho người dùng dán danh sách số, không có ví dụ mặc định
input_numbers = st.text_area("Nhập danh sách số tiền:", height=200, value="", key="input_area")

if st.button("Chuyển đổi"):
    if input_numbers:
        output_numbers = convert_and_divide(input_numbers)
        st.subheader("Kết quả đã chuyển đổi:")
        st.text_area("Danh sách số với dấu phẩy:", value=output_numbers, height=200, key="output_area")
        
        # Nút copy sử dụng HTML và JavaScript, với selector dựa trên key (Streamlit thêm class hoặc id dựa trên key, nhưng dùng querySelector cho label hoặc gần đó)
        # Để chắc chắn, dùng index, nhưng cải thiện bằng cách chọn textarea cuối cùng
        st.markdown("""
        <button onclick="copyToClipboard()">Copy kết quả</button>
        <script>
        function copyToClipboard() {
            var textareas = document.querySelectorAll('textarea');
            var textarea = textareas[textareas.length - 1];  // Chọn textarea cuối cùng (kết quả)
            textarea.select();
            document.execCommand('copy');
            alert('Đã copy vào clipboard!');
        }
        </script>
        """, unsafe_allow_html=True)
    else:
        st.warning("Vui lòng nhập danh sách số để chuyển đổi.")

st.markdown("""
---
**Hướng dẫn sử dụng:**
1. Sao chép danh sách các số tiền của bạn (mỗi số một dòng).
2. Dán vào ô "Nhập danh sách số tiền:".
3. Nhấn nút "Chuyển đổi".
4. Kết quả sẽ hiển thị trong ô "Danh sách số với dấu phẩy:", và bạn có thể nhấn nút "Copy kết quả" để sao chép.
\n\n**Lưu ý:** Nếu nút copy không hoạt động, hãy thử reload trang hoặc đảm bảo trình duyệt cho phép copy clipboard. Nếu vẫn lỗi, có thể do thứ tự elements, thử dùng [1] thay vì [length-1] trong script nếu có nhiều textarea.
""")