import pandas as pd
import numpy as np
from datetime import timedelta


# =========================================================
# AGGREGATE SALES (MONTHLY / WEEKLY / DAILY)
# =========================================================
def aggregate_sales(file_dict, read_func, extract_func):
    """
    Combines multiple sales files of the same granularity
    (monthly OR weekly OR daily).

    Output:
    ITEM_CODE | TOTAL_QTY
    """

    frames = []

    for f in file_dict.values():
        raw = read_func(f)
        clean = extract_func(raw)
        frames.append(clean)

    if not frames:
        return pd.DataFrame(columns=["ITEM_CODE", "QTY"])

    combined = pd.concat(frames, ignore_index=True)

    return (
        combined
        .groupby("ITEM_CODE", as_index=False)["QTY"]
        .sum()
    )


# =========================================================
# CALCULATE AVERAGE WITH MISSING-DAY CORRECTION
# =========================================================
def calculate_average(total_df, periods, level):
    """
    periods = number of files uploaded
    level   = 'MONTHLY' | 'WEEKLY' | 'DAILY'
    """

    df = total_df.copy()

    if df.empty:
        df["AVG_QTY"] = 0
        return df[["ITEM_CODE", "AVG_QTY"]]

    # Base average
    df["AVG_QTY"] = df["QTY"] / max(periods, 1)

    # -----------------------------------------------------
    # DAILY-SPECIFIC ADJUSTMENT
    # -----------------------------------------------------
    if level == "DAILY":
        # Daily files usually miss Sundays / holidays
        # Conservative correction: assume 6 working days/week
        df["AVG_QTY"] = df["AVG_QTY"] * (7 / 6)

    return df[["ITEM_CODE", "AVG_QTY"]]


# =========================================================
# TRUE WEEKLY DEMAND ENGINE (WEEKLY-ANCHORED)
# =========================================================
def calculate_weighted_demand(monthly_df, weekly_df, daily_df, ns_df=None):
    """
    Calculates TRUE_WEEKLY_DEMAND using:
    - Weekly avg as base anchor
    - Daily avg as controlled uplift
    - Monthly avg as fallback support
    - Recent activity gate to avoid dormant inflation

    No existing column removed.
    """

    base = pd.DataFrame()

    for df in [monthly_df, weekly_df, daily_df]:
        if df is not None and not df.empty:
            base = (
                df[["ITEM_CODE"]]
                if base.empty
                else base.merge(df[["ITEM_CODE"]], on="ITEM_CODE", how="outer")
            )


    if base.empty:
        return pd.DataFrame(
            columns=[
                "ITEM_CODE",
                "MONTHLY_AVG_QTY",
                "WEEKLY_AVG_QTY",
                "DAILY_AVG_QTY",
                "TRUE_WEEKLY_DEMAND"
            ]
        )

    def attach(df, col):
        return df.rename(columns={"AVG_QTY": col}) if df is not None else None

    # Attach averages
    base = base.merge(
        attach(monthly_df, "MONTHLY_AVG_QTY"),
        on="ITEM_CODE", how="left"
    ) if monthly_df is not None else base.assign(MONTHLY_AVG_QTY=0)

    base = base.merge(
        attach(weekly_df, "WEEKLY_AVG_QTY"),
        on="ITEM_CODE", how="left"
    ) if weekly_df is not None else base.assign(WEEKLY_AVG_QTY=0)

    base = base.merge(
        attach(daily_df, "DAILY_AVG_QTY"),
        on="ITEM_CODE", how="left"
    ) if daily_df is not None else base.assign(DAILY_AVG_QTY=0)

    base = base.fillna(0)

    # -----------------------------------------------------
    # WEEKLY EQUIVALENTS
    # -----------------------------------------------------
    base["MONTHLY_WEEK_EQ"] = base["MONTHLY_AVG_QTY"] / 4.33
    base["DAILY_WEEK_EQ"] = base["DAILY_AVG_QTY"] * 6

    # -----------------------------------------------------
    # RECENT ACTIVITY GATE
    # -----------------------------------------------------
    if ns_df is not None and "NS_ACTIVE_DAYS" in ns_df.columns:
        base = base.merge(
            ns_df[["ITEM_CODE", "NS_ACTIVE_DAYS"]],
            on="ITEM_CODE", how="left"
        )
        base["NS_ACTIVE_DAYS"] = base["NS_ACTIVE_DAYS"].fillna(0)
    else:
        base["NS_ACTIVE_DAYS"] = 0

    base["RECENT_ACTIVITY"] = (
        (base["WEEKLY_AVG_QTY"] > 0) |
        (base["DAILY_AVG_QTY"] > 0) |
        (base["NS_ACTIVE_DAYS"] > 0)
    )

    # -----------------------------------------------------
    # BASE = WEEKLY AVG
    # -----------------------------------------------------
    base["TRUE_WEEKLY_DEMAND"] = base["WEEKLY_AVG_QTY"]

    # -----------------------------------------------------
    # DAILY TREND UPLIFT (CONTROLLED)
    # -----------------------------------------------------
    daily_uplift = (
        (base["DAILY_WEEK_EQ"] - base["WEEKLY_AVG_QTY"])
        .clip(lower=0) * 0.50
    )

    base["TRUE_WEEKLY_DEMAND"] += daily_uplift

    # -----------------------------------------------------
    # MONTHLY SUPPORT (ONLY IF WEEKLY IS WEAK)
    # -----------------------------------------------------
    monthly_support = np.where(
        base["WEEKLY_AVG_QTY"] < (0.5 * base["MONTHLY_WEEK_EQ"]),
        base["MONTHLY_WEEK_EQ"] * 0.30,
        0
    )

    base["TRUE_WEEKLY_DEMAND"] += monthly_support

    # -----------------------------------------------------
    # APPLY RECENT ACTIVITY GATE
    # -----------------------------------------------------
    base.loc[~base["RECENT_ACTIVITY"], "TRUE_WEEKLY_DEMAND"] = 0

    # -----------------------------------------------------
    # HARD CAP (ANTI-EXPLOSION)
    # -----------------------------------------------------
    base["TRUE_WEEKLY_DEMAND"] = np.minimum(
        base["TRUE_WEEKLY_DEMAND"],
        np.maximum(
            base["WEEKLY_AVG_QTY"] * 1.5,
            base["MONTHLY_WEEK_EQ"]
        )
    )

    return base[
        [
            "ITEM_CODE",
            "MONTHLY_AVG_QTY",
            "WEEKLY_AVG_QTY",
            "DAILY_AVG_QTY",
            "TRUE_WEEKLY_DEMAND"
        ]
    ]


# =========================================================
# HOLIDAY / NO-SALE INFERENCE (OPTIONAL EXTENSION HOOK)
# =========================================================
def infer_holiday_adjustment(sales_dates):
    """
    Placeholder for future enhancement:
    Detect missing dates → infer holidays → shift demand.

    Currently returns neutral factor (1.0)
    """
    return 1.0
