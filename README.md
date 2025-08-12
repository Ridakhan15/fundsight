# FundSight

FundSight — Mutual Fund NAV Trends & Forecast

**What it is**
A small Streamlit app that fetches Indian mutual fund NAVs from `mfapi.in`, displays normalized NAV trends and allows forecasting using Prophet.

## Features
- Fetches real NAV history for Indian mutual funds (mfapi.in)
- Normalize NAVs (base = 100) for direct comparison
- Shows latest NAV and 1-day % change
- Forecast future NAV using Prophet (per fund)
- Streamlit UI (interactive)

## How to run (local)
1. Create & activate virtual environment:
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

2. Install dependencies:
```bash
pip install -r requirements.txt

3. Run the app (Streamlit):

bash
Copy
Edit
streamlit run app.py
Open the URL Streamlit shows (usually http://localhost:8501).

Notes
Do not commit API keys or .env files.

If Prophet fails to install on Windows, consider using Anaconda (conda) or ask for help.