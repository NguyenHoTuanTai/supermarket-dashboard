import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("🛒 Giỏ hàng của bạn")

# KIỂM TRA LOGIN
if "username" not in st.session_state or st.session_state["username"] is None:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

if "role" not in st.session_state or st.session_state["role"] != "user":
    st.error("❌ Trang này chỉ dành cho USER.")
    st.stop()

username = st.session_state["username"]

# Ẩn sidebar admin
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li:nth-child(1),
        [data-testid="stSidebarNav"] ul li:nth-child(2)
        {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

cart_file = "data/cart.csv"

needed_cols = ["Customer Name", "Product Name", "Product ID",
               "Category", "Sub-Category", "Quantity", "Price"]

if os.path.exists(cart_file):
    df_cart = pd.read_csv(cart_file)
    # Đảm bảo các cột cần thiết luôn có
    for col in needed_cols:
        if col not in df_cart.columns:
            df_cart[col] = ""
else:
    df_cart = pd.DataFrame(columns=needed_cols)
    df_cart.to_csv(cart_file, index=False)

# Lấy cart của user hiện tại
cart_items = df_cart[df_cart["Customer Name"] == username].to_dict(orient="records")

if not cart_items:
    st.warning("Giỏ hàng đang trống!")
    st.stop()

# HÀM CẬP NHẬT FILE CART.CSV
def save_cart_to_file(new_items):
    df_existing = pd.read_csv(cart_file) if os.path.exists(cart_file) else pd.DataFrame(columns=needed_cols)
    # Giữ lại sản phẩm của user khác
    df_remaining = df_existing[df_existing["Customer Name"] != username]
    # Thêm cart mới của user hiện tại
    df_new = pd.DataFrame(new_items, columns=needed_cols)
    df_final = pd.concat([df_remaining, df_new], ignore_index=True)
    df_final.to_csv(cart_file, index=False)

# HÀM MUA HÀNG
def process_purchase(product_name, quantity):
    csv_file = "data/Global_Superstore2.csv"
    df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1")
    product_rows = df_existing[df_existing["Product Name"] == product_name]
    today = datetime.now()

    existed_order = df_existing[
        (df_existing["Customer Name"] == username) &
        (df_existing["Product Name"] == product_name)
    ]

    if not existed_order.empty:
        df_existing.loc[existed_order.index[0], ["Order Date", "Ship Date"]] = [today, today]
        df_existing.to_csv(csv_file, index=False, encoding="ISO-8859-1")
        return existed_order.iloc[0].copy()

    row = product_rows.drop_duplicates(subset=["Product Name"]).iloc[0].copy()
    row["Customer Name"] = username
    row["Order ID"] = f"BUY-{today.strftime('%Y%m%d%H%M%S%f')}"
    row["Order Date"] = today
    row["Ship Date"] = today

    df_updated = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
    df_updated.to_csv(csv_file, index=False, encoding="ISO-8859-1")

    return row

# FLAG CHỐNG DOUBLE CLICK
if "processing_purchase" not in st.session_state:
    st.session_state["processing_purchase"] = False

clicked_buy = None
clicked_remove = None

# HIỂN THỊ GIỎ HÀNG
for i, item in enumerate(cart_items):
    with st.container():
        st.write(f"**{item['Product Name']}**")
        st.write(f"Số lượng: {item['Quantity']}")
        st.write(f"Giá mỗi SP: ${item.get('Price', 0):,.2f}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🛒 Mua", key=f"buy_{i}"):
                clicked_buy = i

        with col2:
            if st.button("🗑 Xóa", key=f"del_{i}"):
                clicked_remove = i

# XỬ LÝ MUA HÀNG
if clicked_buy is not None:

    if st.session_state["processing_purchase"]:
        st.stop()

    st.session_state["processing_purchase"] = True

    item = cart_items[clicked_buy]
    product_name = item["Product Name"]
    quantity = item["Quantity"]

    purchased_row = process_purchase(product_name, quantity)

    # LƯU VÀO SESSION STATE
    if "purchased" not in st.session_state:
        st.session_state["purchased"] = []
    st.session_state["purchased"].append(purchased_row.to_dict())

    # XÓA KHỎI CART
    new_cart = [item for idx, item in enumerate(cart_items) if idx != clicked_buy]
    save_cart_to_file(new_cart)

    st.session_state["processing_purchase"] = False
    st.switch_page("pages/my_orders.py")


# XỬ LÝ XÓA SẢN PHẨM
if clicked_remove is not None:
    new_cart = [item for idx, item in enumerate(cart_items) if idx != clicked_remove]
    save_cart_to_file(new_cart)
    st.rerun()

# TỔNG TIỀN
total_price = sum(item["Price"] * item["Quantity"] for item in cart_items)
st.markdown(f"**Tổng tiền giỏ hàng: ${total_price:,.2f}**")
