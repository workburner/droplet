import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# USER INPUT
# -------------------------

print("Enter up to 5 stock/ETF tickers")
print("Examples: SSO (2x S&P500), TQQQ (3x Nasdaq), UPRO, QLD, SPY, DIA")

tickers_input = input("Enter tickers separated by commas: ")
tickers = [t.strip().upper() for t in tickers_input.split(",")][:5]

total_investment = input("Total investment amount (default 10000): ")
total_investment = float(total_investment) if total_investment else 10000

print("\nChoose time unit:")
print("1 = Years, 2 = Months, 3 = Days")
choice = input("Enter choice: ")

length = int(input("Enter duration (e.g., 5 years / 12 months / 100 days): "))

# -------------------------
# DOWNLOAD DATA (FIXED)
# -------------------------

data = yf.download(tickers, period="max", auto_adjust=True, progress=True)

# Handle MultiIndex (multiple tickers)
if isinstance(data.columns, pd.MultiIndex):
    data = data["Close"]

# Drop only rows where ALL are NaN
data = data.dropna(how="all")

# -------------------------
# DATE HANDLING
# -------------------------

earliest_date = data.dropna().index[0]
latest_date = data.index[-1]

print(f"\nEarliest available date: {earliest_date.date()}")
print(f"Latest available date: {latest_date.date()}")

start_date_input = input(f"Enter start date (>= {earliest_date.date()}): ")
start_date = pd.to_datetime(start_date_input)

data = data[data.index >= start_date]

if choice == "1":
    end_date = start_date + pd.DateOffset(years=length)
    freq = "YE"   # FIXED
elif choice == "2":
    end_date = start_date + pd.DateOffset(months=length)
    freq = "ME"   # safer modern equivalent of "M"
else:
    end_date = start_date + pd.DateOffset(days=length)
    freq = "D"
# Determine end date
if freq == "YE":
    investment_dates = data.resample("YE").first().index
elif freq == "ME":
    investment_dates = data.resample("ME").first().index
else:
    investment_dates = data.index  # daily = every trading day

data = data[data.index <= end_date]

# -------------------------
# HELPER FUNCTIONS
# -------------------------

def calculate_drawdown(series):
    peak = series.cummax()
    return (series - peak) / peak

def plot_results(df, title):
    plt.figure(figsize=(12,6))
    for col in df.columns:
        plt.plot(df.index, df[col], label=col)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# -------------------------
# SCENARIO A: LUMP SUM
# -------------------------

lump_results = {}

for ticker in tickers:
    if ticker not in data.columns:
        continue

    prices = data[ticker].dropna()
    if len(prices) == 0:
        continue

    shares = total_investment / prices.iloc[0]
    portfolio = shares * prices
    lump_results[ticker] = portfolio

lump_df = pd.DataFrame(lump_results)
lump_drawdown = lump_df.apply(calculate_drawdown)

# -------------------------
# SCENARIO B: TRUE RECURRING INVESTMENT
# -------------------------

recurring_results = {}

# Create investment schedule
investment_dates = pd.date_range(start=data.index[0], end=data.index[-1], freq=freq)

for ticker in tickers:
    if ticker not in data.columns:
        continue

    prices = data[ticker].dropna()

    shares = 0
    portfolio_values = []
    dates = []

    valid_invest_dates = investment_dates[investment_dates.isin(prices.index)]
    num_investments = len(valid_invest_dates)

    if num_investments == 0:
        continue

    invest_amount_each = total_investment / num_investments

    for date in prices.index:
        if date in valid_invest_dates:
            shares += invest_amount_each / prices.loc[date]

        portfolio_values.append(shares * prices.loc[date])
        dates.append(date)

    recurring_results[ticker] = pd.Series(portfolio_values, index=dates)

recurring_df = pd.DataFrame(recurring_results)
recurring_drawdown = recurring_df.apply(calculate_drawdown)

# -------------------------
# PLOTTING
# -------------------------

plot_results(lump_df, "Scenario A: Lump Sum Performance")
plot_results(lump_drawdown, "Scenario A: Lump Sum Drawdown")

plot_results(recurring_df, "Scenario B: Recurring Investment Performance")
plot_results(recurring_drawdown, "Scenario B: Recurring Investment Drawdown")

# -------------------------
# SNAPSHOT FEATURE
# -------------------------

snapshot_date_input = input("\nEnter a date to inspect (or press Enter to skip): ")

if snapshot_date_input:
    snapshot_date = pd.to_datetime(snapshot_date_input)

    print("\n--- Snapshot Results ---")

    print("\nLump Sum:")
    print(lump_df.loc[:snapshot_date].tail(1).T)

    print("\nRecurring:")
    print(recurring_df.loc[:snapshot_date].tail(1).T)