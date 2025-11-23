import streamlit as st
import pandas as pd

# ẩn khi chưa đăng nhập
if "role" not in st.session_state:
    st.markdown("""
        <style>
            header[data-testid="stHeader"] {
                display: none !important;
            }
            [data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Login", page_icon="🔐")


# Load dữ liệu khách hàng
df = pd.read_csv(
    "data/Global_Superstore2.csv", 
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)
accounts = pd.read_csv("data/customers_unique.csv", encoding="utf-8")



all_customers = df["Customer Name"].unique()




st.title("🔐 Đăng nhập hệ thống")

username = st.text_input("Tên đăng nhập")
password = st.text_input("Mật khẩu", type="password")

role = st.radio("Chọn vai trò", ["admin", "user"])

if st.button("Đăng nhập"):

    # Tìm tài khoản trong file
    user_row = accounts[
        (accounts["Customer Name"] == username) &
        (accounts["password"] == password) &
        (accounts["role"] == role)
    ]

    if user_row.empty:
        st.error("❌ Sai tài khoản hoặc mật khẩu!")
    else:
        st.session_state["Customer Name"] = username
        st.session_state["role"] = role

        st.success(f"Đăng nhập thành công với quyền {role}!")

        if role == "admin":
            st.session_state["username"] = username
            st.session_state["role"] = "admin"
            st.switch_page("pages/app.py")
        else:
            st.session_state["username"] = username
            st.session_state["role"] = "user"
            st.switch_page("pages/product_view.py")

