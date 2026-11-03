# Skatteverket Tax Assistant (`k4-assistant`)

A comprehensive, specialized web application built with Streamlit to assist Swedish taxpayers in managing, calculating, and preparing their annual tax declarations for Skatteverket.

## 🚀 What can you do with this app?
This tool simplifies complex Swedish tax reporting by guiding you through your declaration with a formal interface that matches official branding.
- **K4 (Stocks, Funds, Crypto)**: Line-by-line itemization for all asset sales.
- **Cost Basis Helper**: Calculates complex average cost basis (*genomsnittsmetoden*) based on historical buy/sell events and automatically exports data to K4.
- **K5/K6 (Property Sales)**: Computes gains/losses for house and apartment sales.
- **K3 (Rental Income)**: Automatically applies standard and property-specific deductions.
- **Multi-Year Management**: Manage declarations across multiple tax years (2022–2026) in one dashboard.
- **Export Totals**: Generates official summary values formatted exactly for Skatteverket's e-service boxes.

## 🛠️ Getting Started

### Prerequisites
- [Install UV](https://docs.astral.sh/uv/getting-started/installation/)

### Installation
1. **Clone the repository**:
   ```bash
   git clone <YOUR_REPO_URL>
   cd k4-assistant
   ```
2. **Install dependencies**:
   ```bash
   uv sync
   ```
3. **Run the application**:
   ```bash
   uv run streamlit run src/app.py --server.port 8501
   ```
4. **Open in browser**:
   Navigate to [`http://localhost:8501`](http://localhost:8501)

## 📖 How to use
1. **Sign In**: Log in (mock) to save your portfolio holdings and tax declarations to your profile.
2. **Select Tax Year**: Choose the declaration year (e.g., 2025) from the sidebar.
3. **Questionnaire**: Check the boxes for the tax activities performed during that year (e.g., "Sold stocks", "Rented out property").
4. **Enter Data**: Fill out individual asset sales (K4) or transaction histories (Cost Basis Helper).
5. **Generate Summary**: View the official "Skatteverket Mirror" table to easily transfer the required box values to your official Skatteverket tax return.
