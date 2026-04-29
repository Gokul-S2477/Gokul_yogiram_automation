import re
import streamlit as st
from datetime import date, timedelta, datetime


MONTH_ALIASES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


# ---------- INIT SESSION STATE ----------
def init_session_state():
    if "monthly_data" not in st.session_state:
        st.session_state.monthly_data = {}

    if "weekly_data" not in st.session_state:
        st.session_state.weekly_data = {}

    if "daily_data" not in st.session_state:
        st.session_state.daily_data = {}

    if "ns_file" not in st.session_state:
        st.session_state.ns_file = None

    if "stock_file" not in st.session_state:
        st.session_state.stock_file = None


# ---------- DATE HELPERS ----------
def get_last_n_months(today, n=6):
    months = []
    current = today.replace(day=1)
    for _ in range(n):
        current = (current - timedelta(days=1)).replace(day=1)
        months.append(current.strftime("%b-%Y"))
    return months


def get_last_n_weeks(today, n=6):
    weeks = []
    last_sunday = today - timedelta(days=today.weekday() + 1)
    for _ in range(n):
        start = last_sunday - timedelta(days=6)
        weeks.append(f"{start.strftime('%d %b')} - {last_sunday.strftime('%d %b')}")
        last_sunday = start - timedelta(days=1)
    return weeks


def get_recent_month_options(today, n=12):
    """
    Returns month labels including current month:
    Mar-2026, Feb-2026, Jan-2026, ...
    """
    options = []
    current = today.replace(day=1)
    for _ in range(n):
        options.append(current.strftime("%b-%Y"))
        current = (current - timedelta(days=1)).replace(day=1)
    return options


def _normalize_year(raw_year, default_year):
    if raw_year is None:
        return default_year
    year = int(raw_year)
    if year < 100:
        year += 2000
    return year


def _try_build_date(day, month, year):
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _month_from_token(token):
    cleaned = re.sub(r"[^a-z]", "", token.lower())
    return MONTH_ALIASES.get(cleaned)


def _try_date_from_key(date_key):
    try:
        return date.fromisoformat(str(date_key))
    except ValueError:
        return None


def _safe_date_from_key(date_key):
    """
    Converts stored key (YYYY-MM-DD) to date object.
    Falls back to today's date for unexpected legacy keys.
    """
    parsed = _try_date_from_key(date_key)
    return parsed if parsed is not None else date.today()


def _format_date_with_day(date_obj):
    return f"{date_obj.isoformat()} ({date_obj.strftime('%A')})"


def format_date_key_with_day(date_key):
    parsed = _try_date_from_key(date_key)
    if parsed is None:
        return str(date_key)
    return _format_date_with_day(parsed)


def parse_daily_date_from_filename(filename, default_month, default_year):
    """
    Supports common file names:
    - 1 feb
    - 01 feb
    - 15-feb-2026
    - feb 27
    - 01/02/2026
    Falls back to using selected month + first day number found.
    """
    stem = filename.rsplit(".", 1)[0]
    text = stem.lower()
    text = re.sub(r"[_\.]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Pattern: day month [year] -> 15 feb / 01-feb-26
    match = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s*[- ]?\s*([a-z]{3,9})(?:\s*[- ]?\s*(\d{2,4}))?\b",
        text,
    )
    if match:
        day = int(match.group(1))
        month = _month_from_token(match.group(2))
        year = _normalize_year(match.group(3), default_year)
        if month is not None:
            built = _try_build_date(day, month, year)
            if built is not None:
                return built

    # Pattern: month day [year] -> feb 15 / march-01-2026
    match = re.search(
        r"\b([a-z]{3,9})\s*[- ]?\s*(\d{1,2})(?:st|nd|rd|th)?(?:\s*[- ]?\s*(\d{2,4}))?\b",
        text,
    )
    if match:
        month = _month_from_token(match.group(1))
        day = int(match.group(2))
        year = _normalize_year(match.group(3), default_year)
        if month is not None:
            built = _try_build_date(day, month, year)
            if built is not None:
                return built

    # Pattern: dd/mm[/yy|yyyy]
    match = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = _normalize_year(match.group(3), default_year)
        built = _try_build_date(day, month, year)
        if built is not None:
            return built

    # Fallback: first day-like number in filename + selected month
    match = re.search(r"^\D*(\d{1,2})(?:st|nd|rd|th)?\b", text)
    if match:
        day = int(match.group(1))
        return _try_build_date(day, default_month, default_year)

    return None


# ---------- DISPLAY HELPERS ----------
def show_uploaded_files(
    title,
    data_dict,
    delete_prefix,
    sort_keys=False,
    key_formatter=None,
):
    st.markdown(f"**{title}**")

    if not data_dict:
        st.info("No files uploaded yet.")
        return

    items = list(data_dict.items())
    if sort_keys:
        items = sorted(items, key=lambda x: x[0])

    for key, file in items:
        display_key = key_formatter(key) if key_formatter else key
        col1, col2, col3 = st.columns([3, 4, 1])
        with col1:
            st.write(f"**{display_key}**")
        with col2:
            st.write(file.name)
        with col3:
            if st.button("Remove", key=f"{delete_prefix}_{key}"):
                del data_dict[key]
                st.rerun()


# ---------- UPLOAD UI ----------
def upload_section():
    init_session_state()

    # ---------------- DATE ----------------
    st.header("Step 1: Select Today's Date")
    today = st.date_input("Select today's date", value=date.today())

    st.divider()

    # ---------------- MONTHLY SALES ----------------
    st.subheader("Monthly Sales Upload")
    months = get_last_n_months(today, 6)
    selected_month = st.selectbox("Select Month", months)

    monthly_file = st.file_uploader(
        f"Upload sales file for {selected_month}",
        type=["xlsx", "xls", "csv"],
        key=f"monthly_{selected_month}",
    )

    if monthly_file:
        st.session_state.monthly_data[selected_month] = monthly_file
        st.success(f"Uploaded monthly sales for {selected_month}")

    show_uploaded_files(
        "Uploaded Monthly Files",
        st.session_state.monthly_data,
        "del_month",
    )

    st.divider()

    # ---------------- WEEKLY SALES ----------------
    st.subheader("Weekly Sales Upload")
    weeks = get_last_n_weeks(today, 6)
    selected_week = st.selectbox("Select Week", weeks)

    weekly_file = st.file_uploader(
        f"Upload weekly sales for {selected_week}",
        type=["xlsx", "xls", "csv"],
        key=f"weekly_{selected_week}",
    )

    if weekly_file:
        st.session_state.weekly_data[selected_week] = weekly_file
        st.success(f"Uploaded weekly sales for {selected_week}")

    show_uploaded_files(
        "Uploaded Weekly Files",
        st.session_state.weekly_data,
        "del_week",
    )

    st.divider()

    # ---------------- DAILY SALES (BULK AUTO-DATE) ----------------
    st.subheader("Daily Sales Upload")
    st.caption(
        "Choose month, upload multiple files together, and date will be auto-detected from "
        "file names (examples: 1 feb, 01 feb, 15-feb, feb 27, 01/02/2026)."
    )

    daily_month_options = get_recent_month_options(today, n=12)
    current_month_label = today.replace(day=1).strftime("%b-%Y")
    default_idx = (
        daily_month_options.index(current_month_label)
        if current_month_label in daily_month_options
        else 0
    )

    selected_daily_month = st.selectbox(
        "Select Daily Month",
        daily_month_options,
        index=default_idx,
        key="daily_month_selector",
    )

    month_anchor = datetime.strptime(selected_daily_month, "%b-%Y").date()
    default_month = month_anchor.month
    default_year = month_anchor.year

    daily_files = st.file_uploader(
        f"Upload all daily sales files for {selected_daily_month}",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key=f"daily_bulk_{selected_daily_month}",
    )

    if st.button("Add Daily Files", key=f"add_daily_{selected_daily_month}"):
        if not daily_files:
            st.warning("Please select one or more daily files first.")
        else:
            added_count = 0
            updated_count = 0
            failed_files = []

            for file in daily_files:
                parsed_date = parse_daily_date_from_filename(
                    file.name,
                    default_month=default_month,
                    default_year=default_year,
                )

                if parsed_date is None:
                    failed_files.append(file.name)
                    continue

                date_key = parsed_date.isoformat()
                if date_key in st.session_state.daily_data:
                    updated_count += 1
                else:
                    added_count += 1
                st.session_state.daily_data[date_key] = file

            if added_count or updated_count:
                parts = [f"added {added_count}"]
                if updated_count:
                    parts.append(f"updated {updated_count}")
                st.success(f"Daily uploads processed: {', '.join(parts)}.")

            if failed_files:
                st.error(
                    "Could not detect date from file name for: "
                    + ", ".join(failed_files)
                )

    show_uploaded_files(
        "Uploaded Daily Files",
        st.session_state.daily_data,
        "del_day",
        sort_keys=True,
        key_formatter=format_date_key_with_day,
    )

    if st.session_state.daily_data:
        st.markdown("**Manual Daily Date Correction**")

        daily_items = sorted(st.session_state.daily_data.items(), key=lambda x: x[0])
        option_map = {}
        option_labels = []

        for idx, (mapped_date, file_obj) in enumerate(daily_items, start=1):
            label = f"{idx}. {format_date_key_with_day(mapped_date)} -> {file_obj.name}"
            option_labels.append(label)
            option_map[label] = mapped_date

        selected_mapping = st.selectbox(
            "Select mapped file",
            option_labels,
            key="daily_reassign_select",
        )

        old_date_key = option_map[selected_mapping]
        suggested_date = _safe_date_from_key(old_date_key)

        reassigned_date = st.date_input(
            "Assign to this date",
            value=suggested_date,
            key=f"daily_reassign_date_{old_date_key}",
        )
        st.caption(f"Selected target day: **{reassigned_date.strftime('%A')}**")

        if st.button("Apply Date Correction", key="apply_daily_date_correction"):
            new_date_key = reassigned_date.isoformat()

            if new_date_key == old_date_key:
                st.info("Selected file is already mapped to this date.")
            else:
                selected_file = st.session_state.daily_data.pop(old_date_key)
                replaced_existing = new_date_key in st.session_state.daily_data
                st.session_state.daily_data[new_date_key] = selected_file

                if replaced_existing:
                    st.warning(
                        f"Updated {selected_file.name} to {_format_date_with_day(reassigned_date)}. "
                        "Existing file on that date was replaced."
                    )
                else:
                    st.success(
                        f"Updated {selected_file.name} to {_format_date_with_day(reassigned_date)}."
                    )

                st.rerun()

    st.divider()

    # ---------------- NS REPORT (SINGLE FILE) ----------------
    st.subheader("NS (Not Supplied) Upload")

    ns_file = st.file_uploader(
        "Upload NS Report (with Ord.Date, Item Code, Loss Ord.)",
        type=["xlsx", "xls", "csv"],
        key="ns_file_uploader",
    )

    if ns_file:
        st.session_state.ns_file = ns_file
        st.success(f"Uploaded NS report: {ns_file.name}")

    if st.session_state.ns_file:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(st.session_state.ns_file.name)
        with col2:
            if st.button("Remove NS File"):
                st.session_state.ns_file = None
                st.rerun()

    st.divider()

    # ---------------- STOCK FILE ----------------
    st.subheader("Current Stock Upload")

    stock_file = st.file_uploader(
        "Upload Current Stock File",
        type=["xlsx", "xls", "csv"],
        key="stock_file_uploader",
    )

    if stock_file:
        st.session_state.stock_file = stock_file
        st.success(f"Stock file uploaded: {stock_file.name}")

    if st.session_state.stock_file:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(st.session_state.stock_file.name)
        with col2:
            if st.button("Remove Stock File"):
                st.session_state.stock_file = None
                st.rerun()

    # ---------------- RETURN DATA ----------------
    return {
        "today": today,
        "monthly": st.session_state.monthly_data,
        "weekly": st.session_state.weekly_data,
        "daily": st.session_state.daily_data,
        "ns": st.session_state.ns_file,
        "stock": st.session_state.stock_file,
    }
