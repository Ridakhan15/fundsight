📈 FundSight
Mutual Fund NAV Trends & Forecast

Overview
FundSight is a lightweight and interactive Streamlit app that fetches real-time Indian mutual fund NAV data from mfapi.in, visualizes trends, and provides future NAV forecasts using Facebook Prophet.

✨ Features
✅ Fetch historical NAV data for Indian mutual funds
✅ Normalize NAVs (base = 100) for direct performance comparison
✅ View latest NAV and 1-day percentage change
✅ Forecast future NAV trends for selected funds
✅ Clean, interactive Streamlit interface

🚀 Getting Started (Local Setup)
1. Clone this repository
bash
Copy
Edit
git clone https://github.com/yourusername/FundSight.git
cd FundSight
2. Create & activate a virtual environment
Windows:

bash
Copy
Edit
python -m venv venv
venv\Scripts\activate
Mac/Linux:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate
3. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Run the app
bash
Copy
Edit
streamlit run app.py
Once the server starts, open the link shown in your terminal (usually http://localhost:8501).

🛠 Notes
No API keys needed — data is fetched directly from mfapi.in

If Prophet fails to install on Windows, try:

Using Anaconda

Installing dependencies via:

bash
Copy
Edit
conda install -c conda-forge prophet
Do not commit sensitive files like .env or API keys (if added later).
