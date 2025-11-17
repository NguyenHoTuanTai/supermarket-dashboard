import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.offline as py
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LinearRegression
from scipy.stats import zscore


st.set_page_config(page_title="Supermarket Dashboard", layout="wide")


def load_fe():
    with open("fe.html", "r", encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)


load_fe()



# Upload

def multi_toggle_filter(title, df_column, key_prefix):
    st.write(f"### {title}")
    st.markdown('<div class="scroll-box">', unsafe_allow_html=True)

    selected = []
    unique_vals = df_column.dropna().unique()

    for val in unique_vals:
        key = f"{key_prefix}_{val}"

        # default = True (bật)
        if key not in st.session_state:
            st.session_state[key] = True  

        if st.toggle(str(val), key=key):
            selected.append(val)

    st.markdown('</div>', unsafe_allow_html=True)
    return selected

uploaded = st.file_uploader("Tải file CSV dữ liệu", type=["csv"])

if uploaded:

    df = pd.read_csv(
    uploaded,
    encoding="ISO-8859-1",
    parse_dates=["Order Date", "Ship Date"],
    dayfirst=True
    )

    #Chuẩn hóa
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year.astype("Int64")
    df["Month"] = df["Order Date"].dt.month
    
    


    # làm sạch năm
    years_list = sorted([int(y) for y in df["Year"].dropna().unique()])

    st.subheader("Xem dữ liệu")
    st.dataframe(df.head(10))


    #============================
    #Filter

    #Reset
    st.sidebar.subheader("Lọc dữ liệu")
    if st.sidebar.button("Reset filter"):
        st.session_state.clear()

    #NĂM 
    with st.sidebar.expander("Năm", expanded=False):
        year_filter = []
        for y in years_list:
            key = f"year_{y}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(y), key=key):
                year_filter.append(y)
    with st.sidebar.expander("Tháng", expanded=False):
        month_filter = []
        for m in range(1, 13):
            key = f"month_{m}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(f"Tháng {m}", key=key):
                month_filter.append(m)


    #CATEGORY
    with st.sidebar.expander("Category", expanded=False):
        category_filter = []
        for c in df["Category"].dropna().unique():
            key = f"cat_{c}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(c), key=key):
                category_filter.append(c)


    #REGION
    with st.sidebar.expander("Region", expanded=False):
        region_filter = []
        for r in df["Region"].dropna().unique():
            key = f"reg_{r}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(r), key=key):
                region_filter.append(r)

    #MARKET 
    with st.sidebar.expander("Market", expanded=False):
        market_filter = []
        for m in df["Market"].dropna().unique():
            key = f"mar_{m}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(m), key=key):
                market_filter.append(m)
 
    #SEGMENT  
    with st.sidebar.expander("Segment", expanded=False):
        segment_filter = []
        for s in df["Segment"].dropna().unique():
            key = f"seg_{s}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(s), key=key):
                segment_filter.append(s)


    #SHIP MODE
    with st.sidebar.expander("Ship Mode", expanded=False):
        ship_filter = []
        for sm in df["Ship Mode"].dropna().unique():
            key = f"ship_{sm}"
            if key not in st.session_state:
                st.session_state[key] = True
            if st.toggle(str(sm), key=key):
                ship_filter.append(sm)
    

    #ÁP DỤNG FILTERS
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered["Year"].isin(year_filter)]
    df_filtered = df_filtered[df_filtered["Month"].isin(month_filter)]
    df_filtered = df_filtered[df_filtered["Category"].isin(category_filter)]
    df_filtered = df_filtered[df_filtered["Region"].isin(region_filter)]
    df_filtered = df_filtered[df_filtered["Market"].isin(market_filter)]
    df_filtered = df_filtered[df_filtered["Segment"].isin(segment_filter)]
    df_filtered = df_filtered[df_filtered["Ship Mode"].isin(ship_filter)]

    st.sidebar.markdown("---")
    with st.sidebar.subheader("Chức năng"):
        st.sidebar.download_button(
                label="Tải dữ liệu đã lọc (CSV)",
                data=df_filtered.to_csv(index=False).encode('utf-8'),
                file_name="filtered_data.csv",
                mime="text/csv"
        )
    with st.sidebar:
        show_summary = st.checkbox("Hiện thống kê tổng hợp")

    def generate_insights(df):

        summary = {}
        action_plan = []

        MIN_SALES = 200
        MIN_ORDERS = 3
        MIN_LOSS = -50

        #TỔNG QUAN
        total_sales = df["Sales"].sum()
        total_profit = df["Profit"].sum()

        summary["total_sales"] = total_sales
        summary["total_profit"] = total_profit
        summary["profit_status"] = (
            "Lợi nhuận tổng thể DƯƠNG"
            if total_profit > 0
            else "Lợi nhuận tổng thể ÂM"
        )
        #TOP SKU LỖ NẶNG NHẤT
        prod_profit = df.groupby("Product Name")["Profit"].sum().reset_index()
        df_losses = prod_profit[prod_profit["Profit"] < 0].sort_values("Profit")

        top_n = min(5, len(df_losses))
        summary["top_loss_sku"] = df_losses.head(top_n).to_dict("records")
        summary["top_loss_title"] = f"Top {top_n} SKU lỗ nặng nhất"

        #SKU LỖ ≥ 3 THÁNG LIÊN TIẾP
        df["Month"] = df["Order Date"].dt.to_period("M")

        monthly = df.groupby(["Product Name", "Month"]).agg(
            monthly_sales=("Sales", "sum"),
            monthly_profit=("Profit", "sum"),
            orders=("Order ID", "count")
        ).reset_index()

        #meaning filters
        monthly = monthly[
            (monthly["monthly_sales"] >= MIN_SALES)
            & (monthly["orders"] >= MIN_ORDERS)
        ]

        monthly["is_loss"] = monthly["monthly_profit"] < MIN_LOSS

        risky = []
        for sku in monthly["Product Name"].unique():
            sub = monthly[monthly["Product Name"] == sku].sort_values("Month")
            streak = 0
            max_streak = 0
            for v in sub["is_loss"]:
                if v:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 0
            if max_streak >= 3:
                risky.append(sku)

        summary["risky_sku_count"] = len(risky)
        summary["risky_sku_preview"] = risky[:5]

        #CATEGORY TREND (Slope-based)
        df["MonthStr"] = df["Order Date"].dt.to_period("M").astype(str)
        g = df.groupby(["Category", "MonthStr"])["Sales"].sum().reset_index()

        trend_up, trend_down = [], []

        for cat in g["Category"].unique():
            sub = g[g["Category"] == cat].sort_values("MonthStr")
            if len(sub) < 3:
                continue

            sub["t"] = np.arange(len(sub))

            X = sub["t"].values.reshape(-1, 1)
            y = sub["Sales"].values

            model = LinearRegression()
            model.fit(X, y)

            slope = model.coef_[0]
            avg_sales = y.mean()

            if slope > 0.02 * avg_sales:
                trend_up.append(cat)
            elif slope < -0.02 * avg_sales:
                trend_down.append(cat)

        summary["trend_up"] = trend_up
        summary["trend_down"] = trend_down

        #CATEGORY HEALTH SCORE (v3 PRO)
        cat_scores = []

        # Chuẩn hóa trend thành dictionary
        trend_dict = {cat: "up" for cat in trend_up}
        trend_dict.update({cat: "down" for cat in trend_down})

        for cat, sub in df.groupby("Category"):
            sales = sub["Sales"].sum()
            profit = sub["Profit"].sum()

            margin = profit / max(sales, 1)
            loss_ratio = (sub["Profit"] < 0).mean()

            #Margin score (scale về -1 → 1 trong khoảng -20% đến +20%) -----
            margin_score = min(max(margin, -0.2), 0.2) / 0.2   # normalize
            margin_score = (margin_score + 1) / 2              # convert → 0 → 1

            #Loss score (1 tốt – 0 xấu) -----
            loss_score = 1 - loss_ratio

            #rend score
            if cat in trend_dict:
                if trend_dict[cat] == "up":
                    trend_score = 1
                else:
                    trend_score = 0
            else:
                trend_score = 0.5 

            # ----- Combine -----
            score = (
                margin_score * 0.4 +    
                loss_score * 0.4 +      
                trend_score * 0.2       
            ) * 100

            score = round(score, 1)
            cat_scores.append([cat, score])

        summary["cat_health"] = cat_scores

        #ROOT CAUSE
        root_causes = []

        # margin thấp
        df["Margin"] = df["Profit"] / df["Sales"]
        if (df["Margin"] < 0.1).sum() > 0:
            root_causes.append("Nhiều SKU có biên lợi nhuận thấp (<10%).")

        #discount và profit
        if "Discount" in df.columns:
            tmp = df.groupby("Discount")["Profit"].mean().reset_index()
            if tmp["Profit"].corr(tmp["Discount"]) < 0:
                root_causes.append("Discount cao đang làm giảm mạnh lợi nhuận.")

        #shipping cost
        if "Shipping Cost" in df.columns:
            root_causes.append("Một số SKU đang chịu chi phí vận chuyển cao bất thường.")

        summary["root_causes"] = root_causes

        #ACTION PLAN thông minh
        # rủi ro tổng hợp
        risk_level = "Thấp"
        if summary["risky_sku_count"] >= 20:
            risk_level = "Cao"
        elif summary["risky_sku_count"] >= 5:
            risk_level = "Trung bình"

        summary["risk_level"] = risk_level

        #kế hoạch
        if summary["risky_sku_count"] > 0:
            action_plan.append(
                f"Ưu tiên 1: Xử lý {summary['risky_sku_count']} SKU lỗ ≥3 tháng liên tiếp."
            )

        if len(trend_down) > 0:
            action_plan.append(
                f"Ưu tiên 2: Category suy giảm: {', '.join(trend_down)} → cần tối ưu marketing & pricing."
            )

        if len(trend_up) > 0:
            action_plan.append(
                f"Ưu tiên 3: Category tăng trưởng: {', '.join(trend_up)} → tăng tồn kho & đẩy bán."
            )

        if (df["Margin"] < 0.1).sum() > 0:
            action_plan.append(
                "Ưu tiên 4: Điều chỉnh giá/đàm phán NCC cho SKU margin thấp."
            )

        action_plan.append("Tối ưu các SKU có shipping cost cao bất thường.")

        return summary, action_plan


    summary, actions = generate_insights(df_filtered)



    

    
   
    #==========================
    # KPIs
    total_sales = df_filtered["Sales"].sum()
    total_profit = df_filtered["Profit"].sum()
    total_orders = df_filtered.shape[0]

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Tổng Doanh Thu</div>
            <div class="kpi-value">${total_sales:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Tổng Lợi Nhuận</div>
            <div class="kpi-value">${total_profit:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Tổng Số Đơn</div>
            <div class="kpi-value">{total_orders:,}</div>
        </div>
        """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Doanh thu theo thời gian", "Category", "Lợi nhuận","Region","Top 10 sản phẩm bán chạy","Top 10 sản phẩm lỗ"])

    # Tab 1: Sales Over Time
    with tab1:
        st.subheader("Doanh thu theo thời gian (Month)")

        df_filtered["Month"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
        sales_time = df_filtered.groupby("Month")["Sales"].sum().reset_index()

        fig = px.line(
            sales_time,
            x="Month",
            y="Sales",
            title="Sales Over Time",
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Category
    with tab2:
        st.subheader("Doanh thu theo Category")

        sales_category = df_filtered.groupby("Category")["Sales"].sum().reset_index()

        fig2 = px.bar(
            sales_category,
            x="Category",
            y="Sales",
            title="Revenue by Category",
            color="Category",
            template="plotly_white"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Tab 3: Profit by Sub-category
    with tab3:
        st.subheader("Lợi nhuận theo Sub-Category")

        profit_sub = df_filtered.groupby("Sub-Category")["Profit"].sum().reset_index()

        fig3 = px.bar(
            profit_sub.sort_values("Profit", ascending=False),
            x="Sub-Category",
            y="Profit",
            title="Profit by Sub-Category",
            color="Profit",
            template="plotly_white"
        )
        st.plotly_chart(fig3, use_container_width=True)
    with tab4:
        st.subheader("Doanh thu theo Region")

        sales_category = df_filtered.groupby("Region")["Sales"].sum().reset_index()

        fig4 = px.bar(
            sales_category,
            x="Region",
            y="Sales",
            title="Revenue by Region",
            color="Region",
            template="plotly_white"
        )
        st.plotly_chart(fig4, use_container_width=True)
    with tab5:
        st.subheader("Top 10 sản phẩm doanh thu cao nhất")

        top10_products = (
            df_filtered.groupby("Product Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig5 = px.bar(
            top10_products,
            x="Sales",
            y="Product Name",
            orientation="h",
            title="Top 10 Products with Highest Revenue",
            text_auto=".2s"
        )
        fig5.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig5, use_container_width=True)
    with tab6:
        st.subheader("Top 10 sản phẩm lỗ nặng")

        top10_profit_bad = (
            df_filtered.groupby("Product Name")["Profit"]
            .sum()
            .sort_values(ascending=True)
            .head(10)
            .reset_index()
        )

        fig6 = px.bar(
            top10_profit_bad,
            x="Profit",
            y="Product Name",
            orientation="h",
            title="Top 10 products with heavy losses",
            text_auto=".2s",
            color_discrete_sequence=["#DC3545"]
        )
        st.plotly_chart(fig6, use_container_width=True)

    
        

    t1, t2,t3 = st.tabs(["Dự báo doanh thu", "Dự đoán khách hàng rời đi","code thêm machine learning ở đây"])

    with t1:
        st.subheader("Dự báo doanh thu 90 ngày tiếp theo (Prophet)")

        #Gộp theo tuần
        weekly_sales = df.groupby(pd.Grouper(key='Order Date', freq='W'))['Sales'].sum().reset_index()
        weekly_sales.rename(columns={'Order Date':'ds','Sales':'y'}, inplace=True)

        #train – test
        last_date = weekly_sales['ds'].max()
        test_start = last_date - pd.Timedelta(weeks=4)   # 4 tuần cuối
        train = weekly_sales[weekly_sales['ds'] <= test_start]
        test = weekly_sales[weekly_sales['ds'] > test_start]

        #Prophet
        model_t1 = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
        model_t1.fit(train)

        future = model_t1.make_future_dataframe(periods=4+12, freq='W')  # 4 tuần test + 12 tuần dự báo
        forecast = model_t1.predict(future)

        #Forecast test + forecast 90 ngày
        forecast_test = forecast[(forecast['ds'] > test_start) & (forecast['ds'] <= last_date)]
        forecast_90 = forecast[forecast['ds'] > last_date]

        #Accuracy
        y_true = test['y'].values
        y_pred = forecast_test['yhat'].values

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        #SMAPE
        def smape(y_true, y_pred):
            return 100*np.mean(2*np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))

        smape_val = smape(y_true, y_pred)
        accuracy = 100 - smape_val

        print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, SMAPE: {smape_val:.2f}%, Accuracy: {accuracy:.2f}%")

        #dữ liệu vẽ
        forecast_90_plot = forecast_90[['ds','yhat']].copy()
        forecast_90_plot.rename(columns={'ds':'Date','yhat':'Sales'}, inplace=True)
        forecast_90_plot['Type'] = 'Forecast'

        test_plot = test.copy()
        test_plot.rename(columns={'ds':'Date','y':'Sales'}, inplace=True)
        test_plot['Type'] = 'Actual'

        plot_df = pd.concat([test_plot, forecast_90_plot], ignore_index=True)

        #Plot
        fig_t1 = px.line(plot_df, x='Date', y='Sales', color='Type', markers=True)

        fig_t1.add_annotation(
            xref="paper", yref="paper",
            x=0.5, y=1.12,                     
            text=f"Độ chính xác mô hình: {accuracy:.2f}%",
            showarrow=False,
            font=dict(size=16, color="red")    
        )

        st.plotly_chart(fig_t1)

    with t2:
        st.subheader("Churn Prediction")

        #chuẩn bị dữ liệu
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

        rfm = df.groupby('Customer ID').agg({
            'Order Date': lambda x: (snapshot_date - x.max()).days,  # Recency
            'Order ID': 'nunique',                                  # Frequency
            'Sales': 'sum'                                          # Monetary
        }).reset_index()

        rfm.rename(columns={
            'Order Date':'Recency(Lần mua gần nhất)',
            'Order ID':'Frequency(số lần mua)',
            'Sales':'Monetary(tiền đã chi)'
        }, inplace=True)

        rfm['Churn'] = (rfm['Recency(Lần mua gần nhất)'] > 90).astype(int)

        rfm['Churn_Label'] = rfm['Churn'].map({0: 'An toàn', 1: 'Nguy cơ rời bỏ'})

        #Train-test split
        X = rfm[['Recency(Lần mua gần nhất)','Frequency(số lần mua)','Monetary(tiền đã chi)']]
        y = rfm['Churn']

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

        #Random Forest
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        #Predict
        rfm['Churn_Prob'] = clf.predict_proba(X_scaled)[:,1]
        

        def churn_risk_label(prob):
            if prob >= 0.7:
                return 'Nguy cơ rời bỏ'
            else:
                return 'An toàn'
        
        rfm['Churn_Label_ML'] = rfm['Churn_Prob'].apply(churn_risk_label)

        #độ chính xác 
        y_pred_test = clf.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred_test) * 100
        st.write(f"**Độ chính xác của mô hình:** {accuracy:.2f}%")

        #Count số khách
        risk_count = rfm.groupby('Churn_Label_ML')['Customer ID'].nunique().reset_index()
        risk_count.rename(columns={'Customer ID':'Count'}, inplace=True)

        #Vẽ Pie/Donut chart
        fig_risk = px.pie(
            risk_count, 
            names='Churn_Label_ML', 
            values='Count', 
            hole=0.4,
            color='Churn_Label_ML', 
            color_discrete_map={'Nguy cơ rời bỏ':'red','An toàn':'green'}
        )
        fig_risk.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_risk)

        #Show Top 10 Khách Nguy cơ rời bỏ
        top_high_risk = rfm[rfm['Churn_Label_ML']=='Nguy cơ rời bỏ'].sort_values('Churn_Prob', ascending=False).head(10)
        st.subheader("Top 10 Khách Nguy cơ rời bỏ")
        st.dataframe(top_high_risk[[
            'Customer ID',
            'Recency(Lần mua gần nhất)',
            'Frequency(số lần mua)',
            'Monetary(tiền đã chi)',
            'Churn_Label_ML'
        ]])
    with t3:
        st.write("code thêm ở đây")


    if show_summary:
        st.title("báo cáo và lời khuyên")
        summary, actions = generate_insights(df_filtered)

        st.header("Executive Summary")
        st.markdown(f"### {summary['profit_status']}")
        st.metric("Tổng Sales", f"{summary['total_sales']:,} USD")
        st.metric("Tổng Profit", f"{summary['total_profit']:,} USD")

        # Top SKU lỗ
        st.subheader(summary["top_loss_title"])
        for p in summary["top_loss_sku"]:
            st.markdown(f"- **{p['Product Name']}**: {p['Profit']:.0f} USD")

        # SKU lỗ dài hạn
        st.subheader("SKU lỗ ≥ 3 tháng liên tiếp")
        st.markdown(f"Tổng cộng: **{summary['risky_sku_count']} SKU**")
        for p in summary["risky_sku_preview"]:
            st.markdown(f"- {p}")

        # Xu hướng Category
        st.subheader("Category tăng trưởng")
        for c in summary["trend_up"]:
            st.markdown(f"- {c}")

        st.subheader("Category suy giảm")
        for c in summary["trend_down"]:
            st.markdown(f"- {c}")

        # Root cause
        st.subheader("Nguyên nhân chính (Root Cause)")
        for r in summary["root_causes"]:
            st.markdown(f"- {r}")

        # Action plan
        st.header("Action Plan – Ưu tiên theo mức độ")
        for a in actions:
            st.markdown(f"- {a}")

        # Category Score
        st.subheader("Category Health Score")
        for cat, score in summary["cat_health"]:
            st.markdown(f"- **{cat}**: {score}/100")

        st.info("""
        **Chỉ số gợi ý:**
        - 70–90 điểm: Category ổn định
        - 30–60 điểm: Category gặp vấn đề
        - <30 điểm: Category nguy hiểm
        """)


    

    



