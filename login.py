import streamlit as st
import pandas as pd
import random
import os
import random
from email.mime.text import MIMEText
import smtplib
from email.mime.text import MIMEText

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



accounts = pd.read_csv("data/customers_unique.csv", encoding="utf-8")

st.title("🔐 Đăng nhập")

EMAIL_SENDER = "anhtaimonkey222@gmail.com"         
APP_PASSWORD = "eqdg pygz vmcb pipt" 
def send_otp(to_email, user_name=None):
  
    otp = str(random.randint(100000, 999999))
    msg = MIMEText(f"Mã OTP là: {otp}")
    msg["Subject"] = "Mã OTP"
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_SENDER, APP_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return otp
    except smtplib.SMTPAuthenticationError:
        st.error("Đăng nhập Gmail thất bại. Kiểm tra Email/ App Password!")
        return None
    except Exception as e:
        st.error(f"Lỗi khi gửi email: {e}")
        return None


tab_login, tab_register, tab_forgot = st.tabs(["Đăng nhập", "Đăng ký tài khoản", "Quên mật khẩu"])

#đăng nhập
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
            st.session_state["Customer ID"] = user_row.iloc[0]["Customer ID"]
            st.session_state["logged_in"] = True 
            st.success(f"Đăng nhập thành công với quyền {role}!")

            if role == "admin":
                st.switch_page("pages/app.py")
            else:
                st.switch_page("pages/product_view.py")

#TAB đăng ký
with tab_register:
    st.subheader("Tạo tài khoản mới")
    reg_name = st.text_input("Tên đầy đủ", key="reg_name")
    reg_email = st.text_input("Gmail", key="reg_email")
    reg_pass = st.text_input("Mật khẩu", type="password", key="reg_pass")
    reg_pass2 = st.text_input("Xác nhận mật khẩu", type="password", key="reg_pass2")
    reg_role = "user"

    # Session state
    if "reg_otp_code" not in st.session_state:
        st.session_state.reg_otp_code = None
    if "reg_email_temp" not in st.session_state:
        st.session_state.reg_email_temp = None

    # Bước 1: Gửi OTP
    if st.button("Gửi mã OTP", key="send_otp_register"):
        if reg_name.strip() == "" or reg_email.strip() == "" or reg_pass == "" or reg_pass2 == "":
            st.warning("Vui lòng nhập đầy đủ thông tin!")
        elif reg_pass != reg_pass2:
            st.error("Mật khẩu xác nhận không trùng khớp!")
        else:
            otp = send_otp(reg_email)
            if otp:
                st.session_state.reg_otp_code = otp
                st.session_state.reg_email_temp = reg_email.strip()
                st.success(f"Mã OTP đã được gửi đến Gmail {reg_email.strip()}")

    # Bước 2: Nhập OTP và tạo tài khoản
    if st.session_state.reg_otp_code:
        otp_input = st.text_input("Nhập OTP vừa nhận", key="reg_otp_input")
        if st.button("Xác nhận OTP và tạo tài khoản"):
            if otp_input == st.session_state.reg_otp_code:
                parts = reg_name.split()
                initials = "".join([p[0].upper() for p in parts[:2]])
                random_num = random.randint(100, 9999)
                cust_id = f"{initials}-{random_num}"

                new_user = pd.DataFrame([{
                    "Customer ID": cust_id,
                    "Customer Name": reg_name,
                    "password": reg_pass,
                    "role": reg_role,
                    "Email": st.session_state.reg_email_temp
                }])

                with open("data/customers_unique.csv", "a", encoding="utf-8", newline="") as f:
                    new_user.to_csv(f, header=False, index=False)

                st.success(f"Tạo tài khoản thành công! ID của bạn là **{cust_id}**")
                st.info("Bạn có thể quay lại tab Đăng nhập để đăng nhập.")

                st.session_state.reg_otp_code = None
                st.session_state.reg_email_temp = None
            else:
                st.error("OTP không đúng!")
# TAB quên mật khẩu
with tab_forgot:
    st.header("Quên mật khẩu")

    # Nhập thông tin xác thực
    forgot_name = st.text_input("Tên đầy đủ", key="forgot_name")
    forgot_email = st.text_input("Email đăng ký", key="forgot_email")

    
    #gửi otp
    if st.button("Gửi OTP", key="forgot_send_otp_btn"):
        if forgot_name.strip() == "" or forgot_email.strip() == "":
            st.warning("Vui lòng nhập đầy đủ Tên và Email!")
        else:
            #Kiểm tra thông tin 
            check = accounts[
                (accounts["Customer Name"].str.lower() == forgot_name.strip().lower()) &
                (accounts["Email"].str.lower() == forgot_email.strip().lower())
            ]

            if check.empty:
                st.error("Tên hoặc Email không trùng khớp với bất kỳ tài khoản nào!")
            else:
                otp = send_otp(forgot_email, forgot_name)  # Gửi OTP

                st.session_state["reset_customer_name"] = forgot_name
                st.session_state["reset_email"] = forgot_email
                st.session_state["reset_otp"] = otp

                st.success("Mã OTP đã được gửi về email của bạn!")

    #nhập OTP & đổi mk
    if "reset_otp" in st.session_state:
        input_otp = st.text_input("Nhập OTP", key="forgot_input_otp")
        new_pass = st.text_input("Mật khẩu mới", type="password", key="forgot_new_pass")
        new_pass2 = st.text_input("Xác nhận mật khẩu mới", type="password", key="forgot_new_pass2")

        if st.button("Đặt lại mật khẩu", key="forgot_reset_pass_btn"):
            if input_otp != str(st.session_state["reset_otp"]):
                st.error("OTP không đúng!")
            elif new_pass == "" or new_pass2 == "":
                st.warning("Vui lòng nhập đầy đủ mật khẩu!")
            elif new_pass != new_pass2:
                st.error("Mật khẩu xác nhận không trùng khớp!")
            else:
                #Cập nhật mật khẩu
                accounts.loc[
                    (accounts["Customer Name"].str.lower() == st.session_state["reset_customer_name"].lower()) &
                    (accounts["Email"].str.lower() == st.session_state["reset_email"].lower()),
                    "password"
                ] = new_pass

                accounts.to_csv("data/customers_unique.csv", index=False, encoding="utf-8")

                st.success("Đổi mật khẩu thành công!")

                
                for key in ["reset_customer_name", "reset_email", "reset_otp"]:
                    st.session_state.pop(key, None)





