def classify_items(df):
    """
    FINAL CLASSIFICATION LOGIC (PHARMA SAFE)

    Uses:
    - TRUE_WEEKLY_DEMAND (corrected model)
    - Stock vs weekly need
    - Activity detection
    - Human-readable order reason
    """

    df = df.copy()

    # -------------------------------------------------
    # STOCK STATUS
    # -------------------------------------------------
    df["STOCK_STATUS"] = "OK"

    # No stock
    df.loc[df["STOCK_QTY"] <= 0, "STOCK_STATUS"] = "CRITICAL"

    # Excess stock (more than 4 weeks cover)
    df.loc[
        df["STOCK_QTY"] > df["TRUE_WEEKLY_DEMAND"] * 4,
        "STOCK_STATUS"
    ] = "EXCESS"

    # -------------------------------------------------
    # ITEM STATUS
    # -------------------------------------------------
    df["ITEM_STATUS"] = "ACTIVE"

    # No movement at all
    df.loc[
        (df["DAILY_AVG_QTY"] == 0) &
        (df["WEEKLY_AVG_QTY"] == 0) &
        (df["MONTHLY_AVG_QTY"] == 0),
        "ITEM_STATUS"
    ] = "DORMANT"

    # -------------------------------------------------
    # ORDER REASON (EXPLAINABLE)
    # -------------------------------------------------
    reasons = []

    for _, r in df.iterrows():
        reason = []

        if r["STOCK_QTY"] <= 0:
            reason.append("Zero stock")

        if r["NS_CONSECUTIVE_MAX"] >= 5:
            reason.append(f"NS for {int(r['NS_CONSECUTIVE_MAX'])} consecutive days")

        if r["NS_LINES_AVG"] >= 5:
            reason.append("High shop demand (NS lines)")

        if r["NS_TREND"] == "INCREASING":
            reason.append("NS trend increasing")

        if r["DAYS_OF_COVER"] < 3:
            reason.append("Low days of cover")

        if not reason:
            reason.append("Routine weekly replenishment")

        reasons.append(" + ".join(reason))

    df["ORDER_REASON"] = reasons

    return df
