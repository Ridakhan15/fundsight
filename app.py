# app.py
import streamlit as st
import pandas as pd
import requests
from prophet import Prophet

st.set_page_config(page_title="FundSight", layout="wide")
st.title("📈 FundSight — Mutual Fund NAV Trends & Forecast")

# ---- Helper to get list of all mutual funds ----
@st.cache_data(ttl=86400)
def get_all_funds():
    url = "https://api.mfapi.in/mf"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return pd.DataFrame(r.json())  # has schemeCode & schemeName

# ---- Helper to fetch NAV data ----
@st.cache_data(ttl=3600)
def get_nav(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    j = r.json()
    name = j['meta']['scheme_name']
    df = pd.DataFrame(j['data'])
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['nav'] = df['nav'].astype(float)
    df = df.sort_values('date').reset_index(drop=True)
    return name, df

# ---- Fetch all funds ----
fund_list_df = get_all_funds()

# Sidebar: search & pick funds
st.sidebar.header("Select funds to compare")
selected_names = st.sidebar.multiselect(
    "Pick funds",
    fund_list_df['schemeName'].tolist(),
    default=fund_list_df['schemeName'].head(3).tolist()
)

# Create dict of selected funds (code: name)
FUNDS = {
    str(row['schemeCode']): row['schemeName']
    for _, row in fund_list_df[fund_list_df['schemeName'].isin(selected_names)].iterrows()
}

if not FUNDS:
    st.info("Select at least one fund from the sidebar.")
    st.stop()

# Build combined normalized series
dfs = {}
for code, friendly in FUNDS.items():
    _, df = get_nav(code)
    df = df.set_index('date')['nav']
    dfs[friendly] = df

combined = pd.concat(dfs, axis=1).sort_index().ffill()
norm = combined.divide(combined.iloc[0]).multiply(100)

# ---- Show normalized NAV comparison ----
st.subheader("📊 Normalized NAV Comparison (base = 100)")
st.line_chart(norm)

# ---- Latest NAV & % change ----
latest = combined.tail(1).T
yesterday = combined.shift(1).tail(1).T
change = ((latest - yesterday) / yesterday * 100).round(2)
metrics = pd.DataFrame({
    'Latest NAV': latest[latest.columns[0]].values,
    '1-day %': change[change.columns[0]].values
}, index=latest.index)
st.table(metrics)

# ---- Forecast ----
st.subheader("🔮 Forecast a selected fund")
to_forecast = st.selectbox("Choose fund to forecast", list(dfs.keys()))
days = st.slider("Days to forecast", 30, 180, 90)

if st.button("Run Forecast"):
    code = [k for k, v in FUNDS.items() if v == to_forecast][0]
    name, df = get_nav(code)
    df_prophet = df[['date', 'nav']].rename(columns={'date': 'ds', 'nav': 'y'})
    m = Prophet()
    m.fit(df_prophet)
    future = m.make_future_dataframe(periods=days)
    fcst = m.predict(future)
    fig = m.plot(fcst)
    st.pyplot(fig)
    st.write(fcst[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
