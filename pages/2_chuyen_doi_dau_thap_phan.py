# Tệp này sẽ nằm trong thư mục 'pages/' với tên: 2_chuyen_doi_dau_thap_phan.py

import streamlit as st

def convert_decimal_point_to_comma(number_list_str):
    """
    Chuyển đổi dấu chấm thập phân thành dấu phẩy trong một danh sách các chuỗi số.

    Args:
        number_list_str (str): Một chuỗi chứa các số, mỗi số trên một dòng.

    Returns:
        str: Các số đã được chuyển đổi, mỗi số trên một dòng, với dấu phẩy là dấu thập phân.
    """
    lines = number_list_str.strip().split('\n')
    converted_numbers = []
    for line in lines:
        if line.strip():  # Đảm bảo không xử lý dòng trống
            converted_numbers.append(line.strip().replace('.', ','))
    return "\n".join(converted_numbers)

st.title("Chuyển đổi dấu thập phân từ chấm sang phẩy")

st.write("Dán danh sách các số của bạn vào ô văn bản dưới đây. Mỗi số nên ở một dòng riêng biệt.")

# Dữ liệu ví dụ từ hình ảnh bạn cung cấp
default_numbers_example = """0.03416
0.28972
0.41048
0.2622
0.11648
0.30376
0.32168
0.669908
0.03648
0.10456
0.23616
0.20908
0.2342
0.38208
0.19288"""

# Ô nhập liệu cho người dùng dán danh sách số
input_numbers = st.text_area("Nhập danh sách số:", height=200, value=default_numbers_example)

if st.button("Chuyển đổi"):
    if input_numbers:
        output_numbers = convert_decimal_point_to_comma(input_numbers)
        st.subheader("Kết quả đã chuyển đổi:")
        st.text_area("Danh sách số với dấu phẩy:", value=output_numbers, height=200)
    else:
        st.warning("Vui lòng nhập danh sách số để chuyển đổi.")

st.markdown("""
---
**Hướng dẫn sử dụng:**
1. Sao chép danh sách các số của bạn (mỗi số một dòng).
2. Dán vào ô "Nhập danh sách số:".
3. Nhấn nút "Chuyển đổi".
4. Kết quả sẽ hiển thị trong ô "Danh sách số với dấu phẩy:".
""")