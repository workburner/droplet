import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 1. Download weekly data
qqq = yf.download("QQQ", period="8y", interval="1wk", auto_adjust=True)
tqqq = yf.download("TQQQ", period="8y", interval="1wk", auto_adjust=True)
# 2. Handle MultiIndex columns
def pick_col(df, col_name, ticker):
   if isinstance(df.columns, pd.MultiIndex):
       return (col_name, ticker)
   return col_name
qqq_open_col = pick_col(qqq, "Open", "QQQ")
qqq_close_col = pick_col(qqq, "Close", "QQQ")
qqq_high_col = pick_col(qqq, "High", "QQQ")
qqq_low_col = pick_col(qqq, "Low", "QQQ")
tqqq_close_col = pick_col(tqqq, "Close", "TQQQ")
# --- STRATEGY: Buy TQQQ on down weeks with >5% intraweek drop ---
qqq["WeeklyDropPct"] = (qqq[qqq_high_col] - qqq[qqq_low_col]) / qqq[qqq_high_col] * 100
qqq["IsDownWeek"] = qqq[qqq_close_col] < qqq[qqq_open_col]
qqq_drops = qqq[(qqq["IsDownWeek"]) & (qqq["WeeklyDropPct"] > 5)].copy()
qqq_drops.reset_index(inplace=True)
tqqq.reset_index(inplace=True)
strategy_trades = tqqq[tqqq["Date"].isin(qqq_drops["Date"])].copy()
strategy_trades["SharesBought"] = 100 / strategy_trades[tqqq_close_col]
strategy_trades["Investment"] = 100
strategy_trades["CumulativeShares"] = strategy_trades["SharesBought"].cumsum()
strategy_trades["CumulativeInvestment"] = strategy_trades["Investment"].cumsum()
strategy_trades["PortfolioValue"] = strategy_trades["CumulativeShares"] * strategy_trades[tqqq_close_col]
# --- BUY-AND-HOLD: $100 every week ---
tqqq_bh = tqqq.copy()
tqqq_bh["SharesBought"] = 100 / tqqq_bh[tqqq_close_col]
tqqq_bh["Investment"] = 100
tqqq_bh["CumulativeShares"] = tqqq_bh["SharesBought"].cumsum()
tqqq_bh["CumulativeInvestment"] = tqqq_bh["Investment"].cumsum()
tqqq_bh["PortfolioValue"] = tqqq_bh["CumulativeShares"] * tqqq_bh[tqqq_close_col]
# --- PLOT COMPARISON ---
plt.figure(figsize=(14,7))
plt.plot(strategy_trades["Date"], strategy_trades["PortfolioValue"], label="Strategy Portfolio Value", color="green")
plt.plot(strategy_trades["Date"], strategy_trades["CumulativeInvestment"], label="Strategy Invested", color="blue", linestyle="--")
plt.plot(tqqq_bh["Date"], tqqq_bh["PortfolioValue"], label="Buy & Hold Portfolio Value", color="red")
plt.plot(tqqq_bh["Date"], tqqq_bh["CumulativeInvestment"], label="Buy & Hold Invested", color="orange", linestyle="--")
plt.title("TQQQ Strategy vs Buy & Hold ($100 per purchase)")
plt.xlabel("Date")
plt.ylabel("USD")
plt.legend()
plt.grid(True)
plt.show()
# --- SUMMARY METRICS ---
def summarize(trades, name="Strategy"):
   total_shares = trades["CumulativeShares"].iloc[-1]
   total_invested = trades["CumulativeInvestment"].iloc[-1]
   last_price = trades[tqqq_close_col].iloc[-1]
   current_value = total_shares * last_price
   profit_loss = current_value - total_invested
   profit_loss_pct = (profit_loss / total_invested) * 100
   years = (trades["Date"].iloc[-1] - trades["Date"].iloc[0]).days / 365.25
   CAGR = (current_value / total_invested) ** (1/years) - 1
   rolling_max = trades["PortfolioValue"].cummax()
   max_drawdown = ((trades["PortfolioValue"] - rolling_max)/rolling_max).min()
   print(f"\n{name} Summary:")
   print(f"Qualifying weeks: {len(trades)}")
   print(f"Total shares bought: {total_shares:.4f}")
   print(f"Total invested capital: ${total_invested:,.2f}")
   print(f"Current value: ${current_value:.2f}")
   print(f"Total gain: ${profit_loss:.2f}")
   print(f"Percent gain: {profit_loss_pct:.2f}%")
   print(f"CAGR: {CAGR*100:.2f}%")
   print(f"Max Drawdown: {max_drawdown*100:.2f}%")
summarize(strategy_trades, "Down-Week Strategy")
summarize(tqqq_bh, "Buy & Hold TQQQ")