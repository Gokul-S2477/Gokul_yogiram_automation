from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ui.upload_ui import upload_section
from core.loader import (
    read_file,
    extract_sales_columns,
    extract_stock_columns,
    extract_ns_columns,
)
from core.sales_metrics import (
    aggregate_sales,
    calculate_average,
    calculate_weighted_demand,
)
from core.ns_logic import calculate_ns_metrics
from core.order_calc import calculate_order_metrics
from core.classification import classify_items


FORECAST_RUN_KEY = "forecast_run_requested"

FORECAST_OUTPUT_COLUMNS = [
    "ITEM_CODE",
    "ITEM_NAME",
    "COMPANY",
    "PACK",
    "MONTHLY_AVG_QTY",
    "WEEKLY_AVG_QTY",
    "DAILY_AVG_QTY",
    "TRUE_WEEKLY_DEMAND",
    "STOCK_QTY",
    "RACK",
    "COST_RATE",
    "LAST_PURCHASE_DT",
    "DAYS_SINCE_LAST_PURCHASE",
    "DAYS_OF_COVER",
    "NS_ACTIVE_DAYS",
    "NS_CONSECUTIVE_MAX",
    "NS_LINES_AVG",
    "NS_QTY_AVG",
    "NS_TREND",
    "NS_LOSS_ORDER_AMT_30D",
    "NS_FILL_RATE_30D",
    "NS_AFFECTED_PARTIES_30D",
    "SAFETY_STOCK",
    "FINAL_ORDER_QTY",
    "FINAL_ORDER_VALUE",
    "MIN_ORDER_QTY",
    "MAX_ORDER_QTY",
    "STOCK_STATUS",
    "ITEM_STATUS",
    "ORDER_REASON",
]


def _fmt_number(value, decimals=0):
    return f"{value:,.{decimals}f}"


def _fmt_amount(value):
    return f"INR {_fmt_number(value, 2)}"


def _first_non_empty(series):
    non_null = series.dropna().astype(str).str.strip()
    non_null = non_null[(non_null != "") & (non_null.str.lower() != "nan")]
    return non_null.iloc[0] if not non_null.empty else ""


def _prefer_non_empty(primary, fallback):
    primary_s = primary.astype(str).str.strip()
    fallback_s = fallback.astype(str).str.strip()
    return primary_s.where((primary_s != "") & (primary_s.str.lower() != "nan"), fallback_s)


def _build_item_master(uploaded):
    item_master_frames = []
    for block in [uploaded["monthly"], uploaded["weekly"], uploaded["daily"]]:
        for file_obj in block.values():
            cleaned = extract_sales_columns(read_file(file_obj))
            item_master_frames.append(
                cleaned[["ITEM_CODE", "ITEM_NAME", "COMPANY", "PACK", "LOCATION"]]
            )

    if not item_master_frames:
        return pd.DataFrame(columns=["ITEM_CODE", "ITEM_NAME", "COMPANY", "PACK", "LOCATION"])

    combined = pd.concat(item_master_frames, ignore_index=True)
    return (
        combined.groupby("ITEM_CODE", as_index=False)
        .agg(
            ITEM_NAME=("ITEM_NAME", _first_non_empty),
            COMPANY=("COMPANY", _first_non_empty),
            PACK=("PACK", _first_non_empty),
            LOCATION=("LOCATION", _first_non_empty),
        )
    )


def _load_sales_averages(uploaded):
    monthly_avg = weekly_avg = daily_avg = None

    if uploaded["monthly"]:
        monthly_total = aggregate_sales(uploaded["monthly"], read_file, extract_sales_columns)
        monthly_avg = calculate_average(monthly_total, len(uploaded["monthly"]), level="MONTHLY")

    if uploaded["weekly"]:
        weekly_total = aggregate_sales(uploaded["weekly"], read_file, extract_sales_columns)
        weekly_avg = calculate_average(weekly_total, len(uploaded["weekly"]), level="WEEKLY")

    if uploaded["daily"]:
        daily_total = aggregate_sales(uploaded["daily"], read_file, extract_sales_columns)
        daily_avg = calculate_average(daily_total, len(uploaded["daily"]), level="DAILY")

    return monthly_avg, weekly_avg, daily_avg


def _load_ns_metrics(uploaded):
    if uploaded["ns"] is None:
        return pd.DataFrame(
            columns=[
                "ITEM_CODE",
                "NS_ACTIVE_DAYS",
                "NS_CONSECUTIVE_MAX",
                "NS_LINES_AVG",
                "NS_QTY_AVG",
                "NS_RECENT_DAYS",
                "NS_TREND",
                "NS_SEVERITY_SCORE",
                "NS_RISK_SCORE",
                "NS_LOSS_ORDER_AMT_30D",
                "NS_FILL_RATE_30D",
                "NS_AFFECTED_PARTIES_30D",
            ]
        )

    ns_raw = extract_ns_columns(read_file(uploaded["ns"]))
    return calculate_ns_metrics(ns_raw, lookback_days=30)


def _build_summary_bundle(final_df):
    report_df = final_df.copy()
    order_df = report_df[report_df["FINAL_ORDER_QTY"] > 0].copy()

    company_for_group = (
        order_df["COMPANY"]
        .astype(str)
        .str.strip()
        .replace("", "UNSPECIFIED")
        .fillna("UNSPECIFIED")
    )
    order_df = order_df.assign(COMPANY_CLEAN=company_for_group)

    top_companies_value = (
        order_df.groupby("COMPANY_CLEAN", as_index=False)["FINAL_ORDER_VALUE"]
        .sum()
        .sort_values("FINAL_ORDER_VALUE", ascending=False)
        .head(10)
        .rename(columns={"COMPANY_CLEAN": "COMPANY", "FINAL_ORDER_VALUE": "ORDER_VALUE"})
    )

    top_companies_qty = (
        order_df.groupby("COMPANY_CLEAN", as_index=False)["FINAL_ORDER_QTY"]
        .sum()
        .sort_values("FINAL_ORDER_QTY", ascending=False)
        .head(10)
        .rename(columns={"COMPANY_CLEAN": "COMPANY", "FINAL_ORDER_QTY": "ORDER_QTY"})
    )

    stock_status_dist = (
        report_df["STOCK_STATUS"]
        .astype(str)
        .str.strip()
        .replace("", "UNKNOWN")
        .value_counts()
        .rename_axis("STOCK_STATUS")
        .reset_index(name="COUNT")
    )

    item_status_dist = (
        report_df["ITEM_STATUS"]
        .astype(str)
        .str.strip()
        .replace("", "UNKNOWN")
        .value_counts()
        .rename_axis("ITEM_STATUS")
        .reset_index(name="COUNT")
    )

    cover_bucket_series = pd.cut(
        report_df["DAYS_OF_COVER"],
        bins=[-0.0001, 2, 7, 14, 30, float("inf")],
        labels=["0-2", "3-7", "8-14", "15-30", "30+"],
    )
    cover_bucket_dist = (
        cover_bucket_series.value_counts(sort=False)
        .rename_axis("COVER_BUCKET")
        .reset_index(name="COUNT")
    )

    top_items_order_value = (
        order_df[["ITEM_CODE", "ITEM_NAME", "COMPANY", "FINAL_ORDER_VALUE", "FINAL_ORDER_QTY"]]
        .sort_values("FINAL_ORDER_VALUE", ascending=False)
        .head(15)
    )

    top_items_ns_loss = (
        report_df[["ITEM_CODE", "ITEM_NAME", "COMPANY", "NS_LOSS_ORDER_AMT_30D"]]
        .sort_values("NS_LOSS_ORDER_AMT_30D", ascending=False)
        .head(15)
    )

    kpis = {
        "total_items": int(len(report_df)),
        "items_to_order": int(len(order_df)),
        "critical_stock_items": int((report_df["STOCK_STATUS"] == "CRITICAL").sum()),
        "low_cover_items": int((report_df["DAYS_OF_COVER"] < 3).sum()),
        "total_order_qty": float(order_df["FINAL_ORDER_QTY"].sum()),
        "total_order_value": float(order_df["FINAL_ORDER_VALUE"].sum()),
        "avg_days_cover": float(report_df["DAYS_OF_COVER"].mean()) if len(report_df) else 0.0,
        "avg_fill_rate_30d": float(report_df["NS_FILL_RATE_30D"].mean()) if len(report_df) else 0.0,
    }

    top_company_name = (
        top_companies_value.iloc[0]["COMPANY"]
        if not top_companies_value.empty
        else "N/A"
    )
    top_company_value = (
        float(top_companies_value.iloc[0]["ORDER_VALUE"])
        if not top_companies_value.empty
        else 0.0
    )

    summary_lines = [
        f"{kpis['total_items']} items analyzed and {kpis['items_to_order']} items need ordering now.",
        f"Total recommendation is {_fmt_number(kpis['total_order_qty'], 2)} units with value {_fmt_amount(kpis['total_order_value'])}.",
        f"{kpis['critical_stock_items']} items are in critical stock and {kpis['low_cover_items']} items are below 3 days of cover.",
        f"Highest company exposure is {top_company_name} with {_fmt_amount(top_company_value)} recommended order value.",
    ]

    kpi_table = pd.DataFrame(
        [
            {"KPI": "Total Items Analyzed", "Value": kpis["total_items"]},
            {"KPI": "Items To Order", "Value": kpis["items_to_order"]},
            {"KPI": "Critical Stock Items", "Value": kpis["critical_stock_items"]},
            {"KPI": "Low Cover Items (<3 Days)", "Value": kpis["low_cover_items"]},
            {"KPI": "Total Order Qty", "Value": round(kpis["total_order_qty"], 2)},
            {"KPI": "Total Order Value", "Value": round(kpis["total_order_value"], 2)},
            {"KPI": "Average Days Of Cover", "Value": round(kpis["avg_days_cover"], 2)},
            {"KPI": "Average NS Fill Rate (30D)", "Value": round(kpis["avg_fill_rate_30d"], 4)},
        ]
    )

    return {
        "summary_lines": summary_lines,
        "kpis": kpis,
        "kpi_table": kpi_table,
        "top_companies_value": top_companies_value,
        "top_companies_qty": top_companies_qty,
        "stock_status_dist": stock_status_dist,
        "item_status_dist": item_status_dist,
        "cover_bucket_dist": cover_bucket_dist,
        "top_items_order_value": top_items_order_value,
        "top_items_ns_loss": top_items_ns_loss,
    }


def _write_summary_sheet(writer, bundle):
    sheet_name = "Summary"

    summary_df = pd.DataFrame({"Executive Summary": bundle["summary_lines"]})
    summary_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0, startcol=0)

    bundle["kpi_table"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=6, startcol=0)
    bundle["top_companies_value"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=6, startcol=4)
    bundle["top_companies_qty"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=6, startcol=8)

    bundle["stock_status_dist"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=22, startcol=0)
    bundle["item_status_dist"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=22, startcol=4)
    bundle["cover_bucket_dist"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=22, startcol=8)

    bundle["top_items_order_value"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=36, startcol=0)
    bundle["top_items_ns_loss"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=36, startcol=7)


def _to_excel(recommendation_df, summary_bundle):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        recommendation_df.to_excel(writer, index=False, sheet_name="Recommendations")
        _write_summary_sheet(writer, summary_bundle)
    buffer.seek(0)
    return buffer.getvalue()


def render_glass_metric(label, value, delta=None, icon="📊", color="#00f2ff"):
    delta_html = ""
    if delta:
        d_color = "#00ff88" if not str(delta).startswith("-") else "#ff4b4b"
        delta_html = f'<div style="color: {d_color}; font-size: 0.85rem; font-weight: 600; margin-top: 4px;">{delta}</div>'
    
    st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
                    <div style="color: white; font-size: 1.6rem; font-weight: 700; margin-top: 8px; font-family: 'Inter', sans-serif;">{value}</div>
                    {delta_html}
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 12px; font-size: 1.2rem;">{icon}</div>
            </div>
            <div style="position: absolute; bottom: 0; left: 0; width: 100%; height: 3px; background: linear-gradient(90deg, transparent, {color}, transparent); opacity: 0.5;"></div>
        </div>
    """, unsafe_allow_html=True)

def _render_summary_dashboard(bundle):
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
            animation: fadeInScale 0.6s ease-out forwards;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(0, 242, 255, 0.3);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.95) translateY(10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        
        .section-header {
            font-size: 1.8rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #fff 0%, #00f2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📊 Strategic Insights</div>', unsafe_allow_html=True)
    
    kpis = bundle["kpis"]
    
    # KPI Grid 1
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_glass_metric("Market Analysis", _fmt_number(kpis["total_items"]), icon="🔍", color="#00f2ff")
    with c2: render_glass_metric("Procurement Need", _fmt_number(kpis["items_to_order"]), icon="📦", color="#ffcc00")
    with c3: render_glass_metric("Critical Risk", _fmt_number(kpis["critical_stock_items"]), icon="⚠️", color="#ff4b4b")
    with c4: render_glass_metric("Supply Efficiency", f"{_fmt_number(kpis['avg_fill_rate_30d'] * 100, 1)}%", icon="⚡", color="#00ff88")

    # KPI Grid 2
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_glass_metric("Total Order Qty", _fmt_number(kpis["total_order_qty"], 0), icon="🔢", color="#b066ff")
    with c2: render_glass_metric("Investment Req", _fmt_amount(kpis["total_order_value"]), icon="💰", color="#00ff88")
    with c3: render_glass_metric("Avg Stock Cover", f"{_fmt_number(kpis['avg_days_cover'], 1)} Days", icon="📅", color="#00f2ff")
    with c4: 
        potential_lost = bundle["top_items_ns_loss"]["NS_LOSS_ORDER_AMT_30D"].sum()
        render_glass_metric("NS Loss Risk", _fmt_amount(potential_lost), icon="📉", color="#ff4b4b")

    st.markdown('<div class="section-header" style="margin-top: 3rem;">📈 Visual Intelligence</div>', unsafe_allow_html=True)
    
    # Row 1: TreeMap and Donut
    r1c1, r1c2 = st.columns([2, 1])
    
    with r1c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig = px.treemap(
            bundle["top_companies_value"],
            path=["COMPANY"],
            values="ORDER_VALUE",
            title="Order Value Distribution by Company",
            color="ORDER_VALUE",
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r1c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        status_df = bundle["stock_status_dist"]
        fig = px.pie(
            status_df, 
            values="COUNT", 
            names="STOCK_STATUS", 
            hole=0.6,
            title="Inventory Health",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2: Animated Horizontal Bar Charts
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)
    
    with r2c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        items_df = bundle["top_items_order_value"].head(10).sort_values("FINAL_ORDER_VALUE", ascending=True)
        fig = px.bar(
            items_df,
            x="FINAL_ORDER_VALUE",
            y="ITEM_NAME",
            orientation='h',
            title="Top Priority Items (By Value)",
            text_auto='.2s',
            template="plotly_dark",
            color="FINAL_ORDER_VALUE",
            color_continuous_scale="Blues"
        )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r2c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        ns_df = bundle["top_items_ns_loss"].head(10).sort_values("NS_LOSS_ORDER_AMT_30D", ascending=True)
        fig = px.bar(
            ns_df,
            x="NS_LOSS_ORDER_AMT_30D",
            y="ITEM_NAME",
            orientation='h',
            title="Supply Risk Exposure (NS Loss)",
            text_auto='.2s',
            template="plotly_dark",
            color="NS_LOSS_ORDER_AMT_30D",
            color_continuous_scale="Reds"
        )
        fig.update_layout(margin=dict(t=50, l=10, r=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_forecast_module():
    st.markdown(
        """
        <div class="forecast-hero">
            <div class="forecast-title">Forecast App</div>
            <div class="forecast-subtitle">
                Demand forecasting and order recommendation with daily, weekly, monthly, stock, and NS signals.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = upload_section()
    st.divider()

    if FORECAST_RUN_KEY not in st.session_state:
        st.session_state[FORECAST_RUN_KEY] = False

    run_col, reset_col = st.columns([1, 1])
    with run_col:
        if st.button("Run Forecast", key="run_forecast"):
            st.session_state[FORECAST_RUN_KEY] = True
    with reset_col:
        if st.button("Reset Forecast Run", key="reset_forecast_run"):
            st.session_state[FORECAST_RUN_KEY] = False
            st.rerun()

    if not st.session_state[FORECAST_RUN_KEY]:
        st.info("Upload required files, then click Run Forecast.")
        return

    if uploaded["stock"] is None:
        st.error("Stock file is mandatory.")
        return

    if not uploaded["monthly"] and not uploaded["weekly"] and not uploaded["daily"]:
        st.error("At least one sales dataset (monthly / weekly / daily) is required.")
        return

    if uploaded["ns"] is None:
        st.warning("NS file not uploaded. Model will run without NS escalation.")

    try:
        stock_df = extract_stock_columns(read_file(uploaded["stock"]))
        monthly_avg, weekly_avg, daily_avg = _load_sales_averages(uploaded)
        item_master = _build_item_master(uploaded)

        sales_df = calculate_weighted_demand(monthly_avg, weekly_avg, daily_avg)
        ns_metrics = _load_ns_metrics(uploaded)

        final_df = (
            sales_df
            .merge(item_master, on="ITEM_CODE", how="left")
            .merge(stock_df, on="ITEM_CODE", how="left")
            .merge(ns_metrics, on="ITEM_CODE", how="left")
        )

        for text_col in ["ITEM_NAME", "COMPANY", "PACK", "LOCATION", "RACK", "STOCK_PACK"]:
            if text_col not in final_df.columns:
                final_df[text_col] = ""
            final_df[text_col] = final_df[text_col].fillna("").astype(str)

        final_df["PACK"] = _prefer_non_empty(final_df["STOCK_PACK"], final_df["PACK"])
        final_df["RACK"] = _prefer_non_empty(final_df["RACK"], final_df["LOCATION"])

        if "LAST_PURCHASE_DT" not in final_df.columns:
            final_df["LAST_PURCHASE_DT"] = pd.NaT
        final_df["LAST_PURCHASE_DT"] = pd.to_datetime(
            final_df["LAST_PURCHASE_DT"],
            errors="coerce",
        ).dt.normalize()
        final_df["DAYS_SINCE_LAST_PURCHASE"] = (
            pd.Timestamp(date.today()) - final_df["LAST_PURCHASE_DT"]
        ).dt.days
        final_df["DAYS_SINCE_LAST_PURCHASE"] = (
            final_df["DAYS_SINCE_LAST_PURCHASE"]
            .where(final_df["LAST_PURCHASE_DT"].notna(), 0)
            .clip(lower=0)
            .fillna(0)
            .astype(int)
        )
        final_df["LAST_PURCHASE_DT"] = final_df["LAST_PURCHASE_DT"].dt.strftime("%Y-%m-%d").fillna("")

        numeric_fill_cols = [
            "MONTHLY_AVG_QTY",
            "WEEKLY_AVG_QTY",
            "DAILY_AVG_QTY",
            "TRUE_WEEKLY_DEMAND",
            "STOCK_QTY",
            "COST_RATE",
            "NS_ACTIVE_DAYS",
            "NS_CONSECUTIVE_MAX",
            "NS_LINES_AVG",
            "NS_QTY_AVG",
            "NS_RECENT_DAYS",
            "NS_SEVERITY_SCORE",
            "NS_RISK_SCORE",
            "NS_LOSS_ORDER_AMT_30D",
            "NS_FILL_RATE_30D",
            "NS_AFFECTED_PARTIES_30D",
        ]
        for col in numeric_fill_cols:
            if col not in final_df.columns:
                final_df[col] = 0
            final_df[col] = pd.to_numeric(final_df[col], errors="coerce").fillna(0)

        if "NS_TREND" not in final_df.columns:
            final_df["NS_TREND"] = "STABLE"
        final_df["NS_TREND"] = final_df["NS_TREND"].replace(0, "").fillna("")
        final_df["NS_TREND"] = final_df["NS_TREND"].astype(str).str.upper()
        final_df.loc[final_df["NS_TREND"].str.strip() == "", "NS_TREND"] = "STABLE"

        final_df = calculate_order_metrics(final_df)
        final_df = classify_items(final_df)
        final_df["FINAL_ORDER_VALUE"] = final_df["FINAL_ORDER_QTY"] * final_df["COST_RATE"]
        final_df = final_df[FORECAST_OUTPUT_COLUMNS].sort_values(
            "FINAL_ORDER_QTY",
            ascending=False,
        )
    except Exception as exc:
        st.error(f"Forecast run failed: {exc}")
        return

    summary_bundle = _build_summary_bundle(final_df)

    st.header("Final Order Recommendation")
    st.dataframe(final_df, use_container_width=True)

    st.divider()
    _render_summary_dashboard(summary_bundle)

    st.download_button(
        "Download Forecast Excel",
        _to_excel(final_df, summary_bundle),
        file_name=f"pharma_forecast_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_forecast_excel",
    )

