import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard Quản trị Khách hàng Rời bỏ", layout="wide")

st.title("Phân tích Khách hàng Rời bỏ")

# Color Palette exactly matching the book
COLOR_GAIN = "#C0C0C0"  # Grey
COLOR_LOSS = "#F19C99"  # Salmon/Red
COLOR_NET = "#3A7596"   # Muted Blue
COLOR_MARKER = "#F39C12" # Orange for line markers

@st.cache_data(show_spinner="Đang tải dữ liệu và tính toán chỉ số...")
def load_data():
    data_dir = "star_schema_data"
    if not os.path.exists(data_dir):
        # Fallback to single csv if star schema not generated properly
        return pd.read_csv("customer_churn_governance_dataset.csv", parse_dates=["Month", "Last_Updated_Date"])

    fact_df = pd.read_csv(os.path.join(data_dir, "fact_churn.csv"))
    dim_time = pd.read_csv(os.path.join(data_dir, "dim_time.csv"))
    dim_region = pd.read_csv(os.path.join(data_dir, "dim_region.csv"))
    dim_segment = pd.read_csv(os.path.join(data_dir, "dim_segment.csv"))
    dim_product = pd.read_csv(os.path.join(data_dir, "dim_product.csv"))
    
    df = (fact_df
          .merge(dim_time, on="time_id", how="left")
          .merge(dim_region, on="region_id", how="left")
          .merge(dim_segment, on="segment_id", how="left")
          .merge(dim_product, on="product_id", how="left"))
    
    df["Month"] = pd.to_datetime(df["Month"])
    df["Last_Updated_Date"] = pd.to_datetime(df["Last_Updated_Date"])
    return df

df = load_data()

with st.sidebar:
    st.header("Bộ lọc")
    regions = st.multiselect("Khu vực", sorted(df.Region.unique()), default=sorted(df.Region.unique()))

f_base = df[df.Region.isin(regions)].copy()

def render_dashboard(f, tab_id):
    if len(f) == 0:
        st.warning(f"Không tìm thấy dữ liệu cho bộ lọc đã chọn.")
        return

    # Aggregate by month for KPIs
    monthly_kpi = f.groupby("Month", as_index=False).agg(
        Beginning_Customers=("Beginning_Customers", "sum"),
        New_Customers=("New_Customers", "sum"),
        Lost_Customers=("Lost_Customers", "sum"),
        Running_Total=("Running_Total", "sum"),
        Beginning_MRR=("Beginning_MRR", "sum"),
        Expansion_MRR=("Expansion_MRR", "sum"),
        Lost_MRR=("Lost_MRR", "sum")
    ).sort_values("Month")

    if len(monthly_kpi) > 0:
        curr = monthly_kpi.iloc[-1]
        
        # Calculate Current Month Metrics
        c_beg_cust = curr['Beginning_Customers']
        c_lost_cust = curr['Lost_Customers']
        c_end_cust = curr['Running_Total']
        
        c_beg_mrr = curr['Beginning_MRR']
        c_exp_mrr = curr['Expansion_MRR']
        c_lost_mrr = curr['Lost_MRR']
        
        cust_churn = (c_lost_cust / c_beg_cust * 100) if c_beg_cust > 0 else 0
        rev_churn = (c_lost_mrr / c_beg_mrr * 100) if c_beg_mrr > 0 else 0
        net_rev_churn = ((c_lost_mrr - c_exp_mrr) / c_beg_mrr * 100) if c_beg_mrr > 0 else 0
        adj_churn = (c_lost_cust / ((c_beg_cust + c_end_cust) / 2) * 100) if (c_beg_cust + c_end_cust) > 0 else 0
        
        cust_churn_delta, rev_churn_delta, net_rev_churn_delta, adj_churn_delta = None, None, None, None
        
        if len(monthly_kpi) > 1:
            prev = monthly_kpi.iloc[-2]
            p_beg_cust = prev['Beginning_Customers']
            p_lost_cust = prev['Lost_Customers']
            p_end_cust = prev['Running_Total']
            
            p_beg_mrr = prev['Beginning_MRR']
            p_exp_mrr = prev['Expansion_MRR']
            p_lost_mrr = prev['Lost_MRR']
            
            p_cust_churn = (p_lost_cust / p_beg_cust * 100) if p_beg_cust > 0 else 0
            p_rev_churn = (p_lost_mrr / p_beg_mrr * 100) if p_beg_mrr > 0 else 0
            p_net_rev_churn = ((p_lost_mrr - p_exp_mrr) / p_beg_mrr * 100) if p_beg_mrr > 0 else 0
            p_adj_churn = (p_lost_cust / ((p_beg_cust + p_end_cust) / 2) * 100) if (p_beg_cust + p_end_cust) > 0 else 0
            
            cust_churn_delta = cust_churn - p_cust_churn
            rev_churn_delta = rev_churn - p_rev_churn
            net_rev_churn_delta = net_rev_churn - p_net_rev_churn
            adj_churn_delta = adj_churn - p_adj_churn
            
        st.subheader(f"Chỉ số Hiệu quả Chính (Tháng gần nhất: {curr['Month'].strftime('%m/%Y')})")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Tỷ lệ KH Rời bỏ", f"{cust_churn:.2f}%", f"{cust_churn_delta:.2f}%" if cust_churn_delta is not None else None, delta_color="inverse")
        kpi2.metric("Tỷ lệ DT Rời bỏ", f"{rev_churn:.2f}%", f"{rev_churn_delta:.2f}%" if rev_churn_delta is not None else None, delta_color="inverse")
        kpi3.metric("Tỷ lệ DT Rời bỏ Ròng", f"{net_rev_churn:.2f}%", f"{net_rev_churn_delta:.2f}%" if net_rev_churn_delta is not None else None, delta_color="inverse")
        kpi4.metric("Tỷ lệ Rời bỏ Điều chỉnh", f"{adj_churn:.2f}%", f"{adj_churn_delta:.2f}%" if adj_churn_delta is not None else None, delta_color="inverse")
        st.markdown("---")

    # Layout
    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.subheader("Hoạt động của Khách hàng - Tổng quan")
        
        # Chart 1: Subscriber Activity All
        monthly = f.groupby("Month", as_index=False).agg(
            New_Customers=("New_Customers", "sum"),
            Lost_Customers=("Lost_Customers", "sum"),
            Net_Customers=("Net_Customers", "sum")
        ).sort_values("Month")
        
        # Calculate Running Total starting from the first month
        monthly["Running_Total"] = monthly["Net_Customers"].cumsum()
        monthly["Prev_Running_Total"] = monthly["Running_Total"].shift(1).fillna(0)
        
        fig1 = go.Figure()
        
        # Gain Bar
        fig1.add_trace(go.Bar(
            x=monthly["Month"],
            y=monthly["New_Customers"],
            base=monthly["Prev_Running_Total"],
            marker_color=COLOR_GAIN, 
            name="Tăng"
        ))
        
        # Loss Bar
        fig1.add_trace(go.Bar(
            x=monthly["Month"],
            y=-monthly["Lost_Customers"],
            base=monthly["Prev_Running_Total"] + monthly["New_Customers"],
            marker_color=COLOR_LOSS, 
            name="Giảm"
        ))
        
        # Net Line
        fig1.add_trace(go.Scatter(
            x=monthly["Month"],
            y=monthly["Running_Total"],
            mode="lines+markers+text",
            line=dict(color=COLOR_NET, width=3),
            marker=dict(size=8, color=COLOR_NET),
            name="Thực tăng",
            text=[f"{val:,.0f}" for val in monthly["Running_Total"]],
            textposition="bottom right"
        ))
        
        fig1.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                tickformat="%m/%Y",
                showgrid=False
            ),
            yaxis=dict(showgrid=True, title="Số lượng Khách hàng"),
            legend=dict(
                orientation="v",
                yanchor="bottom",
                y=0.1,
                xanchor="right",
                x=0.99
            ),
            height=450,
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig1, use_container_width=True, key=f"fig1_{tab_id}")
        
        
        st.subheader("Biến động Khách hàng thực tế theo Khu vực")
        # Chart 2: Net subscriber activity by division
        reg_monthly = f.groupby(["Region", "Month"], as_index=False).agg(
            Net_Customers=("Net_Customers", "sum"),
            New_Customers=("New_Customers", "sum"),
            Lost_Customers=("Lost_Customers", "sum")
        ).sort_values(["Region", "Month"])
        
        reg_monthly["Running_Total"] = reg_monthly.groupby("Region")["Net_Customers"].cumsum()
        
        # We will do a line chart for running total by region
        fig2 = px.line(
            reg_monthly, x="Month", y="Running_Total", color="Region", 
            markers=True,
            color_discrete_sequence=[COLOR_NET], # All lines same blue color like in the book
            labels={"Running_Total": "Khách hàng thực tăng", "Month": ""}
        )
        # Update markers to orange like in the book
        fig2.update_traces(marker=dict(color=COLOR_MARKER, size=6))
        
        # Add text to the last point of each line
        for i, region in enumerate(reg_monthly["Region"].unique()):
            region_data = reg_monthly[reg_monthly["Region"] == region]
            if not region_data.empty:
                last_point = region_data.iloc[-1]
                fig2.add_annotation(
                    x=last_point["Month"],
                    y=last_point["Running_Total"],
                    text=f"<b>{region}</b><br>{last_point['Running_Total']:,.0f}",
                    showarrow=False,
                    xanchor="left",
                    xshift=10
                )
        
        # Inset-like side chart for totals by region
        totals_by_reg = f.groupby("Region", as_index=False).agg(
            Gained=("New_Customers", "sum"),
            Lost=("Lost_Customers", "sum"),
            Net=("Net_Customers", "sum")
        )
        
        fig_inset = go.Figure()
        fig_inset.add_trace(go.Bar(
            x=totals_by_reg["Region"], 
            y=totals_by_reg["Gained"], 
            name="Tăng", 
            marker_color=COLOR_GAIN,
            text=[f"{v:,.0f}" for v in totals_by_reg["Gained"]],
            textposition="outside",
            textangle=0,
            textfont=dict(size=11)
        ))
        fig_inset.add_trace(go.Bar(
            x=totals_by_reg["Region"], 
            y=totals_by_reg["Lost"], 
            name="Giảm", 
            marker_color=COLOR_LOSS,
            text=[f"{v:,.0f}" for v in totals_by_reg["Lost"]],
            textposition="outside",
            textangle=0,
            textfont=dict(size=11)
        ))
        fig_inset.add_trace(go.Scatter(
            x=totals_by_reg["Region"], 
            y=totals_by_reg["Net"], 
            mode="markers+text", 
            marker=dict(size=14, color=COLOR_NET), 
            name="Thực tăng",
            text=[f"{v:,.0f}" for v in totals_by_reg["Net"]],
            textposition="top center",
            textfont=dict(size=12, color=COLOR_NET)
        ))
        fig_inset.update_layout(
            barmode="group", 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, visible=False)
        )
        
        # Place inset alongside line chart
        col_inset, col_line = st.columns([1.3, 1.5])
        with col_inset:
            st.plotly_chart(fig_inset, use_container_width=True, key=f"fig_inset_{tab_id}")
        with col_line:
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickformat="%m/%Y", 
                height=350, 
                margin=dict(l=40, r=80, t=30, b=0),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True, key=f"fig2_{tab_id}")
            
    with right_col:
        st.subheader("Chi tiết")
        
        if reg_monthly.empty:
            st.write("Không có dữ liệu.")
        else:
            # Format Pivot Table
            pivot = reg_monthly[["Region", "Month", "New_Customers", "Lost_Customers", "Net_Customers", "Running_Total"]].copy()
            pivot["Month"] = pivot["Month"].dt.strftime("%m/%Y")
            pivot.rename(columns={
                "Region": "Khu vực",
                "Month": "Tháng",
                "New_Customers": "Khách hàng Mới", 
                "Lost_Customers": "Khách hàng Rời bỏ", 
                "Net_Customers": "Thực tăng", 
                "Running_Total": "Tổng tích lũy"
            }, inplace=True)
            
            pivot.set_index(["Khu vực", "Tháng"], inplace=True)
            
            numeric_cols = ["Khách hàng Mới", "Khách hàng Rời bỏ", "Thực tăng", "Tổng tích lũy"]
            
            # Apply styling matching the book: Grey for Gain, Red for Loss, no background for Net and Total
            styled_df = (pivot.style
                         .background_gradient(subset=["Khách hàng Mới"], cmap="Greys", text_color_threshold=0.5)
                         .background_gradient(subset=["Khách hàng Rời bỏ"], cmap="Reds", text_color_threshold=0.5)
                         .format("{:,.0f}", subset=numeric_cols))
                         
            # We use components.html to guarantee that Streamlit does not strip the Pandas Styler CSS
            html_table = styled_df.to_html()
            
            css = """
            <style>
            table {
                width: 100%;
                border-collapse: collapse;
                font-family: sans-serif;
                color: #595959;
                font-size: 14px;
            }
            th, td {
                border: 1px solid #e0e0e0;
                padding: 8px;
                text-align: right;
            }
            thead th {
                background-color: #f5f5f5;
                font-weight: bold;
                text-align: center;
                position: sticky;
                top: 0;
                z-index: 1;
            }
            tbody th {
                text-align: left; 
                background-color: #ffffff;
            }
            </style>
            """
            
            components.html(css + html_table, height=850, scrolling=True)

# Create Tabs
tab1, tab2 = st.tabs(["Khách hàng cá nhân (Phổ thông, VIP, VVIP)", "Khách hàng doanh nghiệp (Startup, SME, Enterprise)"])

with tab1:
    tab1_segments = ["Mass", "VIP", "VVIP"]
    selected_segments_1 = st.multiselect("Lọc phân khúc (Cá nhân)", tab1_segments, default=tab1_segments, key="seg_tab1")
    f_tab1 = f_base[f_base["Segment"].isin(selected_segments_1)]
    render_dashboard(f_tab1, "tab1")

with tab2:
    tab2_segments = ["Startups", "SME", "Enterprise"]
    selected_segments_2 = st.multiselect("Lọc phân khúc (Doanh nghiệp)", tab2_segments, default=tab2_segments, key="seg_tab2")
    f_tab2 = f_base[f_base["Segment"].isin(selected_segments_2)]
    render_dashboard(f_tab2, "tab2")
