# 📈 FundSight – Mutual Fund NAV Dashboard

A professional-grade Streamlit application for tracking and analyzing Indian mutual fund NAV (Net Asset Value) data. Features interactive visualizations, performance analytics, and AI-powered forecasting capabilities.


## 🚀 Features

### 📊 Dashboard
- **Multi-fund Comparison**: Track up to 8 funds simultaneously with normalized NAV charts
- **Interactive Visualizations**: Plotly-powered charts with zoom, hover details, and legend controls
- **Real-time Metrics**: Latest NAV values with 1-day percentage changes
- **Moving Averages**: Optional SMA overlays for technical analysis
- **Data Export**: Download raw NAV data as CSV

### 📈 Analytics
- **Period Returns**: Calculate performance across multiple timeframes (1M, 3M, 6M, YTD, 1Y)
- **Correlation Analysis**: Heatmap showing relationships between selected funds
- **Fund Details**: Quick access to scheme information and metadata

### 🔮 Forecasting
- **Prophet AI Forecasting**: Advanced time series forecasting with configurable parameters
- **Confidence Intervals**: 95% prediction intervals for forecast reliability
- **Seasonality Controls**: Toggle yearly, weekly, and daily patterns
- **Export Capabilities**: Download forecast results as CSV

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fundsight.git
cd fundsight
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

### Manual Installation
If you don't have a requirements.txt, install the packages individually:
```bash
pip install streamlit pandas requests plotly prophet
```

## 📖 Usage Guide

### Selecting Funds
1. **Choose Funds**: Use the sidebar multiselect to pick up to 8 mutual funds
2. **Set Date Range**: Adjust the start and end dates for your analysis
3. **Chart Options**: Enable log-scale Y-axis or moving averages as needed

### Viewing Analytics
- Navigate to the **Analytics** tab to see performance metrics
- Check correlation heatmaps to understand fund relationships
- Review period returns for different investment horizons

### Running Forecasts
1. **Select a Fund**: Choose one fund from your selection
2. **Set Parameters**: Adjust forecast horizon and seasonality options
3. **Run Forecast**: Click the "Run Forecast" button to generate predictions
4. **Download Results**: Export forecast data for further analysis

## 🏗️ Architecture

### Data Flow
```
MFAPI.in (Free Indian MF Data) → Streamlit App → Interactive Dashboard
    ↓
Cached Data → Normalized Charts → Analytics → Forecasts
```

### Key Components
- **Data Layer**: `get_all_funds()`, `get_nav()` - Cached API calls
- **Processing Layer**: `safe_normalise()`, `period_returns()` - Data transformation
- **UI Layer**: Streamlit components with Plotly integration
- **ML Layer**: Facebook Prophet for time series forecasting

## 🔧 Configuration

### Environment Variables
No API keys required! The app uses the free MFAPI.in service.

### Customization Options
- Modify `sma_windows` in the sidebar for different moving average periods
- Adjust `ttl` values in cached functions for data freshness
- Customize date ranges and fund selection limits

## 📊 API Reference

The app uses the free [MFAPI.in](https://api.mfapi.in) service:

| Endpoint | Description |
|----------|-------------|
| `GET /mf` | List all mutual fund schemes |
| `GET /mf/{scheme_code}` | Get NAV history for a scheme |
| `GET /mf/search?q={query}` | Search funds by name |

## 🐛 Troubleshooting

### Common Issues

**"No NAV data available" Error**
- **Cause**: Selected date range doesn't contain data for chosen funds
- **Fix**: Adjust start date earlier or select different funds

**Prophet Forecast Fails**
- **Cause**: Insufficient historical data
- **Fix**: Choose funds with longer history or reduce forecast horizon

**API Connection Issues**
- **Cause**: Temporary MFAPI.in outage
- **Fix**: Wait and retry, or check MFAPI.in status

### Performance Tips
- Use the date range filter to limit data loading
- Select fewer funds for faster rendering
- Close other browser tabs to free up memory

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Important**: FundSight is for informational purposes only. The data is provided "as-is" from MFAPI.in and should not be considered financial advice. Always consult with qualified financial professionals before making investment decisions.

- Data accuracy depends on MFAPI.in service reliability
- Past performance does not guarantee future results
- Forecasts are probabilistic and contain uncertainty

## 🙏 Acknowledgments

- **MFAPI.in** for providing free mutual fund data
- **Streamlit** for the excellent framework
- **Plotly** for interactive visualizations
- **Facebook Prophet** for time series forecasting

---

**FundSight** – Making mutual fund analysis accessible and insightful since 2024 📈


