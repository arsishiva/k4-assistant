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
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .header-logo {{
        font-size: 32px;
        margin-right: 15px;
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
    <div class="header-bar">
        <span class="header-logo">🇸🇪</span>
        Skatteverket Tax Assistant
    </div>
""",
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "forms_needed" not in st.session_state:
    st.session_state.forms_needed = []
if "k4_rows" not in st.session_state:
    st.session_state.k4_rows = []
if "helper_trades" not in st.session_state:
    st.session_state.helper_trades = []
if "k5k6_data" not in st.session_state:
    st.session_state.k5k6_data = {}
if "k3_data" not in st.session_state:
    st.session_state.k3_data = {}


# --- Navigation ---
def go_to(step):
    st.session_state.step = step
    st.rerun()


# --- Sidebar ---
with st.sidebar:
    st.title("Navigation")
    if st.button("Home"):
        go_to("welcome")

    st.divider()
    st.subheader("Active Forms")
    if not st.session_state.forms_needed:
        st.write("No forms selected yet.")
    for form in st.session_state.forms_needed:
        if st.button(f"Go to {form}", key=f"nav_{form}"):
            if "K4" in form:
                go_to("k4")
            elif "K5" in form:
                go_to("k5k6")
            elif "K3" in form:
                go_to("k3")

    st.divider()
    if st.button("Clear All Data"):
        st.session_state.clear()
        st.rerun()

# --- Application Logic ---

if st.session_state.step == "welcome":
    st.title("Welcome to your Tax Assistant")
    st.write(
        "This tool will guide you through your Swedish tax declaration for the 2025 tax year with Skatteverket's design style."
    )

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("What did you do in 2025?")

        c1, c2 = st.columns(2)
        with c1:
            sell_securities = st.checkbox("I sold stocks or funds (AF account) -> K4")
            sell_crypto = st.checkbox("I sold or traded cryptocurrency -> K4")
            sell_property = st.checkbox("I sold a house or apartment -> K5 / K6")
        with c2:
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
    st.title("K4 Form - Stocks & Securities (Line-by-Line)")
    st.write(
        "Skatteverket's K4 form requires listing each security sold on a separate row with its specific quantity, proceeds, and cost basis."
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Asset Sale Row")

    col1, col2 = st.columns(2)
    with col1:
        sec_name = st.text_input("1. Beteckning (Asset Name / Ticker)")
        quantity = st.number_input("2. Antal (Quantity)", min_value=0, step=1, value=0)
    with col2:
        sales_price = st.number_input("3. Försäljningspris (Sales Proceeds in SEK)", min_value=0, step=1, value=0)
        cost_basis = st.number_input("4. Omkostnadsbelopp (Cost Basis in SEK)", min_value=0, step=1, value=0)

    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        if st.button("Add Row to K4 Form"):
            if sec_name:
                gain_loss = sales_price - cost_basis
                st.session_state.k4_rows.append(
                    {
                        "name": sec_name,
                        "qty": quantity,
                        "proceeds": sales_price,
                        "cost": cost_basis,
                        "gain": max(0, gain_loss),
                        "loss": abs(min(0, gain_loss)),
                    }
                )
                st.success(f"Added {sec_name} to K4 form.")
            else:
                st.error("Please enter the asset name.")
    with c_btn2:
        if st.button("Don't know cost basis?"):
            go_to("cost_basis_helper")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.k4_rows:
        st.subheader("Current K4 Rows")
        df_k4 = pd.DataFrame(st.session_state.k4_rows)
        st.dataframe(df_k4[["name", "qty", "proceeds", "cost", "gain", "loss"]], width="stretch")

        if st.button("Generate Official Skatteverket K4 Summary View"):
            go_to("k4_summary")

elif st.session_state.step == "cost_basis_helper":
    st.title("Cost Basis Calculator Helper")
    st.write(
        "Calculate cost basis per individual ticker symbol using the average cost method (*genomsnittsmetoden*). Add your buys and sells below."
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    h_symbol = st.text_input("Ticker Symbol / Asset Name (e.g., SGE SOCIETE GE, VOLV B)", value="SGE SOCIETE GE")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        t_type = st.selectbox("Transaction Type", ["BUY", "SELL"])
        t_qty = st.number_input("Quantity", min_value=0, step=1, value=0)
    with col_b2:
        t_price = st.number_input("Price per unit (SEK)", min_value=0, step=1, value=0)
        t_fee = st.number_input("Fee (SEK)", min_value=0, step=1, value=0)

    if st.button("Add Transaction"):
        st.session_state.helper_trades.append(
            {"symbol": h_symbol.upper(), "type": t_type, "qty": t_qty, "price": t_price, "fee": t_fee}
        )
        st.success(f"Added {t_type} transaction for {h_symbol.upper()}.")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.helper_trades:
        st.subheader("Recorded Transactions (Color-coded)")
        for tr in st.session_state.helper_trades:
            card_class = "buy-card" if tr["type"] == "BUY" else "sell-card"
            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{tr["symbol"]}</b> | Type: <b>{tr["type"]}</b> | Qty: {tr["qty"]} | Price: {tr["price"]} SEK | Fee: {tr["fee"]} SEK
                </div>
            """,
                unsafe_allow_html=True,
            )

        if st.button("Calculate & Export to K4 per Ticker"):
            df_tr = pd.DataFrame(st.session_state.helper_trades)
            for sym, group in df_tr.groupby("symbol"):
                pos_qty = 0
                total_cost = 0
                unit_cost = 0

                for _, row in group.iterrows():
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

                        gain_loss = proceeds - cost_removed
                        st.session_state.k4_rows.append(
                            {
                                "name": sym,
                                "qty": sold_qty,
                                "proceeds": proceeds,
                                "cost": cost_removed,
                                "gain": max(0, gain_loss),
                                "loss": abs(min(0, gain_loss)),
                            }
                        )

            st.success("Calculated and exported individual ticker rows to K4 form!")

    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        if st.button("Go back to K4 Form"):
            go_to("k4")
    with c_nav2:
        if st.button("Back to K4 Without Exporting"):
            go_to("k4")

elif st.session_state.step == "k4_summary":
    st.title("K4 Form - Official Skatteverket Layout Mirror")
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
        if i < len(st.session_state.k4_rows):
            r = st.session_state.k4_rows[i]
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

    st.subheader("A. Marknadsnoterade aktier, aktieindexobligationer, aktieoptioner m.m.")
    st.dataframe(df_summary, width="stretch", hide_index=True)

    st.markdown(
        f"""
    <div class="card" style="background-color: white; border: 1px solid #333;">
        <h4 style="color: {SKV_DEEP_BLUE};">Summering av bilaga K4</h4>
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
    st.title("K5/K6 - Sale of Real Estate / Apartment")
    st.write("Calculate your capital gain or loss on property sales.")

    prop_kind = st.selectbox("Property Type", ["House (Småhus) - Form K5", "Condominium (Bostadsrätt) - Form K6"])

    st.markdown('<div class="card">', unsafe_allow_html=True)
    sales_price = st.number_input("Sales price (Försäljningspris)", min_value=0, step=1, value=0)
    selling_costs = st.number_input("Selling costs (Broker fees, etc.)", min_value=0, step=1, value=0)

    purchase_price = st.number_input("Purchase price (Inköpspris)", min_value=0, step=1, value=0)
    buying_costs = st.number_input("Acquisition costs (Lagfart, pantbrev - if house)", min_value=0, step=1, value=0)
    improvement_costs = st.number_input("Improvement expenses (Grundförbättringar)", min_value=0, step=1, value=0)

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
        st.session_state.k5k6_data = {
            "kind": prop_kind,
            "profit": profit,
            "net_sales": net_sales,
            "total_cost": total_cost,
        }
        st.success("Property data saved.")
        if "K3" in st.session_state.forms_needed:
            go_to("k3")
        else:
            go_to("summary_all")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == "k3":
    st.title("K3 - Rental Income")
    st.write("Calculate your taxable rental income.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    prop_type = st.radio("Property Type", ["Small house (Småhus)", "Condominium (Bostadsrätt)"])
    total_income = st.number_input("Total rental income received", min_value=0, step=1, value=0)

    standard_deduction = 40000
    extra_deduction = 0
    if prop_type == "Small house (Småhus)":
        extra_deduction = total_income * 0.20
    else:
        extra_deduction = st.number_input("Fees paid to association during rental period", min_value=0, step=1, value=0)

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
        st.session_state.k3_data = {"taxable": taxable}
        st.success("Rental data saved.")
        go_to("summary_all")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.step == "summary_all":
    st.title("Final Tax Summary - All Forms")
    st.write("Here is the complete overview of all your declarations to enter into Skatteverket.")

    if st.session_state.k4_rows:
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

    if st.session_state.k3_data:
        st.markdown(
            f"""
        <div class="card">
            <h3>Rental Income (Main Form)</h3>
            <p>Enter this amount in box <b>7.3</b> (Överskott vid uthyrning av bostad):</p>
            <div class="form-box">{st.session_state.k3_data["taxable"]:,.0f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if st.session_state.k5k6_data:
        res = st.session_state.k5k6_data
        st.markdown(
            f"""
        <div class="card">
            <h3>Property Sale ({res["kind"]})</h3>
            <p>Enter these values in your {res["kind"].split(" - ")[1]}:</p>
            <table style="width: 100%;">
                <tr>
                    <td><b>Försäljningspris efter avdrag för försäljningsutgifter:</b></td>
                    <td style="text-align: right;"><div class="form-box">{res["net_sales"]:,.0f}</div></td>
                </tr>
                <tr>
                    <td><b>Inköpspris och förbättringsutgifter:</b></td>
                    <td style="text-align: right;"><div class="form-box">{res["total_cost"]:,.0f}</div></td>
                </tr>
                <tr>
                    <td><b>{"Vinst" if res["profit"] >= 0 else "Förlust"}:</b></td>
                    <td style="text-align: right;"><div class="form-box">{abs(res["profit"]):,.0f}</div></td>
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
st.caption("🇸🇪 This is a community-built assistant and not an official Skatteverket tool.")
