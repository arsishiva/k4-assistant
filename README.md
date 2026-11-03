# Skatteverket Tax Assistant (`k4-assistant`)

A specialized web application built with Streamlit that assists Swedish taxpayers in calculating, formatting, and filling out their Swedish tax declarations (Skatteverket) for the 2025 tax year.

## Features
- **Skatteverket Design System**: Styled with official red branding (`#E30613`), high-contrast UI cards, and official tax box formatting.
- **Multi-Form Guidance**: Questionnaire workflow to route users to the correct tax forms (**K4** for stocks/funds/crypto, **K5/K6** for property sales, and **K3** for rental income).
- **K4 Official Form Mirror**: Line-by-line itemization matching Skatteverket's official Section A paper and digital forms (Rows 1–9 with exact column layouts for Antal, Beteckning, Försäljningspris, Omkostnadsbelopp, Vinst, and Förlust).
- **Cost Basis Calculator Helper**: Interactive average cost calculation tool (*genomsnittsmetoden*) with color-coded buy/sell transaction cards that automatically export computed results per ticker symbol directly to the K4 form.

## Running Locally

1. Install dependencies using `uv`:
   ```bash
   uv sync
   ```
2. Run the Streamlit application:
   ```bash
   uv run streamlit run src/app.py --server.port 8501
   ```
3. Open your browser at:
   [`http://localhost:8501`](http://localhost:8501)
