from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

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


def _render_bar_chart(df, label_col, value_col, title):
    st.markdown(f"**{title}**")
    if df.empty:
        st.info("No data available.")
        return
    chart_df = df.set_index(label_col)[[value_col]]
    st.bar_chart(chart_df, width='stretch')


def _render_summary_dashboard(bundle):
    st.header("Summary and Insights")
    st.markdown("**Executive Summary**")
    for line in bundle["summary_lines"]:
        st.write(f"- {line}")

    kpis = bundle["kpis"]
    kpi_row_1 = st.columns(4)
    kpi_row_2 = st.columns(4)

    kpi_row_1[0].metric("Total Items", _fmt_number(kpis["total_items"]))
    kpi_row_1[1].metric("Items To Order", _fmt_number(kpis["items_to_order"]))
    kpi_row_1[2].metric("Critical Stock", _fmt_number(kpis["critical_stock_items"]))
    kpi_row_1[3].metric("Low Cover (<3D)", _fmt_number(kpis["low_cover_items"]))

    kpi_row_2[0].metric("Order Qty", _fmt_number(kpis["total_order_qty"], 2))
    kpi_row_2[1].metric("Order Value", _fmt_amount(kpis["total_order_value"]))
    kpi_row_2[2].metric("Avg Cover Days", _fmt_number(kpis["avg_days_cover"], 2))
    kpi_row_2[3].metric("Avg Fill Rate 30D", f"{_fmt_number(kpis['avg_fill_rate_30d'] * 100, 2)}%")

    st.subheader("Charts")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        _render_bar_chart(
            bundle["top_companies_value"],
            "COMPANY",
            "ORDER_VALUE",
            "Top Companies To Order By Value",
        )
    with r1c2:
        _render_bar_chart(
            bundle["top_companies_qty"],
            "COMPANY",
            "ORDER_QTY",
            "Top Companies To Order By Quantity",
        )

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        _render_bar_chart(
            bundle["stock_status_dist"],
            "STOCK_STATUS",
            "COUNT",
            "Stock Status Distribution",
        )
    with r2c2:
        _render_bar_chart(
            bundle["item_status_dist"],
            "ITEM_STATUS",
            "COUNT",
            "Item Status Distribution",
        )

    _render_bar_chart(
        bundle["cover_bucket_dist"],
        "COVER_BUCKET",
        "COUNT",
        "Days Of Cover Bucket Distribution",
    )


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
    st.dataframe(final_df, width='stretch')

    st.divider()
    _render_summary_dashboard(summary_bundle)

    st.download_button(
        "Download Forecast Excel",
        _to_excel(final_df, summary_bundle),
        file_name=f"pharma_forecast_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_forecast_excel",
    )

