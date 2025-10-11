import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import os



# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Yogiram Automation - Gokul",
    page_icon="⚙️",
    layout="centered"
)

# ------------------ LOGIN ------------------
# Easy-to-add users system
users = {
    "admin": "1234",
    "gokul": "abcd",
    "vel":"1234",
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
st.markdown("""
<style>
/* ---------------- BODY & BACKGROUND ---------------- */
body {
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #f0f0f0;
}
/* ---------------- MAIN CONTAINER ---------------- */
.css-1d391kg {  /* streamlit main container */
    background: linear-gradient(145deg, #2a2a72, #009ffd);
    border-radius: 20px;
    padding: 30px 40px;
    margin: 20px auto;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.3);
}
/* ---------------- HEADINGS ---------------- */
h1 {
    font-size: 48px;
    text-align: center;
    color: #ffffff;
    text-shadow: 1px 1px 5px #00000066;
    margin-bottom: 15px;
}
h2 {
    font-size: 28px;
    text-align: center;
    color: #e0e0e0;
    font-weight: 400;
    margin-bottom: 30px;
}
/* ---------------- BUTTONS ---------------- */
.stButton>button {
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
    color: #000000;
    font-weight: bold;
    font-size: 18px;
    padding: 15px 30px;
    border-radius: 15px;
    border: none;
    transition: all 0.4s ease;
    width: 100%;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
}
.stButton>button:hover {
    background: linear-gradient(90deg, #92FE9D, #00C9FF);
    transform: translateY(-3px) scale(1.05);
    color: #000000;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.35);
}
/* ---------------- INPUT BOXES ---------------- */
.stTextInput>div>div>input {
    background: #ffffff11;
    color: #ffffff;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #ffffff55;
    transition: all 0.3s ease;
}
.stTextInput>div>div>input:focus {
    border: 1.5px solid #00FFD4;
    background: #ffffff22;
    outline: none;
    box-shadow: 0px 0px 10px rgba(0,255,212,0.5);
}
/* ---------------- FILE UPLOADER ---------------- */
.stFileUploader>div>div {
    border: 2px dashed #ffffff66;
    border-radius: 15px;
    padding: 20px;
    transition: all 0.3s ease;
}
.stFileUploader>div>div:hover {
    border-color: #00FFD4;
    background: #ffffff11;
}
/* ---------------- DATAFRAMES / TABLES ---------------- */
.stDataFrame div[data-testid="stDataFrameContainer"] {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
}
.stDataFrame th {
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
    color: #000;
    font-weight: bold;
}
.stDataFrame td {
    background: #ffffff11;
    color: #fff;
}
/* ---------------- FOOTER ---------------- */
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 16px;
    color: #f5f5f5;
    padding: 10px 0;
    background: linear-gradient(90deg, #2a2a72, #009ffd);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    box-shadow: 0px -4px 15px rgba(0,0,0,0.3);
}
/* ---------------- CARDS / COLUMNS ---------------- */
.stButton, .stTextInput, .stFileUploader, .stDataFrame {
    margin-bottom: 20px;
}
/* ---------------- HOVER CARD EFFECT ---------------- */
.card:hover {
    transform: scale(1.03);
    box-shadow: 0px 12px 35px rgba(0,0,0,0.35);
}
/* ---------------- SCROLLBAR ---------------- */
::-webkit-scrollbar {
    width: 10px;
}
::-webkit-scrollbar-track {
    background: #1e3c72;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb {
    background: #92FE9D;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #00C9FF;
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





# ------------------ HOME PAGE ------------------
if st.session_state.page == "home":
    st.markdown("<h1>⚙️ Yogiram Automation System</h1>", unsafe_allow_html=True)
    st.markdown("<h2>Welcome to the Automation Portal</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Choose an automation to run 👇")

    col1, col2, col3, col4, col5 ,col6= st.columns(6)

    with col1:
        if st.button("📂 Claim Portal"):
            go_claim()
    with col2:
        if st.button("📊 Max/Min Value Portal"):
            go_maxmin()
    with col3:
        if st.button("💰 Sales Portal"):
            go_sales()
    with col4:
        if username == "admin" and st.button("📝 Login Activity"):
            go_admin_log()
    with col5:
        if st.button("🛒 Apollo Check Portal"):
            go_apollo()   # <- New portal
    with col6:
        if st.button("📦 Pending Indents Check"):
            go_pending_indents()



    st.markdown("---")
    st.markdown("""
        <footer>
            Created by <b>Gokul</b> — Data Analyst, <b>Yogiram</b>
        </footer>
    """, unsafe_allow_html=True)

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
            agg_df["Fulfillment %"] = (agg_df["Invoice Items"] / agg_df["Ordered Items"] * 100).round(2)

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
