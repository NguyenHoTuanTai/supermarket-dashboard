import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="my_orders",
    layout="wide"
)
st.title("Đơn hàng của bạn")

# --- Kiểm tra login ---
if "role" not in st.session_state or st.session_state["role"] != "user":
    st.warning("Bạn phải đăng nhập bằng tài khoản user để xem trang này.")
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

# --- Đọc từ CSV ---
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

# --- Chỉ lọc theo username – KHÔNG GHÉP SESSION_STATE ---
customer_data_display = df[df["Customer Name"] == username]

if customer_data_display.empty:
    st.warning("Bạn chưa mua sản phẩm nào.")
else:
    # Bỏ các cột không cần
    cols_to_drop = ["Quantity", "Discount", "Profit", "Shipping Cost", "Order Priority", "Postal Code"]
    customer_data_display = customer_data_display.drop(
        columns=[c for c in cols_to_drop if c in customer_data_display.columns],
        errors="ignore"
    )

    st.dataframe(customer_data_display, height=600)
