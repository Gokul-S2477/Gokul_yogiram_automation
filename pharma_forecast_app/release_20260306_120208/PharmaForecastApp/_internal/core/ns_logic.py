import pandas as pd
import numpy as np


def calculate_ns_metrics(ns_df, lookback_days=30):
    """
    Robust NS intelligence.
    GUARANTEES:
    - ITEM_CODE handled as string
    - No mixed-type index operations
    - No pandas auto-sorting failures
    """

    # ------------------------------
    # SAFETY: EMPTY INPUT
    # ------------------------------
    if ns_df is None or ns_df.empty:
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

    df = ns_df.copy()

    # 🔒 CRITICAL FIX: FORCE ITEM_CODE TO STRING
    df["ITEM_CODE"] = df["ITEM_CODE"].astype(str)

    # Ensure optional numeric fields always exist
    for col in ["NS_ORD_QTY", "NS_ISS_QTY", "NS_LOSS_ORDER_AMT"]:
        if col not in df.columns:
            df[col] = 0

    if "NS_PARTY_CODE" not in df.columns:
        df["NS_PARTY_CODE"] = ""

    # ------------------------------
    # LOOKBACK WINDOW
    # ------------------------------
    max_date = df["NS_DATE"].max()
    cutoff = max_date - pd.Timedelta(days=lookback_days)
    df = df[df["NS_DATE"] >= cutoff]

    # ------------------------------
    # DAILY AGGREGATION
    # ------------------------------
    daily = (
        df
        .groupby(["ITEM_CODE", "NS_DATE"], as_index=False)
        .agg(
            DAILY_LINES=("NS_LINES", "sum"),
            DAILY_QTY=("NS_QTY", "sum")
        )
        .sort_values(["ITEM_CODE", "NS_DATE"])
    )

    # ------------------------------
    # ACTIVE DAYS
    # ------------------------------
    active_days = (
        daily.groupby("ITEM_CODE")["NS_DATE"]
        .nunique()
        .rename("NS_ACTIVE_DAYS")
    )

    # ------------------------------
    # CONSECUTIVE DAYS
    # ------------------------------
    daily["DAY_DIFF"] = (
        daily.groupby("ITEM_CODE")["NS_DATE"]
        .diff()
        .dt.days
    )

    daily["BREAK"] = (daily["DAY_DIFF"] != 1).cumsum()

    consecutive = (
        daily
        .groupby(["ITEM_CODE", "BREAK"])
        .size()
        .groupby("ITEM_CODE")
        .max()
        .rename("NS_CONSECUTIVE_MAX")
    )

    # ------------------------------
    # AVERAGES
    # ------------------------------
    avg_lines = (
        daily.groupby("ITEM_CODE")["DAILY_LINES"]
        .mean()
        .rename("NS_LINES_AVG")
    )

    avg_qty = (
        daily.groupby("ITEM_CODE")["DAILY_QTY"]
        .mean()
        .rename("NS_QTY_AVG")
    )

    # ------------------------------
    # RECENT DAYS (LAST 7)
    # ------------------------------
    recent_cutoff = max_date - pd.Timedelta(days=7)

    recent_days = (
        daily[daily["NS_DATE"] >= recent_cutoff]
        .groupby("ITEM_CODE")["NS_DATE"]
        .nunique()
        .rename("NS_RECENT_DAYS")
    )

    # ------------------------------
    # TREND (SAFE IMPLEMENTATION)
    # ------------------------------
    mid_date = cutoff + (max_date - cutoff) / 2

    early = (
        daily[daily["NS_DATE"] <= mid_date]
        .groupby("ITEM_CODE")["DAILY_LINES"]
        .mean()
    )

    late = (
        daily[daily["NS_DATE"] > mid_date]
        .groupby("ITEM_CODE")["DAILY_LINES"]
        .mean()
    )

    # 🔒 CRITICAL FIX: ALIGN WITHOUT SORTING
    trend_df = pd.concat(
        [early.rename("EARLY"), late.rename("LATE")],
        axis=1
    ).fillna(0)

    def trend_label(row):
        if row["LATE"] > row["EARLY"] * 1.2:
            return "INCREASING"
        elif row["LATE"] < row["EARLY"] * 0.8:
            return "DECREASING"
        else:
            return "STABLE"

    trend = trend_df.apply(trend_label, axis=1).rename("NS_TREND")

    # ------------------------------
    # SEVERITY SCORE
    # ------------------------------
    severity = (
        avg_lines * 1.5 +
        (avg_qty / (avg_qty.median() + 1))
    ).rename("NS_SEVERITY_SCORE")

    # ------------------------------
    # RISK SCORE (CONSERVATIVE)
    # ------------------------------
    risk = (
        active_days * 0.4 +
        consecutive * 0.6 +
        recent_days * 0.5 +
        severity * 0.8
    ).rename("NS_RISK_SCORE")

    # ------------------------------
    # NEW BUSINESS METRICS (30D)
    # ------------------------------
    loss_amt_30d = (
        df.groupby("ITEM_CODE")["NS_LOSS_ORDER_AMT"]
        .sum()
        .rename("NS_LOSS_ORDER_AMT_30D")
    )

    ord_qty_30d = df.groupby("ITEM_CODE")["NS_ORD_QTY"].sum()
    iss_qty_30d = df.groupby("ITEM_CODE")["NS_ISS_QTY"].sum()
    fill_rate_30d = (
        iss_qty_30d
        .div(ord_qty_30d.replace(0, np.nan))
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .rename("NS_FILL_RATE_30D")
    )

    party_codes = (
        df["NS_PARTY_CODE"]
        .astype(str)
        .str.strip()
        .replace({"nan": "", "None": ""})
    )
    affected_parties_30d = (
        df.assign(_PARTY_CLEAN=party_codes)
        .loc[lambda x: x["_PARTY_CLEAN"] != ""]
        .groupby("ITEM_CODE")["_PARTY_CLEAN"]
        .nunique()
        .rename("NS_AFFECTED_PARTIES_30D")
    )

    # ------------------------------
    # FINAL MERGE (NO SORTING)
    # ------------------------------
    result = pd.concat(
        [
            active_days,
            consecutive,
            avg_lines,
            avg_qty,
            recent_days,
            trend,
            severity,
            risk,
            loss_amt_30d,
            fill_rate_30d,
            affected_parties_30d,
        ],
        axis=1
    ).reset_index()

    # Fill & cast
    result = result.fillna(0)
    result["NS_ACTIVE_DAYS"] = result["NS_ACTIVE_DAYS"].astype(int)
    result["NS_CONSECUTIVE_MAX"] = result["NS_CONSECUTIVE_MAX"].astype(int)
    result["NS_RECENT_DAYS"] = result["NS_RECENT_DAYS"].astype(int)
    result["NS_AFFECTED_PARTIES_30D"] = result["NS_AFFECTED_PARTIES_30D"].astype(int)

    return result
