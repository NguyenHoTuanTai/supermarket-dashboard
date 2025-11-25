import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Giỏ hàng", layout="wide")

cart_file = r"D:/1.3/1.3/data/cart.csv"

# --- Kiểm tra đăng nhập ---
if "username" not in st.session_state or st.session_state["username"] is None:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

username = st.session_state["username"]

# --- Load giỏ hàng ---
if os.path.exists(cart_file):
    cart_df = pd.read_csv(cart_file)
else:
    cart_df = pd.DataFrame(columns=["Customer Name", "Product Name", "Product ID", "Category", "Sub-Category", "Quantity"])

user_cart = cart_df[cart_df["Customer Name"] == username]

# --- Cập nhật session_state ---
st.session_state["cart_items"] = user_cart.to_dict(orient="records")
st.session_state["cart_count"] = user_cart["Quantity"].sum() if not user_cart.empty else 0

st.title("🛒 Giỏ hàng của bạn")

if user_cart.empty:
    st.info("Giỏ hàng của bạn đang trống.")
    st.stop()

# --- Hiển thị từng sản phẩm ---
for i, row in user_cart.iterrows():
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.write(f"**{row['Product Name']}**")
    with col2:
        st.write(f"Số lượng: {row['Quantity']}")
    with col3:
        # Nút Mua ngay
        if st.button(f"Mua ngay {i}", key=f"buy_{i}"):
            # Xử lý mua hàng
            csv_file = "data/Global_Superstore2.csv"
            df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1")
            today = datetime.now()
            
            row_order = row.copy()
            row_order["Order ID"] = f"BUY-{today.strftime('%Y%m%d%H%M%S%f')}"
            row_order["Order Date"] = today
            row_order["Ship Date"] = today
            
            df_updated = pd.concat([df_existing, pd.DataFrame([row_order])], ignore_index=True)
            df_updated.to_csv(csv_file, index=False, encoding="ISO-8859-1")
            
            st.success(f"Đã mua {row['Product Name']}")
            
            # Xóa khỏi giỏ hàng
            cart_df.drop(i, inplace=True)
            cart_df.to_csv(cart_file, index=False)
            st.session_state["cart_count"] -= row["Quantity"]
            st.experimental_rerun()
    with col4:
        # Nút Xóa sản phẩm
        if st.button(f"Xóa {i}", key=f"delete_{i}"):
            cart_df.drop(i, inplace=True)
            cart_df.to_csv(cart_file, index=False)
            st.session_state["cart_count"] -= row["Quantity"]
            st.success(f"Đã xóa {row['Product Name']}")
            st.experimental_rerun()
