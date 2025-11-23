import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="my_orders",
    layout="wide"   
)
st.title("📋 Đơn hàng của bạn")

# --- Kiểm tra login ---
if "role" not in st.session_state or st.session_state["role"] != "user":
    st.warning("❌ Bạn phải đăng nhập bằng tài khoản user để xem trang này.")
    st.stop()

# Check login
if "role" not in st.session_state:
    st.switch_page("product_view.py")

# --- Kiểm tra login ---
if "role" not in st.session_state:
    st.switch_page("login.py")

if st.session_state["role"] == "user":
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] ul li:nth-child(1),
            [data-testid="stSidebarNav"] ul li:nth-child(2)
            {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

username = st.session_state["username"]

# --- Lấy đơn hàng từ CSV ---
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

customer_data = df[df["Customer Name"] == username]

# --- Nếu có đơn hàng vừa mua từ session_state, ghép vào ---
if "purchased" in st.session_state and st.session_state["purchased"]:
    purchased_df = pd.DataFrame(st.session_state["purchased"])
    if not customer_data.empty:
        customer_data_display = pd.concat([customer_data, purchased_df], ignore_index=True)
    else:
        customer_data_display = purchased_df
else:
    customer_data_display = customer_data

if customer_data_display.empty:
    st.warning("⚠️ Bạn chưa mua sản phẩm nào.")
else:
    cols_to_drop = ["Quantity", "Discount", "Profit", "Shipping Cost", "Order Priority", "Postal Code"]
    customer_data_display = customer_data_display.drop(columns=[c for c in cols_to_drop if c in customer_data_display.columns], errors="ignore")
    st.dataframe(customer_data_display, height=600)
