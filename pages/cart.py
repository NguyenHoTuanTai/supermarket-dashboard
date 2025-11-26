import streamlit as st
import pandas as pd

st.title("🛒 Giỏ hàng của bạn")

# Kiểm tra đăng nhập
if "username" not in st.session_state or st.session_state["username"] is None:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

if "role" not in st.session_state or st.session_state["role"] != "user":
    st.error("❌ Trang này chỉ dành cho USER.")
    st.stop()

username = st.session_state["username"]

# Ẩn sidebar cho user
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li:nth-child(1),
        [data-testid="stSidebarNav"] ul li:nth-child(2)
        {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Giỏ hàng
cart_items = st.session_state.get("cart_items", [])
for item in cart_items:
    if "Price" not in item:
        item["Price"] = 0

if not cart_items:
    st.warning("Giỏ hàng đang trống!")
    st.stop()

st.subheader("Danh sách sản phẩm")

# Tạo danh sách nút mua/xóa
to_buy = []
to_remove = []

for i, item in enumerate(cart_items):
    with st.container():
        st.write(f"**{item['Product Name']}**")
        st.write(f"Số lượng: {item['Quantity']}")
        st.write(f"Giá mỗi SP: ${item.get('Price', 0):,.2f}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🛒 Mua", key=f"buy_{i}"):
                to_buy.append(i)
        with col2:
            if st.button("🗑 Xóa", key=f"del_{i}"):
                to_remove.append(i)

# Xử lý mua/xóa sản phẩm dựa trên session_state
if to_buy:
    for i in sorted(to_buy, reverse=True):
        item = cart_items[i]
        st.session_state.setdefault("purchased", []).append(item)
        st.session_state["cart_count"] -= item.get("Quantity", 0)
        st.session_state["cart_items"].pop(i)
    st.experimental_rerun = True  # dummy flag để trigger reload

if to_remove:
    for i in sorted(to_remove, reverse=True):
        item = cart_items[i]
        st.session_state["cart_count"] -= item.get("Quantity", 0)
        st.session_state["cart_items"].pop(i)
    st.experimental_rerun = True  # dummy flag để trigger reload

# Tính tổng tiền
total_price = sum(item.get("Price", 0) * item.get("Quantity", 0) for item in st.session_state.get("cart_items", []))
st.markdown(f"**Tổng tiền giỏ hàng: ${total_price:,.2f}**")
