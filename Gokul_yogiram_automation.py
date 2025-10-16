import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import os


# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Yogiram Automation - Gokul",
    page_icon="⚙️",
    layout="wide",  # force wide layout
    initial_sidebar_state="collapsed"
)

# ------------------ LOGIN ------------------
# Easy-to-add users system
users = {
    "admin": "1234",
    "gokul": "abcd",
    "vel":"1234",
    "yogiram":"yogiram",
    "siva":"1234",
    "rajan":"1234"
}

# Path to the login log file
LOGIN_LOG_FILE = "login_logs.csv"

def log_login(username):
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([[username, log_time]], columns=["Username", "LoginTime"])
    if os.path.exists(LOGIN_LOG_FILE):
        new_entry.to_csv(LOGIN_LOG_FILE, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(LOGIN_LOG_FILE, index=False)

st.title("🔐 Login to Yogiram Automation")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.button("Login"):
    if username in users and password == users[username]:
        st.session_state.logged_in = True
        st.success(f"Login successful! Welcome {username}")
        log_login(username)
    else:
        st.error("Invalid username or password")

# Stop the rest of the app if not logged in
if not st.session_state.logged_in:
    st.stop()


# ------------------ CUSTOM CSS ------------------
st.set_page_config(page_title="Yogiram Automation", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
/* ---------------- BODY & BACKGROUND ---------------- */
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    font-family: 'Poppins', sans-serif;
    color: #f1f1f1;
    margin: 0;
    padding: 0;
}

/* ---------------- STREAMLIT MAIN CONTAINER ---------------- */
.css-1d391kg {
    max-width: 1000px !important;
    width: 100% !important;
    margin: 20px auto !important;
    padding: 30px 40px !important;
    min-height: 900px;
}

/* ---------------- LOGIN & MODULES VERTICAL ALIGN ---------------- */
.stTextInput > div, 
.stButton > div, 
.stFileUploader>div,
.stDataFrame div[data-testid="stDataFrameContainer"] {
    width: 100% !important;
    max-width: 500px;
    min-width: 500px;
    margin: 10px 0 !important;  /* stack vertically */
    display: block !important;
}

/* ---------------- HEADINGS ---------------- */
h1 {
    font-size: 48px;
    text-align: center;
    color: #00ffd5;
    margin-bottom: 20px;
}
h2, h3 {
    color: #b0eaff;
    text-align: center;
}

/* ---------------- BUTTONS ---------------- */
.stButton > button {
    width: 100% !important;
    max-width: 500px;
    min-width: 500px;
    display: block !important;
    margin: 10px 0 !important;
    background: rgba(255,255,255,0.08);
    color: #00ffd5;
    font-weight: 600;
    font-size: 18px;
    border-radius: 12px;
    padding: 12px 0;
    border: 2px solid #00ffd5;
    box-shadow: 0 0 10px rgba(0,255,213,0.3);
}

/* ---------------- TEXT INPUTS ---------------- */
.stTextInput > div > div > input {
    width: 100% !important;
    max-width: 500px;
    min-width: 500px;
    display: block !important;
    padding: 12px 15px;
    font-size: 16px;
}

/* ---------------- FILE UPLOADER ---------------- */
.stFileUploader>div>div {
    padding: 18px;
    background: rgba(255,255,255,0.05);
    color: #e0e0e0;
    border: 2px dashed #00ffd5aa;
    border-radius: 15px;
}

/* ---------------- TABLES ---------------- */
.stDataFrame th {
    background: linear-gradient(90deg, #00c2ff, #00ffd5);
    color: #000;
    font-weight: bold;
    text-align: center;
}
.stDataFrame td {
    background: rgba(255,255,255,0.04);
    color: #fff;
}
.stDataFrame div[data-testid="stDataFrameContainer"] {
    margin-bottom: 30px;
    border-radius: 15px;
}

/* ---------------- FOOTER ---------------- */
footer {
    text-align: center;
    padding: 10px;
    background: rgba(0,0,0,0.3);
    color: #ccc;
    font-size: 14px;
    border-top: 1px solid rgba(255,255,255,0.2);
}
</style>

""", unsafe_allow_html=True)




# ------------------ NAVIGATION ------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home(): st.session_state.page = "home"
def go_claim(): st.session_state.page = "claim"
def go_maxmin(): st.session_state.page = "maxmin"
def go_sales(): st.session_state.page = "sales"
def go_admin_log(): st.session_state.page = "admin_log"
def go_apollo():   # <-- New function for Apollo Check
    st.session_state.page = "apollo"
def go_pending_indents():
    st.session_state.page = "pending_indents"
def go_na_finder():
    st.session_state.page = "na_finder"
def go_info():
    st.session_state.page = "info"
def go_payment_due():
    st.session_state.page = "payment_due"






# ------------------ HOME PAGE ------------------
if st.session_state.page == "home":
    st.markdown("<h1>⚙️ Yogiram Automation System</h1>", unsafe_allow_html=True)
    st.markdown("<h2>Welcome to the Automation Portal</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Choose an automation to run 👇")

    # Vertical buttons
    if st.button("ℹ️ Info Portal"):
        go_info()

    if st.button("📂 Claim Portal"):
        go_claim()
    if st.button("📊 Max/Min Value Portal"):
        go_maxmin()
    if st.button("💰 Sales Portal"):
        go_sales()
    if username == "admin" and st.button("📝 Login Activity"):
        go_admin_log()
    if st.button("🛒 Apollo Check Portal"):
        go_apollo()
    if st.button("📦 Pending Indents Check"):
        go_pending_indents()
    if st.button("🧾 NA Finder"):
        go_na_finder()
    if st.button("📊 DB Age Analysis Portal"):
        st.session_state.page = "db_age"
    if st.button("💳 Payment Due Tracker"):
        go_payment_due()




    st.markdown("---")
    st.markdown("""
        <footer>
            Created by <b>Gokul</b> — Data Analyst, <b>Yogiram</b>
        </footer>
    """, unsafe_allow_html=True)


# ------------------ INFO MODULE ------------------
elif st.session_state.page == "info":
    st.title("ℹ️ Info & Instructions Portal")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"

    st.markdown("""
    ### Claim Report - Invalid Free Qty Issued
    - Upload the claim report file downloaded from your system.
    - Ensure columns like 'Company Name', 'Claim Amount', 'Free Qty' exist.
    - Click 🚀 Process Data to generate summary of invalid free quantities issued.

    ### Pending Indent Module - NS %
    - Upload Pending Indents file and Order Details file.
    - Make sure columns like 'Ind.No.', 'Ordered Items', 'Invoice Items' exist.
    - Click 🚀 Map & Aggregate Data to calculate NS % and fulfillment summary.

    ### Statement with Indent No / Time Analysis Report
    - Upload the relevant Excel/CSV report exported from the system.
    - Columns like 'Indent No', 'Date', 'Time' should be present.
    - Click 🚀 Process Data to analyze indent timelines and time-based trends.

    ### NS Report - NA Report / Current Status
    - Upload NA/NS related data file.
    - Columns must include 'Gold Code', 'Qty', 'NA', 'NA VALUE'.
    - Click 🚀 Process & Merge Qty to get current NA/NS status report by company or SKU.

    ### DB AGE - Supplier Claim Pending Report
    - Upload supplier DB/claim pending file.
    - Columns must include 'Supplier', 'DB Date', 'Pending Amount', etc.
    - Select today or custom date to calculate DB age and generate summary report.

    ---
    **Tips for All Modules:**
    - Always verify column names before uploading.
    - Export files in Excel/CSV format from your source system.
    - Check info section for each module for more details.
    - You can paste additional instructions or software download links here.
    """)


# ------------------ PAYMENT DUE TRACKER ------------------
elif st.session_state.page == "payment_due":

    import pandas as pd
    import streamlit as st
    import os
    from datetime import datetime, timedelta
    from io import BytesIO

    st.title("💳 Payment Due Tracker")

    if st.button("🏠 Back to Home"):
        go_home()

    # ------------------ Load Vendor Master ------------------
    try:
        vendor_master = pd.read_csv("vendor_master.csv")
        required_vendor_cols = ["Vendor Code", "branch", "Name", "PAN", "Mobile", "Email", "Payment Term"]
        for col in required_vendor_cols:
            if col not in vendor_master.columns:
                st.error(f"⚠️ Missing column '{col}' in vendor_master.csv")
                st.stop()
    except FileNotFoundError:
        st.error("⚠️ 'vendor_master.csv' file not found in directory!")
        st.stop()

    # ------------------ Branch Selection ------------------
    branch_list = sorted(vendor_master["branch"].dropna().unique())
    branch = st.selectbox("🏢 Select Branch", branch_list)

    # ------------------ Upload Bill File ------------------
    uploaded_file = st.file_uploader("📤 Upload Bill Statement (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        vendor_master.columns = vendor_master.columns.str.strip().str.lower()

        required_cols = ["party code", "bill. date", "bill amt.", "party name"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"⚠️ Uploaded file must include column '{col}'")
                st.stop()

        # ------------------ Merge Data ------------------
        merged = pd.merge(df, vendor_master, how="left",
                          left_on="party code", right_on="vendor code")

        merged = merged[merged["branch"] == branch]

        merged["bill. date"] = pd.to_datetime(merged["bill. date"], errors="coerce")
        merged["payment term"] = pd.to_numeric(merged["payment term"], errors="coerce").fillna(0)
        merged["payment due date"] = merged["bill. date"] + pd.to_timedelta(merged["payment term"], unit="D")

        # ------------------ Date Filter Options ------------------
        today = datetime.today().date()
        st.subheader("📅 Date Filter Options")
        filter_type = st.radio("Select Filter Type:", ["Today", "Specific Date", "Date Range"], horizontal=True)

        if filter_type == "Today":
            filtered_df = merged[merged["payment due date"].dt.date == today]
            date_text = f"on {today}"

        elif filter_type == "Specific Date":
            selected_date = st.date_input("📆 Choose Date", today)
            filtered_df = merged[merged["payment due date"].dt.date == selected_date]
            date_text = f"on {selected_date}"

        else:  # Date Range
            col1, col2 = st.columns(2)
            start_date = col1.date_input("📆 From Date", today - timedelta(days=7))
            end_date = col2.date_input("📆 To Date", today)
            mask = (merged["payment due date"].dt.date >= start_date) & (merged["payment due date"].dt.date <= end_date)
            filtered_df = merged[mask]
            date_text = f"from {start_date} to {end_date}"

        # ------------------ KPIs ------------------
        total_due = filtered_df["bill amt."].sum()
        total_bills = len(filtered_df)
        total_vendors = filtered_df["party name"].nunique()

        st.markdown("### 📊 Summary KPIs")
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Due Amount", f"₹{total_due:,.2f}")
        c2.metric("📦 Total Bills", total_bills)
        c3.metric("🏢 Vendors with Dues", total_vendors)

        # ------------------ COMPANY-WISE SUMMARY ------------------
        company_summary = (
            filtered_df.groupby(["party code", "party name"], as_index=False)["bill amt."]
            .sum()
            .rename(columns={"bill amt.": "Total Amount Due"})
        )

        st.markdown(f"### 🧾 Company-wise Payment Due {date_text}")
        st.dataframe(company_summary, use_container_width=True)

        # ------------------ DETAILED DUE LIST ------------------
        show_cols = [
            "party code", "party name", "bill. date", "bill amt.",
            "payment term", "payment due date", "name", "mobile", "email"
        ]

        detailed_df = filtered_df[show_cols].sort_values("payment due date")

        st.markdown(f"### 📋 Detailed Bill-wise Dues {date_text}")
        st.dataframe(detailed_df, use_container_width=True)

        # ------------------ DOWNLOAD FUNCTIONS ------------------
        def to_excel_bytes(df, sheet_name="Sheet1"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name=sheet_name)
            return output.getvalue()

        st.download_button(
            "📥 Download Company Summary (Excel)",
            data=to_excel_bytes(company_summary, "Company Summary"),
            file_name=f"Company_Summary_{datetime.now().date()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.download_button(
            "📥 Download Detailed Dues (Excel)",
            data=to_excel_bytes(detailed_df, "Detailed Dues"),
            file_name=f"Detailed_Dues_{datetime.now().date()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    else:
        st.info("📂 Please upload the branch statement file to start tracking payment dues.")

# ------------------ CLAIM PORTAL ------------------
elif st.session_state.page == "claim":
    st.title("📂 Free Claim Portal")
    if st.button("🏠 Back to Home"): go_home()

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview:")
        st.dataframe(df.head())

        if st.button("🚀 Process Data"):
            grouped = df.groupby("Company Name")["Claim Amount"].sum().reset_index()
            grouped.columns = ["Company Name", "Total Claim Amount"]
            st.write("### 📊 Results Summary")
            st.write(f"**Total Claims:** {len(df)}")
            st.write("**Top 5 Companies by Claim Amount:**")
            st.dataframe(grouped.sort_values("Total Claim Amount", ascending=False).head(5))

            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Summary')
                return output.getvalue()

            excel_data = to_excel(grouped)
            today_date = datetime.now().strftime("%Y-%m-%d")
            file_name = f"Company_Wise_Free_Claim_Issued_{today_date}.xlsx"
            st.download_button("📥 Download Processed File", data=excel_data, file_name=file_name,
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ------------------ MAX-MIN PORTAL ------------------
elif st.session_state.page == "maxmin":
    st.title("📊 Max-Min Value Portal")
    if st.button("🏠 Back to Home"): go_home()

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview:")
        st.dataframe(df.head())

        if st.button("🔍 Find Max and Min Values"):
            numeric_df = df.select_dtypes(include='number')
            st.write("### 🔺 Maximum Values:")
            st.dataframe(numeric_df.max().to_frame("Max Value"))
            st.write("### 🔻 Minimum Values:")
            st.dataframe(numeric_df.min().to_frame("Min Value"))

# ------------------ SALES PORTAL ------------------
elif st.session_state.page == "sales":
    st.title("💰 Sales Analysis Portal")
    if st.button("🏠 Back to Home"): go_home()

    uploaded_file = st.file_uploader("Upload your Sales Excel/CSV file", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        st.write("### Uploaded Data Preview:")
        st.dataframe(df.head())

        if st.button("📊 Analyze Sales"):
            df['Dated'] = pd.to_datetime(df['Dated'], errors='coerce', dayfirst=True)
            df['Weekday'] = df['Dated'].dt.day_name()

            total_sales = df['Value'].sum()
            st.metric("💵 Total Sales", f"{total_sales:,.2f}")

            sales_by_day = df.groupby('Weekday')['Value'].sum().reindex(
                ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']).reset_index()
            st.write("### 🗓 Total Sales by Day")
            st.dataframe(sales_by_day)

            company_sales = df.groupby('Company')['Value'].sum().reset_index()
            st.write("### 🏢 Total Sales by Company")
            st.dataframe(company_sales.sort_values('Value', ascending=False))

            outlet_sales = df.groupby('Outlet')['Value'].sum().reset_index()
            st.write("### 🏪 Total Sales by Outlet")
            st.dataframe(outlet_sales.sort_values('Value', ascending=False))

            product_sales = df.groupby('Product')['Value'].sum().reset_index()
            st.write("### 📦 Total Sales by Product")
            st.dataframe(product_sales.sort_values('Value', ascending=False))

            salesman_sales = df.groupby('SalesMan')['Value'].sum().reset_index()
            st.write("### 👨‍💼 Total Sales by Salesman")
            st.dataframe(salesman_sales.sort_values('Value', ascending=False))

            def to_excel(df_dict):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, data in df_dict.items():
                        data.to_excel(writer, index=False, sheet_name=sheet_name)
                return output.getvalue()

            excel_data = to_excel({
                "Sales_by_Day": sales_by_day,
                "Sales_by_Company": company_sales,
                "Sales_by_Outlet": outlet_sales,
                "Sales_by_Product": product_sales,
                "Sales_by_Salesman": salesman_sales
            })

            st.download_button("📥 Download Sales Summary", data=excel_data,
                               file_name=f"Sales_Analysis_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



# ------------------ PENDING INDENTS MODULE ------------------
elif st.session_state.page == "pending_indents":
    st.title("📦 Pending Indents Module")
    
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"

    # Upload files
    pending_file = st.file_uploader("Upload Pending Indents File", type=["xlsx","csv"], key="pending")
    second_file = st.file_uploader("Upload Order Details File", type=["xlsx","csv"], key="second")

    if pending_file and second_file:
        df_pending = pd.read_excel(pending_file) if pending_file.name.endswith(".xlsx") else pd.read_csv(pending_file)
        df_second = pd.read_excel(second_file) if second_file.name.endswith(".xlsx") else pd.read_csv(second_file)

        st.write("### Uploaded Files Preview")
        st.write("Pending Indents:")
        st.dataframe(df_pending.head())
        st.write("Order Details:")
        st.dataframe(df_second.head())

        if st.button("🚀 Map & Aggregate Data"):
            # Map ContractID from Pending Indents
            mapping = df_pending.set_index("Ind.No.")["ContractID"].to_dict()
            df_second["ContractID"] = df_second["Ind No"].map(mapping).fillna("Manual")
            df_second["ContractID"] = df_second["ContractID"].replace("", "(blank)")

            # Aggregate and calculate Fulfillment %
            agg_df = df_second.groupby("ContractID").agg({"Ordered Items":"sum", "Invoice Items":"sum"}).reset_index()
            # Fulfillment % as proper percentage format
            agg_df["Fulfillment %"] = ((agg_df["Invoice Items"] / agg_df["Ordered Items"]) * 100).round(2).astype(str) + "%"


            # Grand Total row
            grand_total = pd.DataFrame({
                "ContractID": ["Grand Total"],
                "Ordered Items": [agg_df["Ordered Items"].sum()],
                "Invoice Items": [agg_df["Invoice Items"].sum()],
                "Fulfillment %": [(agg_df["Invoice Items"].sum() / agg_df["Ordered Items"].sum() * 100).round(2)]
            })

            final_df = pd.concat([agg_df, grand_total], ignore_index=True)
            st.write("### 📊 Aggregated Results")
            st.dataframe(final_df)

            # Download Excel
            from io import BytesIO
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Summary')
                return output.getvalue()

            st.download_button("📥 Download Excel", data=to_excel(final_df), file_name="Pending_Indents_Summary.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # Download CSV
            st.download_button("📥 Download CSV", data=final_df.to_csv(index=False).encode('utf-8'), 
                               file_name="Pending_Indents_Summary.csv", mime="text/csv")



# ------------------ NA FINDER MODULE ------------------
elif st.session_state.page == "na_finder":
    st.title("🧮 NA Finder Module")

    # Upload files
    file1 = st.file_uploader("Upload first file (Indent Data)", type=["xlsx","csv"], key="file1")
    file2 = st.file_uploader("Upload second file (Item Master)", type=["xlsx","csv"], key="file2")

    if file1 and file2:
        df1 = pd.read_excel(file1) if file1.name.endswith(".xlsx") else pd.read_csv(file1)
        df2 = pd.read_excel(file2) if file2.name.endswith(".xlsx") else pd.read_csv(file2)

        st.write("### File Previews")
        st.write("Indent Data:")
        st.dataframe(df1.head())
        st.write("Item Master Data:")
        st.dataframe(df2.head())

        # ---------- Process Button ----------
        if st.button("🚀 Process & Merge Qty from Item Master"):
            numeric_cols = ['NA', 'NA VALUE']
            for col in numeric_cols:
                if col in df1.columns:
                    df1[col] = pd.to_numeric(df1[col], errors='coerce').fillna(0)

            grouped_df = df1.groupby(
                ['SKU CODE', 'CODE', 'ITEM NAME', 'COMPANY'],
                as_index=False
            ).agg({
                'NA': ['count', 'sum'],
                'NA VALUE': 'sum'
            })

            grouped_df.columns = [
                'SKU CODE', 'Gold Code', 'ITEM NAME', 'COMPANY',
                'Count of NA', 'Sum of NA', 'Sum of NA VALUE'
            ]

            if "Gold Code" not in df2.columns or "Qty" not in df2.columns:
                st.error("Second file must have 'Gold Code' and 'Qty' columns")
                st.stop()

            merged_df = grouped_df.merge(
                df2[['Gold Code', 'Qty']],
                on='Gold Code',
                how='left'
            )

            merged_df['Qty'] = merged_df['Qty'].fillna('N/A')

            merged_df = merged_df[['SKU CODE', 'Gold Code', 'ITEM NAME', 'COMPANY', 'Qty',
                                   'Count of NA', 'Sum of NA', 'Sum of NA VALUE']]

            # Store in session_state so it persists after text input
            st.session_state["merged_df"] = merged_df

            st.success("✅ Processing completed! Scroll down for more options.")

        # ---------- If processed data exists ----------
        if "merged_df" in st.session_state:
            merged_df = st.session_state["merged_df"]

            st.write("### ✅ Final Merged Result with Qty from Item Master")
            st.dataframe(merged_df)

            # ---------- Download buttons ----------
            from io import BytesIO
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Merged')
                return output.getvalue()

            excel_data = to_excel(merged_df)
            st.download_button("📥 Download Final Excel", data=excel_data,
                               file_name="NA_Finder_Final.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            st.download_button("📥 Download Final CSV", data=merged_df.to_csv(index=False).encode('utf-8'),
                               file_name="NA_Finder_Final.csv",
                               mime="text/csv")

            # ---------- New Section: Percentage Calculation ----------
            st.markdown("---")
            st.subheader("📊 Company-wise NA Percentage Calculator")

            user_input = st.text_input("Enter a number for percentage calculation (e.g., total value):")

            if user_input:
                try:
                    base_value = float(user_input)

                    # Group by company and calculate sum of Count of NA
                    company_summary = merged_df.groupby('COMPANY', as_index=False)['Count of NA'].sum()

                    # Calculate percentage
                    company_summary['Percentage'] = ((company_summary['Count of NA'] / base_value) * 100).round(3)
                    company_summary['Percentage'] = company_summary['Percentage'].astype(str) + " %"

                    st.write("### 📈 Company-wise NA Summary")
                    st.dataframe(company_summary)

                    # Optional download
                    excel_summary = to_excel(company_summary)
                    st.download_button("📥 Download Company Summary Excel", data=excel_summary,
                                       file_name="Company_NA_Summary.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                except ValueError:
                    st.error("⚠️ Please enter a valid numeric value.")


# ------------------ DB AGE ANALYSIS MODULE ------------------
elif st.session_state.page == "db_age":
    st.title("📊 DB Age Analysis Module")
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"

    # ------------------ FILE UPLOADER ------------------
    uploaded_file = st.file_uploader("Upload your Excel/CSV file", type=["xlsx","csv"], key="db_age_file")
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
        
        # Strip spaces from column names
        df.columns = df.columns.str.strip()
        
        # Find DB Date column
        db_date_col = [col for col in df.columns if col.lower() == 'db date']
        if not db_date_col:
            st.error("⚠️ No 'DB Date' column found in the uploaded file.")
            st.stop()
        db_date_col = db_date_col[0]

        st.write("### Uploaded Data Preview")
        st.dataframe(df.head())

        # ------------------ DATE SELECTION ------------------
        st.subheader("Select Reference Date for Age Calculation")
        date_option = st.radio("Choose date option:", ["Today", "Custom Date"])
        if date_option == "Custom Date":
            reference_date = st.date_input("Select Date")
        else:
            reference_date = pd.to_datetime("today")

        # ------------------ AGE CALCULATION ------------------
        df['DB Date'] = pd.to_datetime(df[db_date_col], errors='coerce', dayfirst=True)
        df['AgeDays'] = (pd.to_datetime(reference_date) - df['DB Date']).dt.days

        # ------------------ AGE BUCKETS ------------------
        def age_bucket(days):
            if pd.isna(days):
                return "Unknown"
            if 0 <= days <= 30:
                return "0-30"
            elif 31 <= days <= 60:
                return "31-60"
            elif 61 <= days <= 90:
                return "61-90"
            elif 91 <= days <= 120:
                return "91-120"
            elif 121 <= days <= 180:
                return "121-180"
            elif 181 <= days <= 270:
                return "181-270"
            elif 271 <= days <= 360:
                return "271-360"
            else:
                return "Above 360"

        df['Age Bucket'] = df['AgeDays'].apply(age_bucket)

        st.write("### Data with Age and Buckets")
        st.dataframe(df.head())

        # ------------------ PIVOT TABLE ------------------
        if 'Pending' not in df.columns:
            st.error("⚠️ No 'Pending' column found in the uploaded file.")
        else:
            pivot_df = pd.pivot_table(
                df,
                index='Supplier',
                columns='Age Bucket',
                values='Pending',
                aggfunc='sum',
                fill_value=0
            ).reset_index()

            st.write("### 📊 Supplier-wise Pending Amount by Age Bucket")
            st.dataframe(pivot_df)

            # ------------------ DOWNLOAD ------------------
            from io import BytesIO
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='DB_Age_Analysis')
                return output.getvalue()

            excel_data = to_excel(pivot_df)
            st.download_button("📥 Download DB Age Pivot Excel", data=excel_data,
                               file_name=f"DB_Age_Analysis_{pd.to_datetime(reference_date).strftime('%Y-%m-%d')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# --------------------------- APOLLO CHECK ---------------------------
elif st.session_state.page == "apollo":
    st.title("🚀 Apollo Check Module")

    # ------------------ FILE UPLOADER ------------------

    if "apollo_file" not in st.session_state:
        st.session_state.apollo_file = None

    uploaded_file = st.file_uploader("Upload your Excel/CSV file for Apollo Check", type=["xlsx", "csv"])
    if uploaded_file:
        st.session_state.apollo_file = uploaded_file

    if not st.session_state.apollo_file:
        st.info("Please upload a file to continue.")
        st.stop()

    # ------------------ READ FILE ------------------
    df = pd.read_excel(st.session_state.apollo_file) if st.session_state.apollo_file.name.endswith(".xlsx") else pd.read_csv(st.session_state.apollo_file)
    df['INDENT DATE'] = pd.to_datetime(df['INDENT DATE'], errors='coerce')
    df = df.sort_values(['SHOP NAME','ITEM NAME','INDENT DATE'])

    # ------------------ TABLE 1: CONTINUOUS ORDERS ------------------
    st.subheader("📊 Continuous Orders Table")
    consecutive_days = st.selectbox("Select consecutive days", list(range(1,16)), key="consec_days")
    continuous_list = []

    for shop, shop_df in df.groupby('SHOP NAME'):
        for item, item_df in shop_df.groupby('ITEM NAME'):
            dates = item_df['INDENT DATE'].sort_values().tolist()
            count = 1
            for i in range(1,len(dates)):
                if (dates[i] - dates[i-1]).days == 1:
                    count += 1
                else:
                    count = 1
                if count >= consecutive_days:
                    continuous_list.append([shop, item, dates[i-consecutive_days+1], dates[i], consecutive_days])
                    break

    continuous_df = pd.DataFrame(continuous_list, columns=['Shop Name','Item Name','Start Date','End Date','Consecutive Days'])
    st.dataframe(continuous_df)

    # ------------------ TABLE 2: NON-CONTINUOUS ORDERS ------------------
    st.subheader("📊 Non-Continuous Orders Table")
    total_days = st.selectbox("Select total order days", list(range(1,16)), key="total_days")
    non_continuous_list = []

    for shop, shop_df in df.groupby('SHOP NAME'):
        for item, item_df in shop_df.groupby('ITEM NAME'):
            unique_days = item_df['INDENT DATE'].nunique()
            if unique_days >= total_days:
                non_continuous_list.append([shop, item, unique_days])

    non_continuous_df = pd.DataFrame(non_continuous_list, columns=['Shop Name','Item Name','Total Days Ordered'])
    st.dataframe(non_continuous_df)

    # ------------------ COMPLETE SUMMARY TABLE ------------------
    st.subheader("📋 Complete Summary Table (All Data)")
    summary_list = []

    for shop, shop_df in df.groupby('SHOP NAME'):
        for item, item_df in shop_df.groupby('ITEM NAME'):
            summary_list.append([shop, item, item_df['INDENT DATE'].nunique()])

    summary_df = pd.DataFrame(summary_list, columns=['Shop Name','Item Name','Total Days Ordered'])
    summary_df = summary_df.sort_values('Total Days Ordered', ascending=False)
    st.dataframe(summary_df)

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"


# ------------------ ADMIN LOGIN LOG PAGE ------------------
elif st.session_state.page == "admin_log":
    st.title("📝 Login Activity Log")
    if st.button("🏠 Back to Home"): go_home()

    if os.path.exists(LOGIN_LOG_FILE):
        log_df = pd.read_csv(LOGIN_LOG_FILE)
        st.dataframe(log_df)

        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='LoginLogs')
            return output.getvalue()

        st.download_button("📥 Download Login Logs", data=to_excel(log_df), file_name="LoginLogs.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No login records yet.")



# END OF FILE   
