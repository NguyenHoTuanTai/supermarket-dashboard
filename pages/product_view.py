import streamlit as st
import pandas as pd
import plotly.express as px

# --- PHẢI ĐỂ LÊN TRÊN CÙNG ---
st.set_page_config(
    page_title="Product View",
    layout="wide"   
)

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

if st.session_state["role"] != "user":
    st.error("❌ Trang này chỉ dành cho USER.")
    st.stop()

# user thì ẩn "app"
if st.session_state["role"] == "user":
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] ul li:nth-child(2) {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Khởi tạo giỏ hàng & purchased ---
if "cart_count" not in st.session_state:
    st.session_state["cart_count"] = 0
if "cart_items" not in st.session_state:
    st.session_state["cart_items"] = []
if "purchased" not in st.session_state:
    st.session_state["purchased"] = []

username = st.session_state["username"]

# --- CSS + Logout + Giỏ hàng góc phải ---
st.markdown("""
<style>
.fixed-top-right {
    position: fixed;
    top: 15px;
    right: 20px;
    z-index: 999;
    display: flex;
    align-items: center;
    gap: 10px;  /* khoảng cách giữa giỏ hàng và logout */
}

.cart-box {
    font-size: 18px;
    background-color: white;
    padding: 5px 10px;
    border-radius: 5px;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.3);
    white-space: nowrap;  /* không giãn rộng */
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
    st.markdown(
        f'<div class="cart-box">🛒 <span style="color:red; font-weight:bold;">{st.session_state["cart_count"]}</span></div>',
        unsafe_allow_html=True
    )
with col3:
    if st.button("🚪 Logout", key="logout_btn"):
        st.session_state.clear()
        st.switch_page("login.py")


# --- UI chính ---
st.title("📊 Dashboard Supermarket")

# --- Load dữ liệu ---
df = pd.read_csv(
    "data/Global_Superstore2.csv",
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
)

# --- Top 20 sản phẩm bán chạy ---
st.subheader("🔥 Top 20 sản phẩm bán chạy nhất")

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

# --- Search + Chi tiết sản phẩm ---
st.subheader("🔍 Khám phá sản phẩm")

search_query = st.text_input("Tìm sản phẩm bất kỳ", "")

# Bộ lọc Category
categories = ["Tất cả"] + sorted(df["Category"].unique())
selected_category = st.selectbox("Lọc theo Category", categories)

# Bộ lọc Sub-Category phụ thuộc Category
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

    # --- Thêm vào giỏ + Mua ngay ---
    def add_to_cart():
        st.session_state["cart_count"] += 1
        st.session_state["cart_items"].append({
            "Product Name": product_info['Product Name'],
            "Product ID": product_info['Product ID'],
            "Category": product_info['Category'],
            "Sub-Category": product_info['Sub-Category']
        })
        st.success(f"✅ {selected_product} đã thêm vào giỏ hàng!")

    def buy_now():
        row = df[df["Product Name"] == selected_product].iloc[0].copy()

        # Cập nhật thông tin người mua và đơn hàng
        row["Customer Name"] = username
        row["Order ID"] = f"BUY-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}"
        row["Order Date"] = pd.Timestamp.now()
        row["Ship Date"] = pd.Timestamp.now()

        # Thêm vào session_state
        st.session_state["purchased"].append(row)

        # --- Cập nhật CSV ---
        csv_file = "data/Global_Superstore2.csv"
        try:
            df_existing = pd.read_csv(csv_file, encoding="ISO-8859-1", parse_dates=["Order Date", "Ship Date"])
            df_updated = pd.concat([df_existing, pd.DataFrame([row])], ignore_index=True)
            df_updated.to_csv(csv_file, index=False, encoding="ISO-8859-1")
        except Exception as e:
            st.error(f"❌ Lỗi khi cập nhật CSV: {e}")
            return

        # --- Thông báo modal ---
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                f"""
                <div style="padding:20px; border:2px solid #4CAF50; border-radius:10px; background-color:#d4edda; color:#155724;">
                    🎉 Bạn đã mua <b>{selected_product}</b> thành công!
                </div>
                """
                , unsafe_allow_html=True)
            if st.button("✅ Xác nhận"):
                placeholder.empty()
                st.switch_page("pages/my_orders.py")



    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("🛒 Thêm vào giỏ", on_click=add_to_cart)
    with col2:
        st.button("🛍️ Mua ngay", on_click=buy_now)

    # --- Đơn hàng liên quan ---
    related_orders = df[df["Product Name"] == selected_product]
    with st.expander(f"📄 {len(related_orders)} đơn hàng liên quan đến sản phẩm này"):
        st.dataframe(related_orders, height=400)
