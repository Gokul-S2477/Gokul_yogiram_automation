import streamlit as st
import sys

if not st.runtime.exists():
    print("\n=================================================================")
    print("❌ ERROR: You ran this using 'python pharma_dashboard.py'")
    print("✅ Please run this app using: streamlit run pharma_dashboard.py")
    print("=================================================================\n")
    sys.exit(1)
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Pharma Supplier Intelligence", layout="wide", page_icon="◈")

# ─── STYLING ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stMetric {
        background-color: #161B22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363D;
    }
    .stMetric label {
        color: #8B949E !important;
        font-family: 'IBM Plex Mono', Consolas, monospace;
        letter-spacing: 1px;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    .main-title {
        background: linear-gradient(90deg, #58A6FF, #b392f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8B949E;
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }
    .badge {
        background-color: #58A6FF;
        color: #0D1117;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: bold;
        vertical-align: super;
        margin-left: 10px;
    }
    /* Hide top padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── DATA PROCESSING ─────────────────────────────────────────────────────────
@st.cache_data
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.strip()

    rename_map = {
        'Supplier Cod': 'Supplier Code',
        'Credit Limi': 'Credit Limit',
        'Order Numbe': 'Order Number',
        'Grn Numbe': 'Grn Number',
        'Order Item': 'Order Items',
        'Receved Item': 'Received Items',
        'Receved Items':  'Received Items',
        'Recieved Items': 'Received Items',
        'Received Valu': 'Received Value',
    }
    df.rename(columns=rename_map, inplace=True)

    for col in ['Order Date', 'Grn Date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

    for col in ['Orderqty', 'Received Qty', 'Order Value', 'Received Value']:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                       .str.replace(',', '', regex=False)
                       .pipe(pd.to_numeric, errors='coerce')
                       .fillna(0)
            )

    df['NS_Flag']      = (df['Received Qty'] == 0).astype(int)
    df['Partial_Flag'] = ((df['Received Qty'] > 0) & (df['Received Qty'] < df['Orderqty'])).astype(int)
    df['Qty_Fill']     = np.where(df['Orderqty'] > 0, df['Received Qty'] / df['Orderqty'], 0)
    df['Val_Fill']     = np.where(df['Order Value'] > 0, df['Received Value'] / df['Order Value'], 0)
    df['NS_Value']     = df['Order Value'] - df['Received Value']
    df['Lead_Days']    = (df['Grn Date'] - df['Order Date']).dt.days
    return df

@st.cache_data
def load_data(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(('xlsx', 'xls')):
        df = pd.read_excel(file)
    else:
        try:
            df = pd.read_csv(file, sep='\t')
            if df.shape[1] < 5:
                file.seek(0)
                df = pd.read_csv(file)
        except Exception:
            file.seek(0)
            df = pd.read_csv(file, encoding='latin-1')
    return clean_df(df)


# ─── MAIN APP ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">Supplier Intelligence <span class="badge">v3.0 MAX</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Pharma Distributor Dashboard</div>', unsafe_allow_html=True)

# ─── SIDEBAR & FILTERS ───────────────────────────────────────────────────────
st.sidebar.markdown("### 📁 Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload Excel/CSV", type=['xlsx', 'xls', 'csv'])

if not uploaded_file:
    st.info("👋 Welcome! Please upload a data file in the sidebar to generate the dashboard. Powered by Streamlit for blazing fast performance.")
    st.stop()

# Load Data
try:
    with st.spinner("Crunching data..."):
        raw_df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

df = raw_df.copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filters")

# Date Filter
if 'Order Date' in df.columns:
    min_date = df['Order Date'].min()
    max_date = df['Order Date'].max()
    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.sidebar.date_input("📅 Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        if len(date_range) == 2:
            df = df[(df['Order Date'].dt.date >= date_range[0]) & (df['Order Date'].dt.date <= date_range[1])]

companies = st.sidebar.multiselect("🏢 Company", sorted(df['Company'].dropna().unique()) if 'Company' in df.columns else [])
suppliers = st.sidebar.multiselect("🏭 Supplier", sorted(df['Supplier Name'].dropna().unique()) if 'Supplier Name' in df.columns else [])
items = st.sidebar.multiselect("💊 Item", sorted(df['Item Name'].dropna().unique()) if 'Item Name' in df.columns else [])

if companies: df = df[df['Company'].isin(companies)]
if suppliers: df = df[df['Supplier Name'].isin(suppliers)]
if items: df = df[df['Item Name'].isin(items)]

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ─── METRICS CALCULATION ─────────────────────────────────────────────────────
ov   = df['Order Value'].sum()
rv   = df['Received Value'].sum()
ns_v = df['NS_Value'].sum()
nsl  = int(df['NS_Flag'].sum())
tot  = len(df)
total_orders = df['Order Number'].nunique() if 'Order Number' in df.columns else 0
fill = rv / ov * 100 if ov > 0 else 0
lead = df['Lead_Days'].dropna().mean()
avg_ov = ov / total_orders if total_orders > 0 else 0

# ─── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📊 Overview", "🏭 Supplier Score", "⚠️ NS Tracker", "💊 Item Analysis", "📦 Qty Report", "🏢 Company Report", "🔎 Item Deep Dive"])

# Colors
C_TEXT = '#E6EDF3'
C_SUB = '#8B949E'
C_BORDER = '#30363D'
C_ACCENT = '#58A6FF'
C_GREEN = '#3FB950'
C_YELLOW = '#D29922'
C_RED = '#F85149'

def base_layout(title=''):
    return dict(
        title=dict(text=title, font=dict(color=C_TEXT, size=16)),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=C_SUB),
        margin=dict(l=40, r=20, t=50, b=40),
    )

with tab1:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Total Lines", f"{tot:,}")
    col3.metric("Avg Order Value", f"₹{avg_ov:,.0f}")
    col4.metric("Avg Lead Days", f"{lead:.1f}d" if pd.notna(lead) else "N/A")
    col5.metric("NS Loss Lines", f"{nsl:,} / {tot:,}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Order Value", f"₹{ov:,.0f}")
    col2.metric("Total Received Value", f"₹{rv:,.0f}", delta=f"{fill:.1f}% Fill Rate")
    col3.metric("Total NS Value Loss", f"₹{ns_v:,.0f}", delta="- Loss", delta_color="inverse")

    st.markdown("---")
    
    # Pre-calculate Qty Fill for gauge
    oq_tot = df['Orderqty'].sum()
    rq_tot = df['Received Qty'].sum()
    q_fill_ov = rq_tot / oq_tot * 100 if oq_tot > 0 else 0
    
    c1, c2, c3 = st.columns([1, 1, 2])
    
    # Gauge 1 (Value)
    fig_g = go.Figure(go.Indicator(
        mode='gauge+number', value=fill, number={'suffix':'%','font':{'color':C_TEXT}},
        gauge=dict(
            axis=dict(range=[0,100]), bar=dict(color=C_ACCENT), bgcolor=C_BORDER,
            steps=[dict(range=[0,50], color='#1a0a0a'), dict(range=[50,75], color='#1a1500'), dict(range=[75,100], color='#0a1a0a')],
            threshold=dict(line=dict(color=C_GREEN, width=2), thickness=0.75, value=90)
        )
    ))
    layout_g = base_layout('Value Fill Rate')
    layout_g.update(margin=dict(l=20,r=20,t=40,b=10), height=250)
    fig_g.update_layout(**layout_g)
    c1.plotly_chart(fig_g, use_container_width=True)
    
    # Gauge 2 (Qty)
    fig_g2 = go.Figure(go.Indicator(
        mode='gauge+number', value=q_fill_ov, number={'suffix':'%','font':{'color':C_TEXT}},
        gauge=dict(
            axis=dict(range=[0,100]), bar=dict(color=C_GREEN), bgcolor=C_BORDER,
            steps=[dict(range=[0,50], color='#1a0a0a'), dict(range=[50,75], color='#1a1500'), dict(range=[75,100], color='#0a1a0a')],
            threshold=dict(line=dict(color=C_ACCENT, width=2), thickness=0.75, value=90)
        )
    ))
    layout_g2 = base_layout('Qty Fill Rate')
    layout_g2.update(margin=dict(l=20,r=20,t=40,b=10), height=250)
    fig_g2.update_layout(**layout_g2)
    c2.plotly_chart(fig_g2, use_container_width=True)

    # Waterfall
    fig_w = go.Figure(go.Waterfall(
        x=['Order Value','NS Loss','Received Value'], y=[ov, -ns_v, 0], measure=['absolute','relative','total'],
        decreasing=dict(marker_color=C_RED), increasing=dict(marker_color=C_GREEN), totals=dict(marker_color=C_ACCENT),
        text=[f'₹{ov:,.0f}', f'-₹{ns_v:,.0f}', f'₹{rv:,.0f}'], textposition='outside', textfont=dict(color=C_TEXT)
    ))
    layout_w = base_layout('Order → Loss → Received (₹)')
    layout_w.update(height=300)
    fig_w.update_layout(**layout_w)
    c3.plotly_chart(fig_w, use_container_width=True)

    c3, c4 = st.columns(2)
    # Daily trend if date exists
    if 'Order Date' in df.columns:
        trend = df.groupby(df['Order Date'].dt.date).agg({'Order Value': 'sum', 'Received Value': 'sum'}).reset_index()
        fig_t = px.line(trend, x='Order Date', y=['Order Value', 'Received Value'], 
                        color_discrete_map={'Order Value': C_ACCENT, 'Received Value': C_GREEN},
                        title='Daily Volume Trend')
        layout_t = base_layout('Daily Volume Trend')
        layout_t.update(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_t.update_layout(**layout_t)
        c3.plotly_chart(fig_t, use_container_width=True)
    
    # Top Suppliers Pie
    if 'Supplier Name' in df.columns:
        sup_vol = df.groupby('Supplier Name')['Order Value'].sum().nlargest(10).reset_index()
        fig_p = px.pie(sup_vol, values='Order Value', names='Supplier Name', hole=0.4, 
                       color_discrete_sequence=px.colors.sequential.Plasma)
        layout_p = base_layout('Top 10 Suppliers by Volume')
        layout_p.update(height=350, showlegend=False)
        fig_p.update_layout(**layout_p)
        c4.plotly_chart(fig_p, use_container_width=True)

    # New charts row
    c5, c6 = st.columns(2)
    if 'Company' in df.columns:
        comp_vol = df.groupby('Company')['Order Value'].sum().reset_index().sort_values('Order Value', ascending=True)
        fig_c = px.bar(comp_vol, x='Order Value', y='Company', orientation='h', color_discrete_sequence=[C_ACCENT])
        layout_c = base_layout('Order Volume by Company')
        layout_c.update(height=300)
        fig_c.update_layout(**layout_c)
        c5.plotly_chart(fig_c, use_container_width=True)
        
    if 'Order Date' in df.columns:
        df['Weekday'] = df['Order Date'].dt.day_name()
        cats = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_vol = df.groupby('Weekday')['Order Number'].nunique().reindex(cats).reset_index().fillna(0)
        fig_dw = px.bar(day_vol, x='Weekday', y='Order Number', color_discrete_sequence=[C_GREEN])
        layout_dw = base_layout('Order Frequency by Day of Week')
        layout_dw.update(height=300)
        fig_dw.update_layout(**layout_dw)
        c6.plotly_chart(fig_dw, use_container_width=True)


with tab2:
    st.subheader("🏭 Supplier Performance Scorecard")
    
    grp = df.groupby(['Supplier Code', 'Supplier Name'])
    sc = grp.agg(
        Total_Orders   = ('Order Number',  'nunique'),
        Total_Lines    = ('Item Code',     'count'),
        NS_Lines       = ('NS_Flag',       'sum'),
        Order_Value    = ('Order Value',   'sum'),
        Received_Value = ('Received Value','sum'),
        NS_Value       = ('NS_Value',      'sum'),
        Avg_Lead_Days  = ('Lead_Days',     'mean'),
        Qty_Fill_Rate  = ('Qty_Fill',      'mean'),
        Val_Fill_Rate  = ('Val_Fill',      'mean'),
    ).reset_index()
    sc['NS_Rate']      = sc['NS_Lines']      / sc['Total_Lines'] * 100
    sc['Score'] = (
        sc['Val_Fill_Rate'] * 50 +
        (1 - sc['NS_Rate'] / 100) * 30 +
        np.clip(1 - (sc['Avg_Lead_Days'].fillna(7) / 10), 0, 1) * 20
    ).round(1)
    sc['Grade'] = pd.cut(sc['Score'], bins=[0,50,65,80,90,100], labels=['F','D','C','B','A'], right=True)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    best_sup = sc.loc[sc['Score'].idxmax()]['Supplier Name'] if not sc.empty else "N/A"
    worst_sup = sc.loc[sc['Score'].idxmin()]['Supplier Name'] if not sc.empty else "N/A"
    avg_score = sc['Score'].mean()
    k1.metric("Active Suppliers", f"{len(sc)}")
    k2.metric("Average Score", f"{avg_score:.1f}/100")
    k3.metric("Top Performer", f"{best_sup[:15]}..")
    k4.metric("Needs Attention", f"{worst_sup[:15]}..")
    
    # Charts
    c1, c2 = st.columns([1, 2])
    grade_counts = sc['Grade'].value_counts().reset_index()
    fig_gpie = px.pie(grade_counts, values='count', names='Grade', hole=0.5,
                      color='Grade', color_discrete_map={'A': C_GREEN, 'B': '#73D055', 'C': C_YELLOW, 'D': '#E67E22', 'F': C_RED})
    layout_gpie = base_layout('Supplier Grades Distribution')
    layout_gpie.update(height=350)
    fig_gpie.update_layout(**layout_gpie)
    c1.plotly_chart(fig_gpie, use_container_width=True)
    
    fig_scat = px.scatter(sc, x='Avg_Lead_Days', y='Val_Fill_Rate', size='Order_Value', color='Score',
                          hover_name='Supplier Name', color_continuous_scale='RdYlGn', size_max=40)
    layout_scat = base_layout('Lead Time vs Fill Rate (Size = Order Vol)')
    layout_scat.update(height=350, yaxis=dict(tickformat='.0%'))
    fig_scat.update_layout(**layout_scat)
    c2.plotly_chart(fig_scat, use_container_width=True)

    st.markdown("""
    **Score Formula:** Value Fill Rate (50) + NS Rate inverse (30) + Lead Time speed (20).  
    **Grades:** A (90-100), B (80-89), C (65-79), D (50-64), F (<50)
    """)
    st.dataframe(
        sc.style.format({
            'Val_Fill_Rate': '{:.1%}', 'NS_Rate': '{:.1f}%', 'Avg_Lead_Days': '{:.1f}', 
            'Order_Value': '₹{:,.0f}', 'NS_Value': '₹{:,.0f}', 'Score': '{:.1f}'
        }).background_gradient(subset=['Score'], cmap='RdYlGn'),
        use_container_width=True, height=500
    )


with tab3:
    ns_df = df[df['NS_Flag'] == 1][['Supplier Name','Item Code','Item Name','Order Number','Order Date','Orderqty','NS_Value']].sort_values('NS_Value', ascending=False)
    
    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("Total NS Lines", f"{len(ns_df):,}")
    k2.metric("Total NS Value", f"₹{ns_df['NS_Value'].sum():,.0f}")
    avg_ns = ns_df['NS_Value'].mean() if not ns_df.empty else 0
    k3.metric("Avg NS Value / Line", f"₹{avg_ns:,.0f}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    # NS by Supplier Chart
    ns_sup = ns_df.groupby('Supplier Name')['NS_Value'].sum().nlargest(10).reset_index()
    fig_ns_sup = px.bar(ns_sup, x='Supplier Name', y='NS_Value', color_discrete_sequence=[C_RED])
    layout_ns_sup = base_layout('Top 10 Suppliers causing NS Loss')
    layout_ns_sup.update(height=350)
    fig_ns_sup.update_layout(**layout_ns_sup)
    c1.plotly_chart(fig_ns_sup, use_container_width=True)
    
    # NS Trend Chart
    if 'Order Date' in ns_df.columns:
        ns_trend = ns_df.groupby(ns_df['Order Date'].dt.date)['NS_Value'].sum().reset_index()
        fig_ns_trend = px.area(ns_trend, x='Order Date', y='NS_Value', color_discrete_sequence=[C_RED])
        layout_ns_trend = base_layout('Daily NS Loss Trend')
        layout_ns_trend.update(height=350)
        fig_ns_trend.update_layout(**layout_ns_trend)
        c2.plotly_chart(fig_ns_trend, use_container_width=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("⚠️ Top Not Supplied (NS) Items")
        top_ns = ns_df.head(15)
        fig_ns = go.Figure(go.Bar(
            x=top_ns['NS_Value'], y=top_ns['Item Name'], orientation='h', marker_color=C_RED,
            text=top_ns['NS_Value'].apply(lambda x: f'₹{x:,.0f}'), textposition='outside'
        ))
        layout_ns = base_layout()
        layout_ns.update(height=500, yaxis=dict(autorange='reversed'), xaxis=dict(title="Lost Value (₹)"))
        fig_ns.update_layout(**layout_ns)
        st.plotly_chart(fig_ns, use_container_width=True)
        
    with col2:
        st.subheader("📋 Items to Re-order")
        st.dataframe(ns_df[['Item Name', 'Orderqty', 'NS_Value']], use_container_width=True, height=500)


with tab4:
    st.subheader("💊 Item Fulfillment Analysis")
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Unique Items Ordered", f"{df['Item Name'].nunique():,}")
    k2.metric("Total Items Received", f"{df['Received Qty'].sum():,.0f}")
    k3.metric("Avg Qty per Line", f"{df['Orderqty'].mean():,.1f}")
    most_exp = df.loc[df['Order Value'].idxmax()]['Item Name'] if not df.empty and 'Order Value' in df.columns else "N/A"
    k4.metric("Highest Value Item", f"{most_exp[:15]}..")
    
    item_df = df.groupby(['Item Code','Item Name']).agg(
        Times_Ordered  = ('Orderqty',    'count'),
        Total_Ordered  = ('Orderqty',    'sum'),
        Total_Received = ('Received Qty','sum'),
        NS_Value       = ('NS_Value',    'sum'),
        Fill_Rate      = ('Qty_Fill',    'mean'),
    ).reset_index().sort_values('NS_Value', ascending=False)
    
    c1, c2 = st.columns(2)
    with c1:
        top_worst = item_df[item_df['Times_Ordered'] > 1].nsmallest(15, 'Fill_Rate')
        colors = [C_RED if r < 0.5 else C_YELLOW if r < 0.8 else C_GREEN for r in top_worst['Fill_Rate']]
        fig_fr = go.Figure(go.Bar(
            x=top_worst['Fill_Rate']*100, y=top_worst['Item Name'], orientation='h', marker_color=colors,
            text=[f'{r*100:.0f}%' for r in top_worst['Fill_Rate']], textposition='outside'
        ))
        layout_fr = base_layout('Worst Item Fill Rates (ordered >1 times)')
        layout_fr.update(height=400, yaxis=dict(autorange='reversed'), xaxis=dict(range=[0,115]))
        fig_fr.update_layout(**layout_fr)
        st.plotly_chart(fig_fr, use_container_width=True)

    with c2:
        top_ordered = df.groupby('Item Name')['Orderqty'].sum().nlargest(15).reset_index()
        fig_ord = go.Figure(go.Bar(
            x=top_ordered['Orderqty'], y=top_ordered['Item Name'], orientation='h', marker_color=C_ACCENT,
            text=top_ordered['Orderqty'].apply(lambda x: f'{x:,.0f}'), textposition='outside'
        ))
        layout_ord = base_layout('Most Ordered Items (Qty)')
        layout_ord.update(height=400, yaxis=dict(autorange='reversed'))
        fig_ord.update_layout(**layout_ord)
        st.plotly_chart(fig_ord, use_container_width=True)

    c3, c4 = st.columns(2)
    # Scatter: Ordered vs Received
    fig_sq = px.scatter(item_df, x='Total_Ordered', y='Total_Received', hover_name='Item Name', color='Fill_Rate',
                        color_continuous_scale='RdYlGn', opacity=0.7)
    fig_sq.add_shape(type='line', x0=0, y0=0, x1=item_df['Total_Ordered'].max(), y1=item_df['Total_Ordered'].max(),
                     line=dict(color=C_BORDER, dash='dash'))
    layout_sq = base_layout('Ordered vs Received Quantities')
    layout_sq.update(height=350)
    fig_sq.update_layout(**layout_sq)
    c3.plotly_chart(fig_sq, use_container_width=True)
    
    # Most Frequent items
    freq = item_df.nlargest(10, 'Times_Ordered')
    fig_fq = px.bar(freq, x='Times_Ordered', y='Item Name', orientation='h', color_discrete_sequence=['#b392f0'])
    layout_fq = base_layout('Most Frequently Ordered Items (Line Count)')
    layout_fq.update(height=350, yaxis=dict(autorange='reversed'))
    fig_fq.update_layout(**layout_fq)
    c4.plotly_chart(fig_fq, use_container_width=True)

    st.markdown("### 🗃️ Full Item Table")
    st.dataframe(
        item_df.style.format({
            'Total_Ordered': '{:,.0f}', 'Total_Received': '{:,.0f}',
            'NS_Value': '₹{:,.0f}', 'Fill_Rate': '{:.1%}'
        }),
        use_container_width=True
    )

with tab5:
    st.subheader("📦 Quantity Fulfillment Report")
    
    oq = df['Orderqty'].sum()
    rq = df['Received Qty'].sum()
    q_fill = rq / oq * 100 if oq > 0 else 0
    shortfall = oq - rq
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Ordered Qty", f"{oq:,.0f}")
    k2.metric("Total Received Qty", f"{rq:,.0f}", delta=f"{q_fill:.1f}% Qty Fill Rate")
    k3.metric("Total Qty Shortfall", f"{shortfall:,.0f}", delta="Missing", delta_color="inverse")
    k4.metric("Avg Qty per Order", f"{oq/total_orders:,.0f}" if total_orders > 0 else "0")

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    top_items_qty = df.groupby('Item Name').agg({'Orderqty':'sum', 'Received Qty':'sum'}).nlargest(15, 'Orderqty').reset_index()
    fig_qty_bar = go.Figure()
    fig_qty_bar.add_trace(go.Bar(x=top_items_qty['Item Name'], y=top_items_qty['Orderqty'], name='Ordered Qty', marker_color=C_ACCENT))
    fig_qty_bar.add_trace(go.Bar(x=top_items_qty['Item Name'], y=top_items_qty['Received Qty'], name='Received Qty', marker_color=C_GREEN))
    layout_qty_bar = base_layout('Top 15 Items: Ordered vs Received Qty')
    layout_qty_bar.update(barmode='group', height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_qty_bar.update_layout(**layout_qty_bar)
    c1.plotly_chart(fig_qty_bar, use_container_width=True)
    
    sup_short = df.copy()
    sup_short['Qty_Shortfall'] = sup_short['Orderqty'] - sup_short['Received Qty']
    top_short = sup_short.groupby('Supplier Name')['Qty_Shortfall'].sum().nlargest(10).reset_index()
    fig_short = px.bar(top_short, x='Supplier Name', y='Qty_Shortfall', color_discrete_sequence=[C_YELLOW])
    layout_short = base_layout('Top 10 Suppliers by Qty Shortfall')
    layout_short.update(height=400)
    fig_short.update_layout(**layout_short)
    c2.plotly_chart(fig_short, use_container_width=True)
    
    if 'Order Date' in df.columns:
        qty_trend = df.groupby(df['Order Date'].dt.date).agg({'Orderqty': 'sum', 'Received Qty': 'sum'}).reset_index()
        fig_qtrend = px.line(qty_trend, x='Order Date', y=['Orderqty', 'Received Qty'],
                             color_discrete_map={'Orderqty': C_ACCENT, 'Received Qty': C_GREEN})
        layout_qtrend = base_layout('Daily Quantity Trend')
        layout_qtrend.update(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_qtrend.update_layout(**layout_qtrend)
        st.plotly_chart(fig_qtrend, use_container_width=True)

with tab6:
    if 'Company' not in df.columns or df['Company'].dropna().empty:
        st.warning("No 'Company' column found in the current dataset.")
    else:
        st.subheader("🏢 Company Performance & Analytics")
        
        # Aggregate Company Data
        c_grp = df.groupby('Company')
        comp_df = c_grp.agg(
            Total_Orders   = ('Order Number',  'nunique'),
            Total_Lines    = ('Item Code',     'count'),
            NS_Lines       = ('NS_Flag',       'sum'),
            Order_Value    = ('Order Value',   'sum'),
            Received_Value = ('Received Value','sum'),
            NS_Value       = ('NS_Value',      'sum'),
            Avg_Lead_Days  = ('Lead_Days',     'mean'),
            Qty_Fill_Rate  = ('Qty_Fill',      'mean'),
            Val_Fill_Rate  = ('Val_Fill',      'mean'),
        ).reset_index()
        
        comp_df['NS_Rate'] = comp_df['NS_Lines'] / comp_df['Total_Lines'] * 100
        comp_df['Score'] = (
            comp_df['Val_Fill_Rate'] * 50 +
            (1 - comp_df['NS_Rate'] / 100) * 30 +
            np.clip(1 - (comp_df['Avg_Lead_Days'].fillna(7) / 10), 0, 1) * 20
        ).round(1)
        comp_df['Grade'] = pd.cut(comp_df['Score'], bins=[0,50,65,80,90,100], labels=['F','D','C','B','A'], right=True)
        
        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        best_comp = comp_df.loc[comp_df['Score'].idxmax()]['Company'] if not comp_df.empty else "N/A"
        worst_comp = comp_df.loc[comp_df['Score'].idxmin()]['Company'] if not comp_df.empty else "N/A"
        avg_comp_score = comp_df['Score'].mean()
        
        k1.metric("Total Companies", f"{len(comp_df)}")
        k2.metric("Average Company Score", f"{avg_comp_score:.1f}/100")
        k3.metric("Top Performing Company", f"{best_comp[:15]}..")
        k4.metric("Worst Performing Company", f"{worst_comp[:15]}..")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        # Advanced Chart 1: Treemap of Company -> Supplier
        if 'Supplier Name' in df.columns:
            tree_data = df.groupby(['Company', 'Supplier Name'])['Order Value'].sum().reset_index()
            tree_data = tree_data[tree_data['Order Value'] > 0]
            fig_tree = px.treemap(tree_data, path=['Company', 'Supplier Name'], values='Order Value',
                                  color='Order Value', color_continuous_scale='Purp',
                                  title="Volume Hierarchy")
            layout_tree = base_layout('Company & Supplier Volume Hierarchy (Treemap)')
            layout_tree.update(height=450, margin=dict(t=50, l=10, r=10, b=10))
            fig_tree.update_layout(**layout_tree)
            c1.plotly_chart(fig_tree, use_container_width=True)
            
        # Advanced Chart 2: Radar Chart
        top_5_comp = comp_df.nlargest(5, 'Order_Value')
        fig_radar = go.Figure()
        categories = ['Value Fill Rate', 'Qty Fill Rate', 'Score', 'Fulfillment Speed']
        for _, row in top_5_comp.iterrows():
            lead_speed = max(0, 100 - (row['Avg_Lead_Days'] * 10)) if pd.notna(row['Avg_Lead_Days']) else 0
            vals = [row['Val_Fill_Rate']*100, row['Qty_Fill_Rate']*100, row['Score'], lead_speed]
            vals.append(vals[0])
            cats = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals, theta=cats, fill='toself', name=row['Company'][:15]
            ))
        layout_radar = base_layout('Top 5 Companies Multi-Metric Radar')
        layout_radar.update(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=C_BORDER, linecolor=C_BORDER),
                angularaxis=dict(gridcolor=C_BORDER, linecolor=C_BORDER)
            ),
            height=450, showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        fig_radar.update_layout(**layout_radar)
        c2.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("### 🗃️ Company Detailed Scorecard")
        st.dataframe(
            comp_df.style.format({
                'Val_Fill_Rate': '{:.1%}', 'Qty_Fill_Rate': '{:.1%}', 'NS_Rate': '{:.1f}%', 'Avg_Lead_Days': '{:.1f}', 
                'Order_Value': '₹{:,.0f}', 'NS_Value': '₹{:,.0f}', 'Score': '{:.1f}'
            }).background_gradient(subset=['Score'], cmap='RdYlGn'),
            use_container_width=True, height=400
        )

with tab7:
    st.subheader("🔎 Single Item Deep Dive")
    if 'Item Name' not in df.columns or df.empty:
        st.warning("No item data available.")
    else:
        item_list = sorted(df['Item Name'].dropna().unique())
        selected_item = st.selectbox("🎯 Search and Select an Item to Analyze:", item_list)
        
        if selected_item:
            idf = df[df['Item Name'] == selected_item]
            
            total_times = len(idf)
            tot_o = idf['Orderqty'].sum()
            tot_r = idf['Received Qty'].sum()
            fill_r = tot_r / tot_o if tot_o > 0 else 0
            
            last_order = idf['Order Date'].max() if 'Order Date' in idf.columns else pd.NaT
            last_grn = idf['Grn Date'].max() if 'Grn Date' in idf.columns else pd.NaT
            sups = idf['Supplier Name'].nunique() if 'Supplier Name' in idf.columns else 0
            
            st.markdown("---")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Times Ordered", f"{total_times:,}")
            k2.metric("Total Ordered Qty", f"{tot_o:,.0f}")
            k3.metric("Total Received Qty", f"{tot_r:,.0f}", delta=f"{fill_r:.1%} Fill Rate")
            k4.metric("Active Suppliers", f"{sups}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Last Ordered Date", last_order.strftime('%Y-%m-%d') if pd.notna(last_order) else "N/A")
            c2.metric("Last Received Date", last_grn.strftime('%Y-%m-%d') if pd.notna(last_grn) else "N/A")
            avg_price = idf['Order Value'].sum() / tot_o if tot_o > 0 else 0
            c3.metric("Avg Price per Unit", f"₹{avg_price:,.2f}")
            
            st.markdown("---")
            c_left, c_right = st.columns(2)
            
            if 'Order Date' in idf.columns and not idf['Order Date'].isna().all():
                hist = idf.groupby(idf['Order Date'].dt.date).agg({'Orderqty':'sum', 'Received Qty':'sum'}).reset_index()
                fig_hist = px.bar(hist, x='Order Date', y=['Orderqty', 'Received Qty'], barmode='group',
                                  color_discrete_map={'Orderqty': C_ACCENT, 'Received Qty': C_GREEN})
                layout_hist = base_layout('Volume Over Time')
                layout_hist.update(height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                fig_hist.update_layout(**layout_hist)
                c_left.plotly_chart(fig_hist, use_container_width=True)
                
            if 'Supplier Name' in idf.columns:
                sup_break = idf.groupby('Supplier Name')['Orderqty'].sum().reset_index()
                fig_sb = px.pie(sup_break, values='Orderqty', names='Supplier Name', hole=0.4,
                                color_discrete_sequence=px.colors.sequential.Plasma)
                layout_sb = base_layout('Sourcing Breakdown (by Qty)')
                layout_sb.update(height=350, showlegend=False)
                fig_sb.update_layout(**layout_sb)
                c_right.plotly_chart(fig_sb, use_container_width=True)
                
            st.markdown(f"### 🗃️ Transaction History: {selected_item}")
            show_cols = [c for c in ['Order Date', 'Grn Date', 'Order Number', 'Supplier Name', 'Orderqty', 'Received Qty', 'Qty_Fill', 'Order Value', 'NS_Value'] if c in idf.columns]
            
            st.dataframe(
                idf[show_cols].style.format({
                    'Orderqty': '{:,.0f}', 'Received Qty': '{:,.0f}', 'Qty_Fill': '{:.1%}',
                    'Order Value': '₹{:,.0f}', 'NS_Value': '₹{:,.0f}',
                    'Order Date': lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '',
                    'Grn Date': lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
                }),
                use_container_width=True
            )
