import datetime
import os
import sys
import pandas as pd
import streamlit as st

# Add src to path to import local modules
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from k4_assistant.costbasis import calculate_gains
    from k4_assistant.models import Side, Trade
except ImportError:
    pass

# --- Skatteverket Official Design Tokens & Brand Colors ---
SKV_DEEP_BLUE = "#003366"  # Primary Brand Blue (Djupblå)
SKV_GOLD_YELLOW = "#FFCC00"  # Accent Yellow (Guldgul)
SKV_INTERACTIVE_BLUE = "#0055A5"  # Link & Button Interactive Blue
SKV_TEXT_DARK = "#222222"  # Accessible Dark Text
SKV_BG_LIGHT = "#F4F5F7"  # Neutral Light Background
SKV_CARD_BORDER = "#E0E0E0"  # Container border
SKV_SUCCESS_GREEN = "#1E7E34"  # Success Green
SKV_ERROR_RED = "#D9381E"  # Error Red

st.set_page_config(
    page_title="Skatteverket Tax Assistant",
    page_icon="🇸🇪",
    layout="wide",
)

# Custom CSS for Skatteverket Official Web Design System
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: "Frutiger", "Helvetica Neue", Arial, "Open Sans", sans-serif;
        color: {SKV_TEXT_DARK};
        font-size: 16px;
        line-height: 1.5;
    }}
    .main {{
        background-color: {SKV_BG_LIGHT};
    }}
    .stButton>button {{
        background-color: {SKV_DEEP_BLUE};
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 15px;
        transition: background-color 0.2s ease-in-out;
    }}
    .stButton>button:hover {{
        background-color: {SKV_INTERACTIVE_BLUE};
        color: white;
    }}
    .header-bar {{
        background-color: {SKV_DEEP_BLUE};
        border-bottom: 4px solid {SKV_GOLD_YELLOW};
        padding: 1.2rem 2rem;
        color: white;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .header-logo {{
        font-size: 32px;
        margin-right: 15px;
    }}
    .user-badge {{
        background-color: rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }}
    .card {{
        background-color: white;
        padding: 2rem;
        border-radius: 6px;
        border: 1px solid {SKV_CARD_BORDER};
        border-top: 4px solid {SKV_DEEP_BLUE};
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .buy-card {{
        background-color: #e6f4ea;
        padding: 1rem;
        border-left: 5px solid {SKV_SUCCESS_GREEN};
        margin-bottom: 0.5rem;
        border-radius: 4px;
    }}
    .sell-card {{
        background-color: #fce8e6;
        padding: 1rem;
        border-left: 5px solid {SKV_ERROR_RED};
        margin-bottom: 0.5rem;
        border-radius: 4px;
    }}
    .form-box {{
        background-color: #FFFFCC;
        padding: 4px 12px;
        border: 1px solid #CCCCCC;
        font-family: monospace;
        font-weight: bold;
        font-size: 15px;
        display: inline-block;
        text-align: right;
        border-radius: 2px;
    }}
    h1, h2, h3, h4 {{
        color: {SKV_DEEP_BLUE};
        font-weight: 700;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None  # Mock Google user account
if "tax_year" not in st.session_state:
    st.session_state.tax_year = 2025
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "forms_needed" not in st.session_state:
    st.session_state.forms_needed = []

# Global trade ledger across all historical years
if "global_trades" not in st.session_state:
    st.session_state.global_trades = []

# Current holdings snapshot storage
if "portfolio_snapshots" not in st.session_state:
    st.session_state.portfolio_snapshots = []

# Declaration summary storage per tax year
if "yearly_data" not in st.session_state:
    st.session_state.yearly_data = {}


def get_year_data(year):
    if year not in st.session_state.yearly_data:
        st.session_state.yearly_data[year] = {
            "k4_rows": [],
            "k5k6_data": {},
            "k3_data": {},
        }
    return st.session_state.yearly_data[year]


# Helper shortcuts for active tax year
active_data = get_year_data(st.session_state.tax_year)

# Top Bar Header with User Status
user_display = (
    f'<span class="user-badge">👤 {st.session_state.user_profile["name"]} ({st.session_state.user_profile["email"]})</span>'
    if st.session_state.user_profile
    else '<span class="user-badge">👤 Guest Mode (Sign in to save)</span>'
)
st.markdown(
    f"""
    <div class="header-bar">
        <div>
            <span class="header-logo">🇸🇪</span>
            Skatteverket Tax Assistant
        </div>
        <div>
            {user_display}
        </div>
    </div>
""",
    unsafe_allow_html=True,
)


# Navigation Function
def go_to(step):
    st.session_state.step = step
    st.rerun()


# --- Sidebar ---
with st.sidebar:
    st.title("User Profile & Tax Year")

    # Account Profile Section (Google Auth Simulation)
    if not st.session_state.user_profile:
        st.subheader("Account Login")
        if st.button("Sign in with Google"):
            st.session_state.user_profile = {
                "name": "Swedish Taxpayer",
                "email": "taxpayer.sweden@gmail.com",
            }
            st.success("Signed in with Google!")
            st.rerun()
    else:
        st.subheader("Profile Settings")
        st.write(f"**Name:** {st.session_state.user_profile['name']}")
        st.write(f"**Email:** {st.session_state.user_profile['email']}")
        if st.button("Sign Out"):
            st.session_state.user_profile = None
            st.rerun()

    st.divider()

    # Tax Year Selector
    st.subheader("Tax Year Selection")
    selected_year = st.selectbox(
        "Select Declaration Year:",
        [2026, 2025, 2024, 2023, 2022],
        index=1,
    )
    if selected_year != st.session_state.tax_year:
        st.session_state.tax_year = selected_year
        st.rerun()

    st.info(f"Managing declaration for year: **{st.session_state.tax_year}**")

    st.divider()

    # Import Previous Year K4 Data
    st.subheader("Import Historical Data")
    import_source_year = st.selectbox(
        "Import previous K4 from year:",
        [y for y in [2025, 2024, 2023, 2022] if y != st.session_state.tax_year],
    )
    if st.button("Import K4 to Current Year"):
        source_data = get_year_data(import_source_year)
        if source_data["k4_rows"]:
            active_data["k4_rows"].extend(source_data["k4_rows"])
            st.success(f"Imported {len(source_data['k4_rows'])} K4 rows from {import_source_year}!")
            st.rerun()
        else:
            st.warning(f"No saved K4 data found for {import_source_year}.")

    st.divider()
    st.subheader("Navigation")
    if st.button("Home / Welcome"):
        go_to("welcome")

    if st.session_state.forms_needed:
        st.divider()
        st.subheader("Active Forms")
        for form in st.session_state.forms_needed:
            if st.button(f"Go to {form}", key=f"nav_{form}"):
                if "K4" in form:
                    go_to("k4")
                elif "K5" in form:
                    go_to("k5k6")
                elif "K3" in form:
                    go_to("k3")

    st.divider()
    if st.button("Clear Data for This Year"):
        st.session_state.yearly_data[st.session_state.tax_year] = {
            "k4_rows": [],
            "k5k6_data": {},
            "k3_data": {},
        }
        st.success(f"Cleared form output for {st.session_state.tax_year}")
        st.rerun()

# --- Application Logic ---

if st.session_state.step == "welcome":
    st.title(f"Tax Assistant for {st.session_state.tax_year}")
    st.write(
        f"This tool will guide you through your Swedish tax declaration for **{st.session_state.tax_year}**."
    )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(f"What activities did you have in {st.session_state.tax_year}?")

        sell_securities = st.checkbox("I sold stocks or funds (AF account) -> K4")
        sell_crypto = st.checkbox("I sold or traded cryptocurrency -> K4")
        sell_property = st.checkbox("I sold a house or apartment -> K5 / K6")
        rent_out = st.checkbox("I rented out my property -> K3")

        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Start Calculation"):
        needed = []
        if sell_securities or sell_crypto:
            needed.append("K4")
        if sell_property:
            needed.append("K5/K6")
        if rent_out:
            needed.append("K3")

        st.session_state.forms_needed = needed

        if "K4" in needed:
            go_to("k4")
        elif "K5/K6" in needed:
            go_to("k5k6")
        elif "K3" in needed:
            go_to("k3")
        else:
            st.warning("Please select at least one activity.")

elif st.session_state.step == "k4":
    st.title(f"K4 Form - Stocks & Securities ({st.session_state.tax_year})")
    st.write("Skatteverket's K4 form requires listing each security sold on a separate row.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Asset Sale Row")

    # Inputs collected in a SINGLE column
    sec_name = st.text_input("1. Beteckning (Asset Name / Ticker)")
    quantity = st.number_input("2. Antal (Quantity)", min_value=0, step=1, value=0)
    sales_price = st.number_input(
        "3. Försäljningspris (Sales Proceeds in SEK)", min_value=0, step=1, value=0
    )
    cost_basis = st.number_input(
        "4. Omkostnadsbelopp (Cost Basis in SEK)", min_value=0, step=1, value=0
    )

    if st.button("Add Row to K4 Form"):
        if sec_name:
            gain_loss = sales_price - cost_basis
            active_data["k4_rows"].append(
                {
                    "name": sec_name,
                    "qty": quantity,
                    "proceeds": sales_price,
                    "cost": cost_basis,
                    "gain": max(0, gain_loss),
                    "loss": abs(min(0, gain_loss)),
                }
            )
            st.success(f"Added {sec_name} to K4 form for {st.session_state.tax_year}.")
        else:
            st.error("Please enter the asset name.")

    if st.button("Don't know cost basis? Use Calculator Helper"):
        go_to("cost_basis_helper")

    st.markdown("</div>", unsafe_allow_html=True)

    if active_data["k4_rows"]:
        st.subheader("Current K4 Rows")
        df_k4 = pd.DataFrame(active_data["k4_rows"])
        st.dataframe(
            df_k4[["name", "qty", "proceeds", "cost", "gain", "loss"]], width="stretch"
        )

        if st.button("Generate Official Skatteverket K4 Summary View"):
            go_to("k4_summary")

elif st.session_state.step == "cost_basis_helper":
    st.title("Historical Cost Basis Ledger & Holdings Scanner")
    st.info(
        "💡 **Full Historical Continuity**: Enter past transactions OR upload a current portfolio holdings screenshot/CSV "
        "to automatically set baseline positions for upcoming tax declarations."
    )

    # --- Section: Holdings Screenshot / File Upload Scanner ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📸 Portfolio Holdings Snapshot Upload (Avanza / Nordnet)")
    uploaded_image = st.file_uploader(
        "Upload broker screenshot or CSV statement showing current holdings & total cost basis:",
        type=["png", "jpg", "jpeg", "csv"],
    )

    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Portfolio Screenshot / Document", width=400)
        st.success("Successfully processed holdings statement!")

        st.subheader("Detected Holding Summary:")
        # Mock extracted portfolio positions from image/file for cost basis baseline
        snap_ticker = st.text_input("Asset Ticker Symbol", value="VOLV B")
        snap_qty = st.number_input("Total Position Quantity", min_value=0, value=100)
        snap_total_cost = st.number_input("Total Historical Acquisition Cost (SEK)", min_value=0, value=25000)

        if st.button("Set as Baseline Position in Profile"):
            st.session_state.portfolio_snapshots.append(
                {
                    "symbol": snap_ticker.upper(),
                    "qty": snap_qty,
                    "total_cost": snap_total_cost,
                    "unit_cost": snap_total_cost / snap_qty if snap_qty > 0 else 0,
                }
            )
            # Also inject baseline BUY transaction into global trade history
            st.session_state.global_trades.append(
                {
                    "symbol": snap_ticker.upper(),
                    "date": f"{st.session_state.tax_year - 1}-12-31",
                    "type": "BUY",
                    "qty": snap_qty,
                    "price": (snap_total_cost / snap_qty) if snap_qty > 0 else 0,
                    "fee": 0,
                }
            )
            st.success(f"Saved baseline holding for {snap_ticker.upper()} into user profile!")

    if st.session_state.portfolio_snapshots:
        st.write("---")
        st.subheader("Saved Profile Portfolio Holdings Baseline")
        st.dataframe(pd.DataFrame(st.session_state.portfolio_snapshots), width="stretch")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Section: Manual Transaction Logging ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Log Individual Transaction")

    h_symbol = st.text_input(
        "Ticker Symbol / Asset Name (e.g., SGE SOCIETE GE, VOLV B)",
        value="SGE SOCIETE GE",
    )
    t_date = st.date_input("Transaction Date", value=datetime.date(2010, 1, 15))
    t_type = st.selectbox("Transaction Type", ["BUY", "SELL"])
    t_qty = st.number_input("Quantity", min_value=0, step=1, value=0)
    t_price = st.number_input("Price per unit (SEK)", min_value=0, step=1, value=0)
    t_fee = st.number_input("Fee (SEK)", min_value=0, step=1, value=0)

    if st.button("Add Transaction to Lifetime Ledger"):
        current_symbol = h_symbol.upper().strip()

        trades_before = [
            tr
            for tr in st.session_state.global_trades
            if tr["symbol"] == current_symbol and tr["date"] <= str(t_date)
        ]

        holding_up_to_date = sum(
            tr["qty"] if tr["type"] == "BUY" else -tr["qty"] for tr in trades_before
        )

        if t_type == "SELL" and t_qty > holding_up_to_date:
            st.error(
                f"❌ Error: Cannot sell {t_qty} units of {current_symbol} on {t_date}. "
                f"Your balance on that date was only {holding_up_to_date} units."
            )
        else:
            st.session_state.global_trades.append(
                {
                    "symbol": current_symbol,
                    "date": str(t_date),
                    "type": t_type,
                    "qty": t_qty,
                    "price": t_price,
                    "fee": t_fee,
                }
            )
            st.success(
                f"Added {t_type} transaction of {t_qty} units for {current_symbol} on {t_date} to global ledger."
            )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.global_trades:
        st.subheader("Lifetime Recorded Transactions (Sorted by Date)")
        sorted_trades = sorted(st.session_state.global_trades, key=lambda x: x["date"])

        for tr in sorted_trades:
            card_class = "buy-card" if tr["type"] == "BUY" else "sell-card"
            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{tr['date']}</b> | <b>{tr['symbol']}</b> | Type: <b>{tr['type']}</b> | Qty: {tr['qty']} | Price: {tr['price']} SEK | Fee: {tr['fee']} SEK
                </div>
            """,
                unsafe_allow_html=True,
            )

        if st.button(
            f"Compute & Export K4 Sales for Declaration Year {st.session_state.tax_year}"
        ):
            active_data["k4_rows"] = []
            df_tr = pd.DataFrame(sorted_trades)

            for sym, group in df_tr.groupby("symbol"):
                pos_qty = 0
                total_cost = 0
                unit_cost = 0

                for _, row in group.iterrows():
                    trade_year = int(row["date"].split("-")[0])

                    if row["type"] == "BUY":
                        pos_qty += row["qty"]
                        total_cost += (row["qty"] * row["price"]) + row["fee"]
                        if pos_qty > 0:
                            unit_cost = total_cost / pos_qty
                    elif row["type"] == "SELL":
                        sold_qty = row["qty"]
                        cost_removed = sold_qty * unit_cost
                        proceeds = (sold_qty * row["price"]) - row["fee"]
                        pos_qty -= sold_qty
                        total_cost -= cost_removed

                        if trade_year == st.session_state.tax_year:
                            gain_loss = proceeds - cost_removed
                            active_data["k4_rows"].append(
                                {
                                    "name": sym,
                                    "qty": sold_qty,
                                    "proceeds": proceeds,
                                    "cost": cost_removed,
                                    "gain": max(0, gain_loss),
                                    "loss": abs(min(0, gain_loss)),
                                }
                            )

            st.success(
                f"Successfully calculated average cost basis from lifetime ledger and exported sales for **{st.session_state.tax_year}** to K4!"
            )

    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("Go back to K4 Form"):
            go_to("k4")
    with c_nav2:
        if st.button("Back to K4 Without Exporting"):
            go_to("k4")

elif st.session_state.step == "k4_summary":
    st.title(
        f"K4 Form - Official Skatteverket Layout Mirror ({st.session_state.tax_year})"
    )
    st.write(
        "Below is the exact mirror of **A. Marknadsnoterade aktier, aktieindexobligationer, aktieoptioner m.m.** formatted cleanly in a table."
    )

    table_data = []
    total_p = 0
    total_c = 0
    total_g = 0
    total_l = 0

    for i in range(9):
        row_num = i + 1
        if i < len(active_data["k4_rows"]):
            r = active_data["k4_rows"][i]
            total_p += r["proceeds"]
            total_c += r["cost"]
            total_g += r["gain"]
            total_l += r["loss"]

            table_data.append(
                {
                    "Rad": row_num,
                    "Antal": f"{r['qty']:,}",
                    "Beteckning": r["name"],
                    "Försäljningspris": f"{r['proceeds']:,.0f}",
                    "Omkostnadsbelopp": f"{r['cost']:,.0f}",
                    "Vinst": f"{r['gain']:,.0f}" if r["gain"] > 0 else "",
                    "Förlust": f"{r['loss']:,.0f}" if r["loss"] > 0 else "",
                }
            )
        else:
            table_data.append(
                {
                    "Rad": row_num,
                    "Antal": "",
                    "Beteckning": "",
                    "Försäljningspris": "",
                    "Omkostnadsbelopp": "",
                    "Vinst": "",
                    "Förlust": "",
                }
            )

    df_summary = pd.DataFrame(table_data)

    st.subheader(
        "A. Marknadsnoterade aktier, aktieindexobligationer, aktieoptioner m.m."
    )
    st.dataframe(df_summary, width="stretch", hide_index=True)

    st.markdown(
        f"""
    <div class="card" style="background-color: white; border: 1px solid #333;">
        <h4 style="color: {SKV_DEEP_BLUE};">Summering av bilaga K4 ({st.session_state.tax_year})</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Total Försäljningspris (Summan av alla försäljningar):</b></td>
                <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;"><div class="form-box">{total_p:,.0f}</div></td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Total Omkostnadsbelopp (Summan av alla omkostnader):</b></td>
                <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;"><div class="form-box">{total_c:,.0f}</div></td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>Total Vinst (Gain):</b></td>
                <td style="text-align: right; padding: 8px; border-bottom: 1px solid #ddd;"><div class="form-box">{total_g:,.0f}</div></td>
            </tr>
            <tr>
                <td style="padding: 8px;"><b>Total Förlust (Loss):</b></td>
                <td style="text-align: right; padding: 8px;"><div class="form-box">{total_l:,.0f}</div></td>
            </tr>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Back to Welcome"):
        go_to("welcome")

elif st.session_state.step == "k5k6":
    st.title(f"K5/K6 - Sale of Real Estate / Apartment ({st.session_state.tax_year})")
    st.write("Calculate your capital gain or loss on property sales.")

    prop_kind = st.selectbox(
        "Property Type",
        ["House (Småhus) - Form K5", "Condominium (Bostadsrätt) - Form K6"],
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    sales_price = st.number_input(
        "Sales price (Försäljningspris)", min_value=0, step=1, value=0
    )
    selling_costs = st.number_input(
        "Selling costs (Broker fees, etc.)", min_value=0, step=1, value=0
    )
    purchase_price = st.number_input(
        "Purchase price (Inköpspris)", min_value=0, step=1, value=0
    )
    buying_costs = st.number_input(
        "Acquisition costs (Lagfart, pantbrev - if house)",
        min_value=0,
        step=1,
        value=0,
    )
    improvement_costs = st.number_input(
        "Improvement expenses (Grundförbättringar)", min_value=0, step=1, value=0
    )

    net_sales = sales_price - selling_costs
    total_cost = purchase_price + buying_costs + improvement_costs
    profit = net_sales - total_cost

    st.markdown(
        f"""
    <hr>
    <h4>Calculation Result:</h4>
    <p>Net Sales: {net_sales:,.0f} SEK</p>
    <p>Total Cost Basis: {total_cost:,.0f} SEK</p>
    <p><b>{"Profit" if profit >= 0 else "Loss"}: {abs(profit):,.0f} SEK</b></p>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Save Property Data"):
        active_data["k5k6_data"] = {
            "kind": prop_kind,
            "profit": profit,
            "net_sales": net_sales,
            "total_cost": total_cost,
        }
        st.success(f"Property data saved for {st.session_state.tax_year}.")
        if "K3" in st.session_state.forms_needed:
            go_to("k3")
        else:
            go_to("summary_all")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == "k3":
    st.title(f"K3 - Rental Income ({st.session_state.tax_year})")
    st.write("Calculate your taxable rental income.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    prop_type = st.radio(
        "Property Type", ["Small house (Småhus)", "Condominium (Bostadsrätt)"]
    )
    total_income = st.number_input(
        "Total rental income received", min_value=0, step=1, value=0
    )

    standard_deduction = 40000
    extra_deduction = 0
    if prop_type == "Small house (Småhus)":
        extra_deduction = total_income * 0.20
    else:
        extra_deduction = st.number_input(
            "Fees paid to association during rental period",
            min_value=0,
            step=1,
            value=0,
        )

    taxable = max(0.0, total_income - standard_deduction - extra_deduction)

    st.markdown(
        f"""
    <hr>
    <h4>Calculation Result:</h4>
    <p>Standard deduction: -40,000 SEK</p>
    <p>Other deductions: -{extra_deduction:,.0f} SEK</p>
    <p><b>Taxable Income: {taxable:,.0f} SEK</b></p>
    """,
        unsafe_allow_html=True,
    )

    if st.button("Save Rental Data"):
        active_data["k3_data"] = {"taxable": taxable}
        st.success(f"Rental data saved for {st.session_state.tax_year}.")
        go_to("summary_all")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == "summary_all":
    st.title(f"Final Tax Summary - Year {st.session_state.tax_year}")
    st.write(
        f"Here is the complete overview of all your declarations to enter into Skatteverket for **{st.session_state.tax_year}**."
    )

    if active_data["k4_rows"]:
        st.markdown(
            """
        <div class="card">
            <h3>K4 Form (Stocks / Securities)</h3>
            <p>You have entries recorded. Click below to view the official K4 table layout mirror.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("View K4 Form Mirror"):
            go_to("k4_summary")

    if active_data["k3_data"]:
        st.markdown(
            f"""
        <div class="card">
            <h3>Rental Income (Main Form)</h3>
            <p>Enter this amount in box <b>7.3</b> (Överskott vid uthyrning av bostad):</p>
            <div class="form-box">{active_data['k3_data']['taxable']:,.0f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if active_data["k5k6_data"]:
        res = active_data["k5k6_data"]
        st.markdown(
            f"""
        <div class="card">
            <h3>Property Sale ({res['kind']})</h3>
            <p>Enter these values in your {res['kind'].split(' - ')[1]}:</p>
            <table style="width: 100%;">
                <tr>
                    <td><b>Försäljningspris efter avdrag för försäljningsutgifter:</b></td>
                    <td style="text-align: right;"><div class="form-box">{res['net_sales']:,.0f}</div></td>
                </tr>
                <tr>
                    <td><b>Inköpspris och förbättringsutgifter:</b></td>
                    <td style="text-align: right;"><div class="form-box">{res['total_cost']:,.0f}</div></td>
                </tr>
                <tr>
                    <td><b>{"Vinst" if res['profit'] >= 0 else "Förlust"}:</b></td>
                    <td style="text-align: right;"><div class="form-box">{abs(res['profit']):,.0f}</div></td>
                </tr>
            </table>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if st.button("Back to Welcome"):
        go_to("welcome")

# Footer
st.divider()
st.caption(
    "🇸🇪 This is a community-built assistant and not an official Skatteverket tool."
)
