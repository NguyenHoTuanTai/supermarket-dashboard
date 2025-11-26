import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="Product View",
    layout="wide"   
)

cart_file = r"D:/1.3/1.3/data/cart.csv"

# Tạo file cart nếu chưa có hoặc nếu rỗng
if not os.path.exists(cart_file) or os.path.getsize(cart_file) == 0:
    pd.DataFrame(columns=[
        "Customer Name", "Product Name", "Product ID",
        "Category", "Sub-Category", "Quantity", "Price"
    ]).to_csv(cart_file, index=False)

if "username" not in st.session_state or st.session_state["username"] is None:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

if "role" not in st.session_state or st.session_state["role"] is None:
    st.warning("Bạn chưa đăng nhập.")
    st.stop()

username = st.session_state["username"]
role = st.session_state["role"]

if role != "user":
    st.error("❌ Trang này chỉ dành cho USER.")
    st.stop()

# Load giỏ hàng lên session_state khi mở trang
cart_df = pd.read_csv(cart_file)

# Lọc giỏ hàng của user hiện tại
user_cart = cart_df[cart_df["Customer Name"] == username]

# Lưu vào session_state
st.session_state["cart_items"] = user_cart.to_dict(orient="records")
st.session_state["cart_count"] = user_cart["Quantity"].sum() if not user_cart.empty else 0

# Ẩn sidebar cho user
if role == "user":
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] ul li:nth-child(1),
            [data-testid="stSidebarNav"] ul li:nth-child(2)
            {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Khởi tạo giỏ hàng & purchased nếu chưa có
if "cart_count" not in st.session_state:
    st.session_state["cart_count"] = 0

if "cart_items" not in st.session_state:
    # Lấy từ CSV nếu username đã có
    username = st.session_state.get("username", None)
    if username is not None:
        cart_file = r"D:/1.3/1.3/data/cart.csv"
        if os.path.exists(cart_file) and os.path.getsize(cart_file) > 0:
            cart_df = pd.read_csv(cart_file)
            user_cart = cart_df[cart_df["Customer Name"] == username]
            st.session_state["cart_items"] = user_cart.to_dict(orient="records")
        else:
            st.session_state["cart_items"] = []
    else:
        st.session_state["cart_items"] = []

if "purchased" not in st.session_state:
    st.session_state["purchased"] = []

st.markdown("""
<style>
.fixed-top-right {
    position: fixed;
    top: 15px;
    right: 20px;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 10px;
}
.cart-box {
    font-size: 18px;
    background-color: white;
    padding: 5px 10px;
    border-radius: 5px;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    white-space: nowrap;
}
.logout-btn {
    background-color: #ff4b4b;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 5px;
    cursor: pointer;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    font-size: 15px;
}
.logout-btn:hover {
    background-color: #ff1f1f;
}
</style>
<div class="fixed-top-right">
    <div class="cart-box">
        🛒 <span style="color:red; font-weight:bold;">{st.session_state['cart_count']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([7, 1, 2])
with col2:
    if st.button(f"🛒 {st.session_state['cart_count']}"):
        st.switch_page("pages/cart.py")
with col3:
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.clear()
        st.switch_page("login.py")

st.title("Dashboard Supermarket")

df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

#Top 20 sản phẩm bán chạy 
st.subheader("Top 20 sản phẩm bán chạy nhất")

top_products = (
    df.groupby("Product Name")
    .agg({
        "Sales": "sum",
        "Category": "first",
        "Sub-Category": "first",
        "Product ID": "first"
    })
    .sort_values("Sales", ascending=False)
    .head(20)
    .reset_index()
)

fig = px.bar(
    top_products,
    x="Sales",
    y="Product Name",
    orientation="h",
    text="Sales",
    labels={"Sales": "Tổng Sales", "Product Name": "Tên sản phẩm"},
)
fig.update_layout(yaxis=dict(autorange="reversed"), height=600)
st.plotly_chart(fig, use_container_width=True)

# Search + Chi tiết sản phẩm
st.subheader("Khám phá sản phẩm")

search_query = st.text_input("Tìm sản phẩm bất kỳ", "")

# lọc Category
categories = ["Tất cả"] + sorted(df["Category"].unique())
selected_category = st.selectbox("Lọc theo Category", categories)

# lọc Sub-Category phụ thuộc Category
if selected_category != "Tất cả":
    subcats = df[df["Category"] == selected_category]["Sub-Category"].unique()
else:
    subcats = df["Sub-Category"].unique()

subcats = ["Tất cả"] + sorted(subcats)
selected_subcat = st.selectbox("Lọc theo Sub-Category", subcats)

# Tạo bảng sản phẩm
all_products = df.groupby("Product Name").agg({
    "Sales": "sum",
    "Category": "first",
    "Sub-Category": "first",
    "Product ID": "first"
}).reset_index()

# Áp dụng lọc Category
if selected_category != "Tất cả":
    all_products = all_products[all_products["Category"] == selected_category]

# Áp dụng lọc Sub-Category
if selected_subcat != "Tất cả":
    all_products = all_products[all_products["Sub-Category"] == selected_subcat]

# Áp dụng lọc theo từ khóa
if search_query:
    all_products = all_products[all_products["Product Name"].str.contains(search_query, case=False, na=False)]
    
products_display = all_products.copy()

if not products_display.empty:
    st.dataframe(products_display, height=600)

    product_names = products_display["Product Name"].tolist()
    selected_product = st.selectbox("Chọn sản phẩm để xem chi tiết", product_names)

    product_info = products_display[products_display["Product Name"] == selected_product].iloc[0]
    st.info(
        f"**Tên sản phẩm:** {product_info['Product Name']}\n\n"
        f"**Product ID:** {product_info['Product ID']}\n\n"
        f"**Category:** {product_info['Category']}\n\n"
        f"**Sub-Category:** {product_info['Sub-Category']}\n\n"
        f"**Tổng Sales:** ${product_info['Sales']:,.2f}"
    )

    # thêm vào giỏ + Mua ngay
    def add_to_cart():
        cart_df = pd.read_csv(cart_file)
        user_cart = cart_df[cart_df["Customer Name"] == username]
        existed = user_cart[user_cart["Product Name"] == selected_product]

        # Lấy dòng sản phẩm đầu tiên để tính giá
        product_rows = df[df["Product Name"] == selected_product]

        if not product_rows.empty:
            row = product_rows.iloc[0]
            try:
                unit_price = float(row["Sales"]) / float(row["Quantity"])
            except (ZeroDivisionError, KeyError, ValueError):
                unit_price = 0
        else:
            unit_price = 0

        unit_price = round(unit_price, 2)

        if not existed.empty:
            idx = existed.index[0]
            cart_df.loc[idx, "Quantity"] += 1
        else:
            new_item = {
                "Customer Name": username,
                "Product Name": product_info["Product Name"],
                "Product ID": product_info["Product ID"],
                "Category": product_info["Category"],
                "Sub-Category": product_info["Sub-Category"],
                "Quantity": 1,
                "Price": unit_price
            }
            cart_df = pd.concat([cart_df, pd.DataFrame([new_item])], ignore_index=True)

        # Lưu lại CSV
        cart_df.to_csv(cart_file, index=False)

        # Cập nhật lại session_state
        user_cart = cart_df[cart_df["Customer Name"] == username]
        st.session_state["cart_items"] = user_cart.to_dict(orient="records")
        st.session_state["cart_count"] = user_cart["Quantity"].sum()

    def buy_now():
        product_rows = df[df["Product Name"] == selected_product]
        if product_rows.empty:
            st.error("Không tìm thấy sản phẩm.")
            return

        csv_file = "data/Global_Superstore2.csv"
        df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1")
        today = datetime.now()

        existed_order = df_existing[
            (df_existing["Customer Name"] == username) &
            (df_existing["Product Name"] == selected_product)
        ]

        if not existed_order.empty:
            row = existed_order.iloc[0].copy()
            row["Order Date"] = today
            row["Ship Date"] = today
            df_existing.loc[existed_order.index[0], ["Order Date", "Ship Date"]] = [today, today]
            df_existing.to_csv(csv_file, index=False, encoding="ISO-8859-1")
        else:
            row = product_rows.drop_duplicates(subset=["Product Name"]).iloc[0].copy()
            row["Customer Name"] = username
            row["Order ID"] = f"BUY-{today.strftime('%Y%m%d%H%M%S%f')}"
            row["Order Date"] = today
            row["Ship Date"] = today

            df_updated = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
            df_updated.to_csv(csv_file, index=False, encoding="ISO-8859-1")

        st.session_state["purchased"].append(row)
        st.switch_page("pages/my_orders.py")

    col1, col2, col3 = st.columns([1, 2, 7])
    with col1:
        st.button("🛒", on_click=add_to_cart)
    with col2:
        st.button("Mua ngay", on_click=buy_now)

    related_orders = df[df["Product Name"] == selected_product]
    with st.expander(f"{len(related_orders)} đơn hàng liên quan đến sản phẩm này"):
        st.dataframe(related_orders, height=400)
