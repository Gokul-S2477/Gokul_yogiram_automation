import numpy as np

def calculate_order_metrics(df):
    df = df.copy()

    # -----------------------------
    # DAILY DEMAND & COVER
    # -----------------------------
    df["DAILY_DEMAND"] = df["DAILY_AVG_QTY"].replace(0, np.nan)
    df["DAYS_OF_COVER"] = (
        df["STOCK_QTY"] / df["DAILY_DEMAND"]
    ).replace([np.inf, -np.inf], 0).fillna(0)

    # -----------------------------
    # BASE SAFETY (REDUCED)
    # -----------------------------
    df["SAFETY_PCT"] = 0.20  # 20% base

    # -----------------------------
    # NS ESCALATION (REDUCED WEIGHTS)
    # -----------------------------
    df.loc[df["NS_CONSECUTIVE_MAX"] >= 5, "SAFETY_PCT"] += 0.12
    df.loc[df["NS_LINES_AVG"] >= 5, "SAFETY_PCT"] += 0.08
    df.loc[df["NS_TREND"] == "INCREASING", "SAFETY_PCT"] += 0.05
    df.loc[df["DAYS_OF_COVER"] < 3, "SAFETY_PCT"] += 0.05

    if "NS_RECENT_DAYS" in df.columns:
        df.loc[df["NS_RECENT_DAYS"] >= 3, "SAFETY_PCT"] += 0.10

    # -----------------------------
    # SOFT CAP (NEW)
    # -----------------------------
    df["SAFETY_PCT"] = df["SAFETY_PCT"].clip(upper=0.60)

    # -----------------------------
    # SAFETY STOCK
    # -----------------------------
    df["SAFETY_STOCK"] = df["TRUE_WEEKLY_DEMAND"] * df["SAFETY_PCT"]

    # -----------------------------
    # HARD CAP (ABSOLUTE)
    # -----------------------------
    df["SAFETY_STOCK"] = np.minimum(
        df["SAFETY_STOCK"],
        df["TRUE_WEEKLY_DEMAND"]
    )

    # -----------------------------
    # FINAL ORDER
    # -----------------------------
    df["EFFECTIVE_REQUIREMENT"] = (
        df["TRUE_WEEKLY_DEMAND"] + df["SAFETY_STOCK"]
    )

    df["FINAL_ORDER_QTY"] = (
        df["EFFECTIVE_REQUIREMENT"] - df["STOCK_QTY"]
    ).clip(lower=0)

    df["MIN_ORDER_QTY"] = df["FINAL_ORDER_QTY"] * 0.90
    df["MAX_ORDER_QTY"] = df["FINAL_ORDER_QTY"] * 1.10

    return df
