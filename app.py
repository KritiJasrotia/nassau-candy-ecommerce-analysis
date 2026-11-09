
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Nassau Candy Analytics",
    page_icon="🍬",
    layout="wide",
)

# ---------------- DESIGN ----------------
st.markdown("""
<style>
    .stApp { background: #F4F7FB; }
    [data-testid="stSidebar"] { background: #101B33; }
    [data-testid="stSidebar"] * { color: #FFFFFF; }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E1E8F0;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 2px 7px #17243D0D;
    }
    div[data-testid="stPlotlyChart"] {
        background: white;
        border: 1px solid #E1E8F0;
        border-radius: 12px;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(file_path):
    path = Path(file_path)

    if path.suffix.lower() == ".csv":
        try:
            data = pd.read_csv(path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            data = pd.read_csv(path, encoding="latin-1")
    else:
        data = pd.read_excel(path)

    data.columns = data.columns.astype(str).str.strip()
    return data


folder = Path(__file__).parent
files = []

for pattern in ("*.csv", "*.xlsx", "*.xls"):
    files.extend(folder.glob(pattern))

files.sort(key=lambda f: (
    "nassau" not in f.name.lower(),
    "clean" not in f.name.lower(),
    f.name.lower()
))

if not files:
    st.error(
        "No CSV or Excel dataset found. Place your Nassau Candy "
        "dataset in the same folder as app.py."
    )
    st.stop()

# If multiple datasets exist, prefer the Nassau Candy cleaned file.
data_file = files[0]

try:
    df = load_data(str(data_file))
except Exception as error:
    st.error(f"Could not load dataset: {error}")
    st.stop()


def get_column(*names):
    normalized = {
        c.lower().replace("_", " ").strip(): c
        for c in df.columns
    }
    for name in names:
        key = name.lower().replace("_", " ").strip()
        if key in normalized:
            return normalized[key]
    return None


COL = {
    "sales": get_column("Sales"),
    "profit": get_column("Gross Profit", "Profit"),
    "orders": get_column("Order ID", "Order_ID"),
    "units": get_column("Units", "Quantity"),
    "product": get_column("Product Name", "Product"),
    "region": get_column("Region"),
    "division": get_column("Division"),
    "ship": get_column("Ship Mode", "Shipping Mode"),
    "order_date": get_column("Order Date", "Order_Date"),
    "ship_date": get_column("Ship Date", "Ship_Date"),
    "shipping_days": get_column("Shipping Days", "Shipping_Days"),
}

required = [
    "sales", "profit", "orders", "units",
    "product", "region", "division", "ship"
]

missing = [key for key in required if COL[key] is None]

if missing:
    st.error("Required dataset columns are missing.")
    st.write("Detected columns:", list(df.columns))
    st.stop()

# Convert numeric columns
for key in ["sales", "profit", "units"]:
    df[COL[key]] = pd.to_numeric(df[COL[key]], errors="coerce").fillna(0)

# Date processing
for key in ["order_date", "ship_date"]:
    if COL[key]:
        df[COL[key]] = pd.to_datetime(
            df[COL[key]], errors="coerce", dayfirst=True
        )

if COL["shipping_days"] is None:
    if COL["order_date"] and COL["ship_date"]:
        df["Shipping Days"] = (
            df[COL["ship_date"]] - df[COL["order_date"]]
        ).dt.days
        COL["shipping_days"] = "Shipping Days"
else:
    df[COL["shipping_days"]] = pd.to_numeric(
        df[COL["shipping_days"]], errors="coerce"
    )

if COL["order_date"]:
    df["__Year"] = df[COL["order_date"]].dt.year
    df["__Month"] = (
        df[COL["order_date"]].dt.to_period("M").dt.to_timestamp()
    )
else:
    df["__Year"] = pd.NA
    df["__Month"] = pd.NaT

# ---------------- HEADER ----------------
st.title("🍬 Nassau Candy Analytics")
st.caption(
    "E-Commerce Sales, Profitability & Product Performance Dashboard"
)
st.caption(f"Dataset: {data_file.name} · {len(df):,} records")

# ---------------- FILTERS ----------------
def reset_filters():
    for key in ["years", "regions", "divisions", "shipping_modes", "top_n"]:
        st.session_state.pop(key, None)


with st.sidebar:
    st.title("Dashboard Filters")
    st.caption("Choose filters to explore your data.")

    st.button(
        "↻ Reset Filters",
        use_container_width=True,
        on_click=reset_filters,
    )

    if df["__Year"].notna().any():
        year_options = sorted(
            int(y) for y in df["__Year"].dropna().unique()
        )
        years = st.multiselect(
            "Year", year_options, default=year_options, key="years"
        )
    else:
        years = []

    region_options = sorted(df[COL["region"]].dropna().unique().tolist())
    regions = st.multiselect(
        "Region", region_options,
        default=region_options, key="regions"
    )

    division_options = sorted(
        df[COL["division"]].dropna().unique().tolist()
    )
    divisions = st.multiselect(
        "Division", division_options,
        default=division_options, key="divisions"
    )

    shipping_options = sorted(
        df[COL["ship"]].dropna().unique().tolist()
    )
    shipping_modes = st.multiselect(
        "Ship Mode", shipping_options,
        default=shipping_options, key="shipping_modes"
    )

# Apply filters to all dashboard sections
filtered = df.copy()

if df["__Year"].notna().any():
    filtered = filtered[filtered["__Year"].isin(years)]

filtered = filtered[filtered[COL["region"]].isin(regions)]
filtered = filtered[filtered[COL["division"]].isin(divisions)]
filtered = filtered[filtered[COL["ship"]].isin(shipping_modes)]

if filtered.empty:
    st.warning("No matching records. Please change your filters.")
    st.stop()

# ---------------- KPI CARDS ----------------
sales = filtered[COL["sales"]].sum()
profit = filtered[COL["profit"]].sum()
orders = filtered[COL["orders"]].nunique()
units = filtered[COL["units"]].sum()
margin = profit / sales * 100 if sales else 0

if COL["shipping_days"]:
    avg_shipping = filtered[COL["shipping_days"]].mean()
else:
    avg_shipping = None

st.subheader("Performance Overview")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Total Sales", f"${sales:,.2f}")
k2.metric("Gross Profit", f"${profit:,.2f}")
k3.metric("Total Orders", f"{orders:,}")
k4.metric("Total Units", f"{units:,.0f}")
k5.metric("Profit Margin", f"{margin:.2f}%")
k6.metric(
    "Avg. Recorded Shipping Days",
    f"{avg_shipping:,.1f}" if pd.notna(avg_shipping) else "N/A"
)

# ---------------- CHART STYLE ----------------
def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=15, r=15, t=55, b=20),
        font=dict(family="Arial", size=12, color="#27364B"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E9EEF5")
    return fig


# ---------------- SALES TRENDS ----------------
st.subheader("Sales & Profit Trends")
left, right = st.columns([1.5, 1])

with left:
    if COL["order_date"] and filtered["__Month"].notna().any():
        monthly = (
            filtered.dropna(subset=["__Month"])
            .groupby("__Month", as_index=False)
            .agg(
                Sales=(COL["sales"], "sum"),
                Gross_Profit=(COL["profit"], "sum"),
            )
            .sort_values("__Month")
        )

        long_data = monthly.melt(
            id_vars="__Month",
            value_vars=["Sales", "Gross_Profit"],
            var_name="Metric",
            value_name="Amount",
        )
        long_data["Metric"] = long_data["Metric"].replace(
            {"Gross_Profit": "Gross Profit"}
        )

        fig = px.line(
            long_data,
            x="__Month",
            y="Amount",
            color="Metric",
            markers=True,
            color_discrete_map={
                "Sales": "#3478F6",
                "Gross Profit": "#18A999",
            },
            title="Monthly Sales & Gross Profit",
            labels={
                "__Month": "Month",
                "Amount": "Amount ($)",
                "Metric": "",
            },
        )
        fig.update_xaxes(tickformat="%b %Y")
        st.plotly_chart(
            style_chart(fig), use_container_width=True
        )
    else:
        st.info("Monthly trends require a valid Order Date column.")

with right:
    region_data = (
        filtered.groupby(COL["region"], as_index=False)
        .agg(
            Sales=(COL["sales"], "sum"),
            Gross_Profit=(COL["profit"], "sum"),
        )
        .sort_values("Sales", ascending=False)
    )

    fig = px.bar(
        region_data,
        x=COL["region"],
        y="Sales",
        color=COL["region"],
        color_discrete_sequence=[
            "#267C9A", "#2FA7A0", "#54CFA5", "#7A8FE8"
        ],
        title="Sales by Region",
        labels={COL["region"]: "Region", "Sales": "Sales ($)"},
        hover_data={"Gross_Profit": ":,.2f"},
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(
        style_chart(fig), use_container_width=True
    )

# ---------------- PRODUCT PERFORMANCE ----------------
st.subheader("Product Performance")

products = (
    filtered.groupby(COL["product"], as_index=False)
    .agg(
        Sales=(COL["sales"], "sum"),
        Gross_Profit=(COL["profit"], "sum"),
        Units=(COL["units"], "sum"),
        Orders=(COL["orders"], "nunique"),
    )
)

products["Profit Margin (%)"] = (
    products["Gross_Profit"]
    / products["Sales"].replace(0, pd.NA) * 100
).fillna(0)

products["Profit per Unit"] = (
    products["Gross_Profit"]
    / products["Units"].replace(0, pd.NA)
).fillna(0)

search_col, top_col = st.columns([2, 1])

with search_col:
    search = st.text_input(
        "Search products",
        placeholder="Enter a product name..."
    )

with top_col:
    top_n = st.selectbox(
        "Number of products",
        [5, 10, 15],
        index=1,
        key="top_n",
    )

visible = products.copy()

if search.strip():
    visible = visible[
        visible[COL["product"]].astype(str).str.contains(
            search.strip(), case=False, na=False
        )
    ]

if visible.empty:
    st.info("No products match your search.")
else:
    p1, p2 = st.columns(2)

    with p1:
        top_sales = visible.nlargest(top_n, "Sales").sort_values("Sales")
        fig = px.bar(
            top_sales,
            x="Sales",
            y=COL["product"],
            orientation="h",
            color="Sales",
            color_continuous_scale=["#B8E4E3", "#267C9A"],
            title=f"Top {top_n} Products by Sales",
            labels={"Sales": "Sales ($)", COL["product"]: "Product"},
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(
            style_chart(fig, 430), use_container_width=True
        )

    with p2:
        top_profit = (
            visible.nlargest(top_n, "Gross_Profit")
            .sort_values("Gross_Profit")
        )
        fig = px.bar(
            top_profit,
            x="Gross_Profit",
            y=COL["product"],
            orientation="h",
            color="Gross_Profit",
            color_continuous_scale=["#B8E4E3", "#159A9C"],
            title=f"Top {top_n} Products by Gross Profit",
            labels={
                "Gross_Profit": "Gross Profit ($)",
                COL["product"]: "Product",
            },
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(
            style_chart(fig, 430), use_container_width=True
        )

    low_margin = (
        visible.nsmallest(top_n, "Profit Margin (%)")
        .sort_values("Profit Margin (%)")
    )
    fig = px.bar(
        low_margin,
        x="Profit Margin (%)",
        y=COL["product"],
        orientation="h",
        color="Profit Margin (%)",
        color_continuous_scale=["#E8A34A", "#2FA7A0"],
        title=f"Lowest {min(top_n, len(low_margin))} Product Margins",
        labels={
            "Profit Margin (%)": "Profit Margin (%)",
            COL["product"]: "Product",
        },
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(
        style_chart(fig, 380), use_container_width=True
    )

    st.markdown("### Product Summary")

    table = visible.sort_values("Sales", ascending=False).copy()
    table["Sales"] = table["Sales"].map(lambda x: f"${x:,.2f}")
    table["Gross_Profit"] = table["Gross_Profit"].map(
        lambda x: f"${x:,.2f}"
    )
    table["Profit Margin (%)"] = table["Profit Margin (%)"].map(
        lambda x: f"{x:.2f}%"
    )
    table["Profit per Unit"] = table["Profit per Unit"].map(
        lambda x: f"${x:,.2f}"
    )
    table["Units"] = table["Units"].map(lambda x: f"{x:,.0f}")
    table.rename(
        columns={"Gross_Profit": "Gross Profit"}, inplace=True
    )

    st.dataframe(
        table, use_container_width=True, hide_index=True
    )

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download filtered data as CSV",
    data=filtered.drop(
        columns=["__Year", "__Month"], errors="ignore"
    ).to_csv(index=False).encode("utf-8"),
    file_name="nassau_candy_filtered_data.csv",
    mime="text/csv",
)

# ---------------- DYNAMIC INSIGHTS ----------------
st.subheader("Business Insights")

region_leader = region_data.sort_values(
    "Sales", ascending=False
).iloc[0]

top_product = products.sort_values(
    "Sales", ascending=False
).iloc[0]

division_data = (
    filtered.groupby(COL["division"], as_index=False)
    .agg(Sales=(COL["sales"], "sum"))
    .sort_values("Sales", ascending=False)
)

division_leader = division_data.iloc[0]

lowest_margin = products.sort_values(
    "Profit Margin (%)", ascending=True
).iloc[0]

st.info(
    f"**Leading region:** {region_leader[COL['region']]} "
    f"with ${region_leader['Sales']:,.2f} in sales."
)

st.info(
    f"**Top product:** {top_product[COL['product']]} "
    f"with ${top_product['Sales']:,.2f} in sales."
)

st.info(
    f"**Leading division:** {division_leader[COL['division']]} "
    f"by sales in the current selection."
)

st.info(
    f"**Margin to review:** {lowest_margin[COL['product']]} "
    f"has a {lowest_margin['Profit Margin (%)']:.2f}% profit margin."
)

st.subheader("Business Recommendations")

st.markdown("""
- Protect sales in high-performing regions and explore growth opportunities elsewhere.
- Review pricing and costs for products with low profit margins.
- Use monthly sales patterns to support inventory planning.
- Investigate unusually high recorded shipping times using the underlying order records.
""")

with st.expander("About this dashboard"):
    st.write(
        "Built using Python, Pandas, Streamlit and Plotly. "
        "The filters update the KPIs, charts, product table and insights. "
        "Shipping-time values are shown as recorded in the source dataset; "
        "they should not automatically be interpreted as verified delivery delays."
    )
    st.write(f"Showing {len(filtered):,} of {len(df):,} records.")
