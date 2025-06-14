# -*- coding: utf-8 -*-
"""nasa final .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1a0y_ZZBdMYv6NWE1iVHv6DNwNZgnA0Jk
"""

import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# Tickers and date range
tickers = ['XOM', 'NEE', 'ENPH', 'AAPL', 'MSFT']
start_date = '2018-12-01'
end_date = '2024-12-31'

# Download historical data
raw_data = yf.download(tickers, start=start_date, end=end_date)
if isinstance(raw_data.columns, pd.MultiIndex) and ('Close' in raw_data.columns.levels[0]):
    price_data = raw_data['Close'].copy()
elif 'Close' in raw_data.columns:
    price_data = raw_data[['Close']].copy()
    price_data.columns = tickers[:1]
else:
    raise KeyError("'Close' not found in the downloaded data.")

price_data.dropna(inplace=True)

# Fetch CME data year-by-year to avoid timeout
nasa_api_key = "FAxgJsyCWIZ4TVdcDuGSkB641vHl6afhjrIzLWAJ"
cme_dates = []

try:
    for year in range(2018, 2025):
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        donki_url = f"https://api.nasa.gov/DONKI/CME?startDate={start}&endDate={end}&api_key={nasa_api_key}"
        response = requests.get(donki_url, timeout=15)
        if response.status_code == 200:
            year_data = response.json()
            dates = [entry['startTime'].split("T")[0] for entry in year_data if 'startTime' in entry]
            cme_dates.extend(dates)
        else:
            print(f"Failed to fetch data for {year}.")
    cme_flags = pd.Series(1, index=pd.to_datetime(cme_dates))
except Exception as e:
    print("Exception during NASA API batch call:", e)
    cme_flags = pd.Series(0, index=price_data.index)

# Merge solar events with price data
price_data['solar_event'] = 0
price_data.loc[price_data.index.isin(cme_flags.index), 'solar_event'] = 1

# Streamlit UI
st.title("🌞 NASA-RLTrader Dashboard")
st.markdown("Visualize the impact of NASA-detected solar events on stock performance.")

selected_tickers = st.multiselect("Select tickers:", tickers, default=['XOM', 'NEE'])
show_only_events = st.checkbox("Show only solar event days", value=False)

palette = sns.color_palette("tab10", len(selected_tickers))
data = price_data[selected_tickers]
if show_only_events:
    data = data[price_data['solar_event'] == 1]

fig, ax = plt.subplots(figsize=(12,6))
for idx, ticker in enumerate(selected_tickers):
    ax.plot(data.index, data[ticker], label=ticker, color=palette[idx])

if not show_only_events:
    event_dates = price_data[price_data['solar_event'] == 1].index
    avg_series = data.mean(axis=1)
    ax.scatter(event_dates, avg_series.loc[event_dates], color='black', marker='x', label='Solar Event')


ax.set_title("Stock Prices with NASA Solar Events")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.grid(True)
ax.legend()

st.pyplot(fig)

st.markdown("Built with ❤️ using yfinance, NASA API, and Streamlit.")









