# 📈 US Broad Market Quantitative Index Factory

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Dash](https://img.shields.io/badge/Dash-Plotly-informational)](https://dash.plotly.com/)

## Overview
An end-to-end quantitative data pipeline and interactive dashboard for constructing, optimizing, and analyzing custom US Broad Market Indices. Moving beyond traditional market-cap weighting, this project implements a dynamic "Index Factory" to generate Thematic portfolios, Smart Beta (Inverse Volatility) strategies, and a Global Minimum Variance (GMV) optimized portfolio using `scipy`.

## Project Architecture
*   **`notebooks/01_Data_Collection_and_Cleaning.ipynb`**: Automated ingestion and classification of 3,000+ equities, extracting sector groupings, shares outstanding, and 10 years of split-adjusted historical pricing via the Yahoo Finance API.
*   **`notebooks/02_Custom_Index_Factory.ipynb`**: A vectorized Python engine that calculates 14 distinct indices. Includes automated outlier sanitization (Winsorization) to handle API data glitches and dynamic rebasing to a starting value of 100.
*   **`app.py`**: A fully interactive Dash/Plotly web application allowing users to dynamically compare cumulative returns, CAGR, Realized Volatility, Sharpe Ratios, and Maximum Drawdowns.

## Key Strategies Implemented
1.  **Core Benchmarks**: Total Market (MCW, Float-Adjusted, Equal-Weight).
2.  **Size & Concentration**: "The Goliath Index" (Top 50 EW), S&P 500 Proxy, Micro-Cap Moonshots.
3.  **Smart Beta & Risk Parity**: Inverse Volatility, High-Beta Speculative.
4.  **Mathematical Optimization**: Global Minimum Variance (SciPy SLSQP Optimizer).

## How to Run Locally
1. Clone the repository: `git clone https://github.com/YourUsername/US_Custom_Indices_Project.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Launch the dashboard: `python app.py`
4. Open your browser to `http://127.0.0.1:8050/`

## Methodology: The "How"
Building a robust index requires navigating real-world data traps. This pipeline implements several professional quantitative techniques:
* **Handling Corporate Actions:** Uses split-adjusted and dividend-adjusted closing prices to prevent massive artificial drawdowns caused by stock splits (e.g., Nvidia's 10-for-1 split).
* **Winsorization & Data Sanitization:** Free pricing APIs often contain phantom data glitches. This engine includes an automated outlier detection filter that drops any equity simulating an impossible market capitalization (>$10 Trillion), ensuring a mathematically pristine covariance matrix.
* **Mathematical Optimization:** The Global Minimum Variance (GMV) portfolio utilizes a SciPy `SLSQP` optimizer, constrained to keep asset weights between 0% and 100% (long-only) and summing to exactly 1.0.

## Key Insights: What the Output Tells Us
By dynamically comparing these indices in the Dash application, several major market narratives become visually apparent:
* **The Concentration Risk:** Comparing the *Total Market (MCW)* to the *Equal-Weighted (EW)* index visually demonstrates how heavily the top 5 mega-cap tech stocks have distorted the broader market performance.
* **The "Two Economies":** The *Pure Tech* and *Ex-Tech Economy* indices show a massive divergence, proving that traditional sectors (manufacturing, banking, retail) experienced drastically different realities than the software sector over the last decade.
* **Risk Mitigation in Action:** During severe market downturns (like the 2020 COVID crash or 2022 bear market), the *Global Minimum Variance* and *SWAN Defensive* indices successfully smooth out the volatility curve, protecting base capital much better than traditional market-cap weighting.

## Disclaimer
**For Educational Purposes Only.** The base holdings data utilized in this project was sourced directly from the public [Wilshire 5000 Index Fund Holdings](https://wilshire.com/product-literature/wilshire-5000-index-fund-holdings), with historical pricing data retrieved via Yahoo Finance. This repository and its accompanying web application do not constitute financial advice, investment recommendations, or an endorsement of any specific equity or trading strategy. The index methodologies and performance metrics calculated herein are strictly for academic and portfolio demonstration purposes.