# FundSight: Mutual Fund NAV Trends & Forecast 📈

FundSight is a lightweight and interactive Streamlit app designed to help you visualize and forecast the Net Asset Value (NAV) trends of Indian mutual funds. The app fetches real-time data and provides clear, actionable insights into fund performance.

-----

## ✨ Features

  * **Historical NAV Data**: Access and fetch historical NAV data for a wide range of Indian mutual funds.
  * **Normalized Performance View**: Compare fund performance directly by normalizing NAVs to a base of 100.
  * **Real-Time Insights**: View the latest NAV and its 1-day percentage change.
  * **Future Forecasting**: Get a glimpse into the future with NAV forecasts for selected funds using the **Facebook Prophet** library.
  * **Clean & Interactive Interface**: Navigate a user-friendly and responsive Streamlit interface.

-----

## 🚀 Getting Started (Local Setup)

Follow these simple steps to get FundSight up and running on your local machine.

### 1\. Clone the Repository

```bash
git clone https://github.com/Ridakhan15/FundSight.git
cd FundSight
```

### 2\. Set Up a Virtual Environment

It's a best practice to use a virtual environment to manage dependencies.

**Windows**:

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux**:

```bash
python -m venv venv
source venv/bin/activate
```

### 3\. Install Dependencies

Install all the necessary packages using the provided `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4\. Run the App

Launch the application using Streamlit.

```bash
streamlit run app.py
```

Once the server starts, open the link shown in your terminal (usually `http://localhost:8501`) in your web browser.

-----

## 🛠 Notes

  * **No API keys are required** to get started; the data is fetched directly from **mfapi.in**.
  * **Prophet Installation on Windows**: If you encounter issues installing the `prophet` package, consider using Anaconda. You can install it with the following command:
    ```bash
    conda install -c conda-forge prophet
    ```
  * **Security**: Remember not to commit sensitive files, such as `.env` or API keys, to your repository.

