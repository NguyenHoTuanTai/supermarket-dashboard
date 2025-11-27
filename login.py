import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",         
    initial_sidebar_state="expanded"  
)

# Ẩn UI khi chưa đăng nhập
if "role" not in st.session_state:
    st.markdown("""
        <style>
            
            header[data-testid="stHeader"] { display: none !important; }
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

# Tạo thư mục data nếu chưa có
os.makedirs("data", exist_ok=True)

# Load dữ liệu
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

# Nếu file accounts chưa có → tạo mới
if not os.path.exists("data/customers_unique.csv"):
    pd.DataFrame(columns=["Customer ID", "Customer Name", "password", "role"]).to_csv(
        "data/customers_unique.csv",
        index=False,
        encoding="utf-8"
    )

accounts = pd.read_csv("data/customers_unique.csv", encoding="utf-8")

st.title("🔐 Đăng nhập")

#đăng nhập / đăng ký
tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng ký tài khoản"])

#ĐĂNG NHẬP
with tab_login:
    username = st.text_input("Tên đăng nhập", key="login_username")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    role = st.radio("Chọn vai trò", ["admin", "user"], key="login_role")

    if st.button("Đăng nhập"):
        user_row = accounts[
            (accounts["Customer Name"] == username) &
            (accounts["password"] == password) &
            (accounts["role"] == role)
        ]

        if user_row.empty:
            st.error("Sai tài khoản hoặc mật khẩu!")
        else:
            st.session_state["Customer Name"] = username
            st.session_state["role"] = role
            st.session_state["logged_in"] = True 
            st.success(f"Đăng nhập thành công với quyền {role}!")

            if role == "admin":
                st.switch_page("pages/app.py")
            else:
                st.switch_page("pages/product_view.py")

#TAB ĐĂNG KÝ
with tab_register:
    st.subheader("Tạo tài khoản mới")

    reg_name = st.text_input("Tên đầy đủ", key="reg_name")
    reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
    reg_pass2 = st.text_input("Xác nhận mật khẩu", type="password", key="reg_pass2")
    reg_role = "user"

    if st.button("Tạo tài khoản", key="create_account"):
        if reg_name.strip() == "" or reg_pass == "" or reg_pass2 == "":
            st.warning("Vui lòng nhập đầy đủ tất cả thông tin!")
        elif reg_pass != reg_pass2:
            st.error("Mật khẩu xác nhận không trùng khớp!")
        else:
            #Tạo ID 
            parts = reg_name.split()
            initials = "".join([p[0].upper() for p in parts[:2]])
            random_num = random.randint(100, 9999)
            cust_id = f"{initials}-{random_num}"

            #Lưu vào file
            new_user = pd.DataFrame([{
                "Customer ID": cust_id,
                "Customer Name": reg_name,
                "password": reg_pass,
                "role": reg_role           
            }])

            with open("data/customers_unique.csv", "a", encoding="utf-8", newline="") as f:
                new_user.to_csv(f, header=False, index=False)

            st.success(f"Tạo tài khoản thành công! ID của bạn là **{cust_id}**")
            st.info("Bạn có thể quay lại tab Đăng nhập để đăng nhập.")

