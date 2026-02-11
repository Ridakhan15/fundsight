# ──────────────────────────────────────────────────────────────────────────────
# FundSight – Mutual‑Fund NAV Trends, Comparison & Forecast
#   • Free data from https://api.mfapi.in
#   • Interactive Plotly charts
#   • Prophet forecasting
#   • Auto‑adjusts the start‑date when the chosen window would be empty
#   • Robust handling of missing / empty data
# ──────────────────────────────────────────────────────────────────────────────

import datetime as dt
from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from prophet import Prophet

# ──────────────────────────────────────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FundSight – Mutual‑Fund Dashboard",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded",
)

st.title("📈 FundSight — Mutual Fund NAV Trends & Forecast")

# ──────────────────────────────────────────────────────────────────────────────
# Helper: generic API getter (with simple error handling)
# ──────────────────────────────────────────────────────────────────────────────
def _api_get(url: str) -> dict | None:
    """GET JSON from MFAPI; returns None and shows an error message on failure."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        st.error(f"❌  API request failed – *{exc}*")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Cached: list of all funds (once per day)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86_400, show_spinner=False)
def get_all_funds() -> pd.DataFrame:
    payload = _api_get("https://api.mfapi.in/mf")
    if payload is None:                     # error already shown in _api_get
        st.stop()
    df = pd.DataFrame(payload)
    df.rename(
        columns={"schemeCode": "scheme_code", "schemeName": "scheme_name"},
        inplace=True,
    )
    return df


# ──────────────────────────────────────────────────────────────────────────────
# Cached: NAV history for a single scheme (hourly)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3_600, show_spinner=False)
def get_nav(scheme_code: str) -> Tuple[str, pd.DataFrame]:
    """
    Fetch NAV history for a scheme.

    Returns (scheme_name, df) where *df* has columns ['date', 'nav'].
    If the scheme has no historical data an **empty** DataFrame is returned
    together with a friendly info banner (so the app never crashes).
    """
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    payload = _api_get(url)
    if payload is None:
        st.stop()

    name = payload["meta"]["scheme_name"]
    raw_df = pd.DataFrame(payload.get("data", []))

    if raw_df.empty:
        st.info(
            f"⚠️  No NAV history found for scheme {scheme_code} – it may be a brand‑new fund."
        )
        return name, pd.DataFrame(columns=["date", "nav"])

    raw_df["date"] = pd.to_datetime(raw_df["date"], format="%d-%m-%Y")
    raw_df["nav"] = pd.to_numeric(raw_df["nav"], errors="coerce")
    raw_df = raw_df.sort_values("date").reset_index(drop=True)
    return name, raw_df[["date", "nav"]]


# ──────────────────────────────────────────────────────────────────────────────
# Helper: safe normalisation (works even when df is empty)
# ──────────────────────────────────────────────────────────────────────────────
def safe_normalise(df: pd.DataFrame, base_date: pd.Timestamp) -> pd.DataFrame:
    """
    Normalise every column to 100 on ``base_date``.
    Returns an empty DataFrame unchanged if ``df`` is empty.
    """
    if df.empty:
        return df

    if base_date not in df.index:
        base_date = df.index[0]

    base_vals = df.loc[base_date]
    return df.div(base_vals).multiply(100)


# ──────────────────────────────────────────────────────────────────────────────
# Helper: period‑returns (graceful handling of empty input)
# ──────────────────────────────────────────────────────────────────────────────
def period_returns(
    df: pd.DataFrame, periods: List[Tuple[str, pd.Timestamp]]
) -> pd.DataFrame:
    """
    Compute % returns for each fund over the supplied periods.

    Returns an empty DataFrame when the input ``df`` is empty.
    """
    if df.empty:
        return pd.DataFrame(columns=[label for label, _ in periods])

    latest = df.iloc[-1]
    rows = {}
    for label, start in periods:
        if start < df.index[0]:
            rows[label] = pd.Series(
                [float("nan")] * df.shape[1], index=df.columns
            )
            continue
        price_start = df.loc[df.index <= start].iloc[-1]
        rows[label] = ((latest / price_start - 1) * 100).round(2)

    return pd.DataFrame(rows).T


# ──────────────────────────────────────────────────────────────────────────────
# Helper: build the combined DataFrame and auto‑adjust start‑date if needed
# ──────────────────────────────────────────────────────────────────────────────
def build_combined(
    series_dict: Dict[str, pd.Series],
    start_date: dt.date,
    end_date: dt.date,
) -> Tuple[pd.DataFrame, str]:
    """
    Concatenate series, apply the user‑chosen window,
    and if that window is empty automatically adjust the start date
    to the earliest common observation among the selected funds.

    Returns
    -------
    combined_df : pd.DataFrame
        Funds as columns, datetime index, forward‑filled.
    message : str
        Empty when no adjustment was required, otherwise an info message.
    """
    # ----- 1️⃣  Concatenate full history -----------------
    combined_full = pd.concat(series_dict, axis=1).sort_index()
    # forward‑fill missing days so the chart looks smooth
    combined_full = combined_full.ffill()

    # ----- 2️⃣  Try the user‑requested window --------------
    combined = combined_full.loc[start_date:end_date]

    if not combined.empty:
        return combined, ""

    # ----- 3️⃣  Window empty → find earliest date that exists for *all* funds
    # (i.e. the latest of the first dates of each non‑empty series)
    earliest_common = max(
        s.dropna().index.min()
        for s in series_dict.values()
        if not s.dropna().empty
    )

    # If the earliest common date is after the chosen end date → nothing we can do
    if earliest_common > pd.Timestamp(end_date):
        return pd.DataFrame(columns=series_dict.keys()), (
            "No overlapping NAV data after adjusting the start date."
        )

    # Slice again using the adjusted start date
    combined = combined_full.loc[earliest_common:end_date]

    msg = (
        f"Adjusted start date to **{earliest_common.date()}** "
        "so that all selected funds have data."
    )
    return combined, msg


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar – fund selection & global options
# ──────────────────────────────────────────────────────────────────────────────
funds_df = get_all_funds()

st.sidebar.header("🔎 Select Funds")
selected_names = st.sidebar.multiselect(
    label="Pick up to 8 funds",
    options=funds_df["scheme_name"].tolist(),
    default=funds_df["scheme_name"].head(3).tolist(),
    help="Search by typing part of the fund name",
    max_selections=8,
)

if not selected_names:
    st.sidebar.info("Select at least one fund to continue.")
    st.stop()

# Mapping: fund name → scheme code (string)
name_to_code = {
    row["scheme_name"]: str(row["scheme_code"])
    for _, row in funds_df[funds_df["scheme_name"].isin(selected_names)].iterrows()
}

# Date‑range selector (defaults to the last year)
today = dt.date.today()
default_start = today - dt.timedelta(days=365)

start_date = st.sidebar.date_input(
    "Start date", value=default_start, min_value=dt.date(2000, 1, 1), max_value=today
)
end_date = st.sidebar.date_input(
    "End date", value=today, min_value=start_date, max_value=today
)

# Chart style options
st.sidebar.subheader("Chart options")
log_scale = st.sidebar.checkbox("Log‑scale Y‑axis", value=False)
show_sma = st.sidebar.checkbox("Overlay Simple Moving Average (SMA)", value=False)
sma_windows: List[int] = []
if show_sma:
    sma_windows = st.sidebar.multiselect(
        "Select SMA window(s) (days)",
        options=[5, 10, 20, 30, 60, 90],
        default=[20],
        help="SMA will be plotted on top of the normalised chart",
    )

# ──────────────────────────────────────────────────────────────────────────────
# Load full NAV series for the selected funds (once, cached)
# ──────────────────────────────────────────────────────────────────────────────
with st.spinner("Fetching NAV histories for the selected funds…"):
    full_series: Dict[str, pd.Series] = {}
    for fund_name in selected_names:
        code = name_to_code[fund_name]
        _scheme, nav_df = get_nav(code)

        # Keep a Series indexed by date; empty series if no data
        if nav_df.empty:
            full_series[fund_name] = pd.Series(dtype=float)
        else:
            full_series[fund_name] = nav_df.set_index("date")["nav"]

# If *every* selected fund is empty → nothing to show
if all(s.empty for s in full_series.values()):
    st.warning(
        "❗ None of the selected funds have any NAV data. "
        "Try a different fund or a wider date range."
    )
    st.stop()

# Build the combined DataFrame (auto‑adjust start‑date if needed)
combined, adjust_msg = build_combined(full_series, start_date, end_date)

if adjust_msg:
    st.info(adjust_msg)

if combined.empty:
    st.warning(
        "🚫  No NAV data available for the chosen funds/date range, "
        "even after the automatic adjustment."
    )
    st.stop()

# Normalise for the comparison chart (base = 100 on the first available date)
effective_start = combined.index[0]
norm = safe_normalise(combined, pd.Timestamp(effective_start))

# ──────────────────────────────────────────────────────────────────────────────
# Tabs – Dashboard | Analytics | Forecast
# ──────────────────────────────────────────────────────────────────────────────
tab_dashboard, tab_analytics, tab_forecast = st.tabs(
    ["📊 Dashboard", "📈 Analytics", "🔮 Forecast"]
)

# -------------------------------------------------------------------------
#   TAB 1 – Dashboard (chart, latest values, CSV download)
# -------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("Normalized NAV Comparison (base = 100)")

    # ----- Plotly line chart ------------------------------------------------
    fig = go.Figure()
    for col in norm.columns:
        fig.add_trace(
            go.Scatter(
                x=norm.index,
                y=norm[col],
                mode="lines",
                name=col,
            )
        )

    # Optional SMA overlays
    if show_sma and sma_windows:
        for w in sma_windows:
            sma = norm.rolling(window=w).mean()
            for col in norm.columns:
                fig.add_trace(
                    go.Scatter(
                        x=sma.index,
                        y=sma[col],
                        mode="lines",
                        line=dict(dash="dot"),
                        name=f"{col} SMA{w}",
                        hoverinfo="skip",
                    )
                )

    fig.update_layout(
        height=500,
        yaxis=dict(
            title="Index (Base = 100)",
            type="log" if log_scale else "linear",
        ),
        xaxis=dict(title="Date"),
        legend_title_text="Fund",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ----- Latest NAV & 1‑day % change ------------------------------------
    st.subheader("Latest NAV & 1‑day % change")
    latest_vals = combined.iloc[-1]
    # If we have only one observation the “previous” value is the same → 0 % change
    prev_vals = combined.iloc[-2] if len(combined) > 1 else latest_vals

    cols_per_row = 4
    rows = (len(selected_names) + cols_per_row - 1) // cols_per_row
    for r in range(rows):
        cols = st.columns(cols_per_row)
        for col, fund in zip(
            cols,
            selected_names[r * cols_per_row : (r + 1) * cols_per_row],
        ):
            nav_latest = latest_vals[fund]
            nav_prev = prev_vals[fund]
            delta = ((nav_latest - nav_prev) / nav_prev * 100) if nav_prev else 0.0
            col.metric(
                label=fund,
                value=f"₹{nav_latest:,.2f}",
                delta=f"{delta:+.2f}%",
            )

    # ----- Download raw NAV data (CSV) ------------------------------------
    csv_bytes = combined.reset_index().to_csv(index=False).encode()
    st.download_button(
        label="💾 Download raw NAV data (CSV)",
        data=csv_bytes,
        file_name="funds_nav.csv",
        mime="text/csv",
    )

# -------------------------------------------------------------------------
#   TAB 2 – Analytics (period returns, correlation heat‑map, quick meta)
# -------------------------------------------------------------------------
with tab_analytics:
    st.subheader("Analytics & Insights")

    # ----- Period‑wise returns ---------------------------------------------
    st.caption("Percentage returns measured from the most recent NAV")
    today_ts = combined.index[-1]
    periods = [
        ("1‑M", today_ts - pd.DateOffset(months=1)),
        ("3‑M", today_ts - pd.DateOffset(months=3)),
        ("6‑M", today_ts - pd.DateOffset(months=6)),
        ("YTD", pd.Timestamp(year=today_ts.year, month=1, day=1)),
        ("1‑Y", today_ts - pd.DateOffset(years=1)),
    ]
    returns_df = period_returns(combined, periods)
    st.dataframe(returns_df.style.format("{:.2f}%"))

    # ----- Correlation heat‑map --------------------------------------------
    if norm.shape[1] >= 2:          # need at least two series
        st.caption("Correlation matrix of the normalised NAV series")
        corr = norm.corr()
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Correlation Matrix (Normalized NAV)",
        )
        fig_corr.update_layout(height=550, margin=dict(t=40))
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Correlation matrix requires at least two funds.")

    # ----- Fund meta‑information (quick overview) -------------------------
    st.caption("Fund details (first three selected funds)")
    for fund in selected_names[:3]:
        with st.expander(fund):
            # The API we used (`get_nav`) already returns a readable name.
            # If you need additional meta fields you could fetch them here.
            st.write(f"**Fund name**: {fund}")

# -------------------------------------------------------------------------
#   TAB 3 – Forecast (Prophet)
# -------------------------------------------------------------------------
with tab_forecast:
    st.subheader("Prophet Forecast for a Selected Fund")

    fund_to_forecast = st.selectbox(
        "Choose fund to forecast", options=selected_names, index=0
    )
    days_ahead = st.slider(
        "Forecast horizon (days)", min_value=30, max_value=365, value=90, step=15
    )
    st.caption(
        "Seasonality options – leave unchecked for Prophet’s default behaviour"
    )
    col_yr, col_wk, col_dy = st.columns(3)
    with col_yr:
        yearly = st.checkbox("Yearly", value=False)
    with col_wk:
        weekly = st.checkbox("Weekly", value=False)
    with col_dy:
        daily = st.checkbox("Daily", value=False)

    if st.button("▶ Run forecast"):
        # Grab the *original* series for the chosen fund (no forward‑fill)
        series = full_series[fund_to_forecast]
        if series.empty:
            st.error("❗ Selected fund has no NAV data – cannot forecast.")
            st.stop()

        df_prophet = series.reset_index().rename(columns={"date": "ds", "nav": "y"})[
            ["ds", "y"]
        ]

        with st.spinner("Fitting Prophet model…"):
            m = Prophet(
                yearly_seasonality=yearly,
                weekly_seasonality=weekly,
                daily_seasonality=daily,
            )
            m.fit(df_prophet)

            future = m.make_future_dataframe(periods=days_ahead)
            forecast = m.predict(future)

        # ----- Plotly forecast chart ----------------------------------------
        fig_fc = go.Figure()
        # Observed
        fig_fc.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=df_prophet["y"],
                mode="lines",
                name="Observed",
            )
        )
        # Forecast (median)
        fig_fc.add_trace(
            go.Scatter(
                x=forecast["ds"],
                y=forecast["yhat"],
                mode="lines",
                name="Forecast",
            )
        )
        # 95 % confidence band
        fig_fc.add_trace(
            go.Scatter(
                x=forecast["ds"].tolist() + forecast["ds"][::-1].tolist(),
                y=forecast["yhat_upper"]
                .tolist()
                + forecast["yhat_lower"][::-1]
                .tolist(),
                fill="toself",
                fillcolor="rgba(0,100,80,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                hoverinfo="skip",
                name="95 % CI",
            )
        )
        fig_fc.update_layout(
            height=600,
            title=f"Prophet forecast for {fund_to_forecast}",
            xaxis_title="Date",
            yaxis_title="NAV",
            hovermode="x unified",
            margin=dict(l=40, r=40, t=50, b=40),
        )
        st.plotly_chart(fig_fc, use_container_width=True)

        # ----- Forecast table (last 10 rows) ---------------------------------
        st.subheader("Forecast table (last 10 rows)")
        display_fc = (
            forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
            .tail(10)
            .rename(
                columns={
                    "ds": "Date",
                    "yhat": "Forecast",
                    "yhat_lower": "Lower 95 % CI",
                    "yhat_upper": "Upper 95 % CI",
                }
            )
        )
        st.dataframe(display_fc)

        # ----- Download forecast CSV -----------------------------------------
        csv_fc = forecast.to_csv(index=False).encode()
        st.download_button(
            label="💾 Download forecast CSV",
            data=csv_fc,
            file_name=f"{fund_to_forecast.replace(' ', '_')}_forecast.csv",
            mime="text/csv",
        )

# ──────────────────────────────────────────────────────────────────────────────
# Footer – disclaimer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    ---
    **Disclaimer** – Data are sourced from the free MFAPI.in service and are
    provided “as‑is”. They are for informational purposes only and should not be
    construed as investment advice. Consult a qualified financial professional
    before making any investment decisions.
    """
)
