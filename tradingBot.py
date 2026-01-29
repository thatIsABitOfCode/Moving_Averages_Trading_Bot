# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 14:52:49 2026

@author: Yola
"""

import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# List of popular stock symbols
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "FB", "NFLX", "NVDA", "BRK-B", "JPM"]

# Availablw resampling frequencies
resampling_options={
    "Yearly": "Y",
    "Monthly": "M",
    "Weekly": "W",
    "Daily": "D",
    "Hourly": "H",
    "Every 10 Seconds": "10S"
    }

# Title
st.title("Simple Moving Average Strategy")

# User Input: Symbol, Start Date and End Date
symbol = st.selectbox("Select Stock Symbol", symbols)
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2025-01-01"))

# User selects resampling frequency
resample_freq = st.selectbox("Select Resampling Frequency", list(resampling_options.keys()))
resample_code = resampling_options[resample_freq]

# Extract Currency values from yf
data = yf.download(symbol , start= start_date , end= end_date)
df = data

# Resample the data based on user's choice and calculate mean values
df = df.resample(resample_code).mean()

# Fix MultiIndex columns if present
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Indicators: Calculate Moving Averages
if resample_code in ["D","W","M", "Y"]:
    df["MA20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
elif resample_code == "H": #If resa,pling hourly
    df["MA20"] = df["Close"].rolling(window=20, min_periods=1).mean()  # 20 hours
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
else:  #If more detailed, adjust window sizes or leave them out
    df["MA20"] = df["Close"].rolling(window=1, min_periods=1).mean()  # For "10S" (just dummy values)
    df["MA50"] = df["Close"].rolling(window=1, min_periods=1).mean()

# Generate trading Signals
df["Signal"]=0
df.loc[df["MA20"] > df["MA50"], "Signal"] =1
df.loc[df["MA20"] < df["MA50"], "Signal"] =-1

## Remove rows with NaN MA Values
df = df.dropna(subset=["MA20", "MA50"])

# Create Buy and Sell columns
df["Buy"]=0
df["Sell"]=0

# Buy and Sell Conditions
##Buy: MA20 crosses ABOVE MA50
df.loc[
       (df["MA20"].shift(1)<df["MA50"].shift(1))&
       (df["MA20"]>df["MA50"]),
       "Buy"
       ] = 1

##Sell: MA20 crosses BELOW MA50
df.loc[
       (df["MA20"].shift(1)>df["MA50"].shift(1))&
       (df["MA20"]<df["MA50"]),
       "Sell"
       ] = 1



# Plot using Streamlit
st.subheader("Price with Moving Averages")

fig, ax =plt.subplots(figsize=(12,6)) # Adjust the size of the figure



## Buy Signals (green upward triangles)
ax.scatter(
    df.index[df["Buy"]==1],
    df["Close"][df["Buy"]==1],
    marker="^",
    s=100,
    label="Buy Signal",
    color='black'
    )

## Sell Signals (red downward triangles)
ax.scatter(
    df.index[df["Sell"]==1],
    df["Close"][df["Sell"]==1],
    marker="v",
    s=100,
    label="Sell Signal",
    color='red'
    )

# Set date format on x-axis
ax.xaxis.set_major_locator(mdates.MonthLocator()) #Set major ticks to months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format for labels
# Rotate and align the x-tick labels
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
# Improve layout by rotating the x-ticks
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

## Price & MAs
ax.plot(df.index,df["Close"], label = "Close Price")
ax.plot(df.index, df["MA20"], label="MA20")
ax.plot(df.index, df["MA50"], label="MA50")

# Labels and legend
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.set_title(f"{symbol} Price with Trading Signals")
ax.legend()
ax.grid(True)
st.pyplot(fig)

###
st.write(df[["Close", "MA20", "MA50"]].tail(10))
st.write("Total Buy signals:", df["Buy"].sum())
st.write("Total Sell signals:", df["Sell"].sum())
###

###Display recent signals
st.write(df[["MA20", "MA50", "Buy", "Sell"]].tail(10))
###

# Show raw data
st.subheader("Raw Data")
st.dataframe(df)