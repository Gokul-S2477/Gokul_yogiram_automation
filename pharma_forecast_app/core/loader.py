import pandas as pd
import re

# =========================================================
# FILE READER (CSV / EXCEL)
# =========================================================
def read_file(uploaded_file):
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


# =========================================================
# SALES FILE LOADER
# Handles: Monthly / Weekly / Daily
# =========================================================
def extract_sales_columns(df):
    """
    Expected REAL columns (from your ERP):
    - BARCODE               → Item Code
    - ITEM NAME
    - COMPANY
    - QTY.                  → Quantity
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=["ITEM_CODE", "ITEM_NAME", "COMPANY", "PACK", "LOCATION", "QTY"]
        )

    # Normalize headers
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # -------------------------
    # ITEM CODE (MANDATORY)
    # -------------------------
    item_code_col = None
    for col in df.columns:
        if col in ["BARCODE", "ITEM CODE", "ITEMCODE", "GOLD CODE"]:
            item_code_col = col
            break
        if "ITEM CODE" in col:
            item_code_col = col
            break

    if item_code_col is None:
        raise ValueError(
            f"Sales file error: BARCODE or ITEM CODE column missing. "
            f"Columns found: {list(df.columns)}"
        )

    df["ITEM_CODE"] = df[item_code_col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # -------------------------
    # ITEM NAME (OPTIONAL BUT IMPORTANT)
    # -------------------------
    if "ITEM NAME" in df.columns:
        df["ITEM_NAME"] = df["ITEM NAME"]
    else:
        df["ITEM_NAME"] = ""

    # -------------------------
    # COMPANY (FILTER DC CENTER)
    # -------------------------
    if "COMPANY" in df.columns:
        df["COMPANY"] = df["COMPANY"]
        df = df[df["COMPANY"].str.upper() != "DC CENTER"]
    else:
        df["COMPANY"] = ""

    # -------------------------
    # PACK (OPTIONAL)
    # -------------------------
    if "PACK" in df.columns:
        df["PACK"] = df["PACK"]
    else:
        df["PACK"] = ""

    # -------------------------
    # LOCATION (OPTIONAL)
    # -------------------------
    if "LOCATION" in df.columns:
        df["LOCATION"] = df["LOCATION"]
    else:
        df["LOCATION"] = ""

    # -------------------------
    # QUANTITY (MANDATORY)
    # -------------------------
    qty_col = None
    for c in ["QTY.", "QTY"]:
        if c in df.columns:
            qty_col = c
            break

    if qty_col is None:
        raise ValueError(
            "Sales file error: QTY or QTY. column missing."
        )

    df["QTY"] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)

    return df[["ITEM_CODE", "ITEM_NAME", "COMPANY", "PACK", "LOCATION", "QTY"]]


# =========================================================
# STOCK FILE LOADER
# =========================================================
def extract_stock_columns(df):
    """
    Expected REAL columns:
    - Item Code
    - Qty
    """

    if df is None or df.empty:
        raise ValueError("Stock file is empty or not loaded")

    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # -------------------------
    # ITEM CODE
    # -------------------------
    item_col = None
    for c in ["ITEM CODE", "GOLD CODE"]:
        if c in df.columns:
            item_col = c
            break

    if item_col is None:
        raise ValueError(
            "Stock file error: Item Code / Gold Code column missing."
        )

    df["ITEM_CODE"] = df[item_col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # -------------------------
    # STOCK QTY
    # -------------------------
    if "QTY" not in df.columns:
        raise ValueError("Stock file error: Qty column missing")

    df["STOCK_QTY"] = pd.to_numeric(df["QTY"], errors="coerce").fillna(0)

    # -------------------------
    # RACK (OPTIONAL)
    # -------------------------
    if "RACK" in df.columns:
        df["RACK"] = df["RACK"]
    else:
        df["RACK"] = ""

    # -------------------------
    # COST RATE (OPTIONAL; FALLBACK TO COST)
    # -------------------------
    cost_rate_col = None
    for c in ["COSTRATE", "COST RATE", "COST"]:
        if c in df.columns:
            cost_rate_col = c
            break
    if cost_rate_col is not None:
        df["COST_RATE"] = pd.to_numeric(df[cost_rate_col], errors="coerce").fillna(0)
    else:
        df["COST_RATE"] = 0.0

    # -------------------------
    # LAST PURCHASE DATE (OPTIONAL)
    # -------------------------
    last_purchase_col = None
    for c in ["LAST PURCHASE DT.", "LAST PURCHASE DT", "LAST PURCHASE DATE"]:
        if c in df.columns:
            last_purchase_col = c
            break

    if last_purchase_col is not None:
        df["LAST_PURCHASE_DT"] = pd.to_datetime(
            df[last_purchase_col],
            dayfirst=True,
            errors="coerce"
        ).dt.normalize()
    else:
        df["LAST_PURCHASE_DT"] = pd.NaT

    # -------------------------
    # STOCK PACK (OPTIONAL)
    # -------------------------
    if "PACK" in df.columns:
        df["STOCK_PACK"] = df["PACK"]
    else:
        df["STOCK_PACK"] = ""

    return df[
        [
            "ITEM_CODE",
            "STOCK_QTY",
            "RACK",
            "COST_RATE",
            "LAST_PURCHASE_DT",
            "STOCK_PACK",
        ]
    ]


# =========================================================
# NS (NOT SUPPLIED) FILE LOADER — MOST CRITICAL
# =========================================================
def extract_ns_columns(df):
    import pandas as pd
    import re

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "ITEM_CODE",
                "NS_DATE",
                "NS_QTY",
                "NS_LINES",
                "NS_ORD_QTY",
                "NS_ISS_QTY",
                "NS_LOSS_ORDER_AMT",
                "NS_PARTY_CODE",
            ]
        )

    # Normalize headers VERY aggressively
    df = df.copy()
    df.columns = (
        df.columns
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.upper()
    )

    # -------------------------------------------------
    # FLEXIBLE ITEM CODE DETECTION (CRITICAL FIX)
    # -------------------------------------------------
    item_code_col = None
    for col in df.columns:
        if col in ["ITEM CODE", "ITEMCODE"]:
            item_code_col = col
            break
        if "ITEM CODE" in col:
            item_code_col = col
            break
        if col.startswith("MDM"):
            item_code_col = col
            break

    if item_code_col is None:
        raise ValueError(
            f"NS file error: Unable to detect Item Code column. "
            f"Columns found: {list(df.columns)}"
        )

    df["ITEM_CODE"] = df[item_code_col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

    # -------------------------------------------------
    # LOSS ORDER QTY
    # -------------------------------------------------
    loss_col = None
    for col in df.columns:
        if "LOSS ORD" in col:
            loss_col = col
            break

    if loss_col is None:
        raise ValueError("NS file error: Loss Ord. column missing.")

    df["NS_QTY"] = pd.to_numeric(df[loss_col], errors="coerce").fillna(0)

    # -------------------------------------------------
    # ORDER QTY / ISSUE QTY / LOSS AMT (OPTIONAL METRICS)
    # -------------------------------------------------
    ord_qty_col = None
    iss_qty_col = None
    loss_amt_col = None
    party_code_col = None

    for col in df.columns:
        if ("ORD.QTY" in col or "ORD QTY" in col) and "LOSS ORD" not in col:
            ord_qty_col = col
            break

    for col in df.columns:
        if "ISS.QTY" in col or "ISS QTY" in col:
            iss_qty_col = col
            break

    for col in df.columns:
        if "LOSS ORDER AMT" in col:
            loss_amt_col = col
            break

    if "PARTY CODE" in df.columns:
        party_code_col = "PARTY CODE"

    df["NS_ORD_QTY"] = (
        pd.to_numeric(df[ord_qty_col], errors="coerce").fillna(0)
        if ord_qty_col is not None
        else 0
    )
    df["NS_ISS_QTY"] = (
        pd.to_numeric(df[iss_qty_col], errors="coerce").fillna(0)
        if iss_qty_col is not None
        else 0
    )
    df["NS_LOSS_ORDER_AMT"] = (
        pd.to_numeric(df[loss_amt_col], errors="coerce").fillna(0)
        if loss_amt_col is not None
        else 0
    )
    df["NS_PARTY_CODE"] = (
        df[party_code_col].astype(str).fillna("")
        if party_code_col is not None
        else ""
    )

    # -------------------------------------------------
    # ORDER DATE (ROBUST)
    # -------------------------------------------------
    date_col = None
    for col in df.columns:
        if "ORD.DATE" in col or "ORDER DATE" in col:
            date_col = col
            break

    if date_col is None:
        raise ValueError("NS file error: Ord.Date column missing.")

    def parse_date(val):
        if pd.isna(val):
            return None
        if isinstance(val, pd.Timestamp):
            return val.normalize()

        s = str(val)
        m = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", s)
        if not m:
            return None

        return pd.to_datetime(
            m.group(1),
            dayfirst=True,
            errors="coerce"
        )

    df["NS_DATE"] = df[date_col].apply(parse_date)
    df = df.dropna(subset=["NS_DATE"])
    df["NS_DATE"] = df["NS_DATE"].dt.normalize()

    # -------------------------------------------------
    # NS LINES = NUMBER OF SHOPS
    # -------------------------------------------------
    df["NS_LINES"] = 1

    return df[
        [
            "ITEM_CODE",
            "NS_DATE",
            "NS_QTY",
            "NS_LINES",
            "NS_ORD_QTY",
            "NS_ISS_QTY",
            "NS_LOSS_ORDER_AMT",
            "NS_PARTY_CODE",
        ]
    ]
