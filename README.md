# 20ema_checker
A Telegram bot for tracking stock tickers using Yahoo Finance data. The bot provides features to add, delete, and query stock tickers and their respective 20-day Exponential Moving Average (EMA). It also automatically monitors price movements and notifies the user if the price crosses the 20EMA threshold.

# Stock Ticker Telegram Bot

This project is a **Telegram bot** built with Python, designed to help you track stock tickers and their 20-day Exponential Moving Average (EMA) using data from Yahoo Finance. The bot allows users to add, delete, and query stock tickers, as well as monitor price movements automatically.

## Features

- **Add Ticker**: Add stock tickers to track.
- **Delete Ticker**: Remove stock tickers from tracking.
- **Query Tickers**: Display current stock prices and 20-day EMA in a neatly formatted table.
- **Automatic Notifications**: Receive alerts if the stock price crosses the 20-day EMA threshold.
- **Persistence**: Stores tickers and price status in `pickle` files, which persist across bot restarts.
- **Scheduler**: Checks stock prices every 10 minutes and sends notifications if price crosses the 20EMA.

## How It Works

1. **Add Tickers**: Add a stock ticker (e.g., AAPL) using the `/add` command.
2. **Delete Tickers**: Remove a stock ticker using the `/delete` command.
3. **Query Tickers**: Use the `/query` command to get a table of the current price and 20EMA for all tracked tickers.
4. **Crossovers**: The bot monitors each ticker and notifies you when the price crosses the 20EMA (either above or below).

## Requirements

- Python 3.8+
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/en/stable/)
- [yfinance](https://pypi.org/project/yfinance/)
- [pandas](https://pandas.pydata.org/)

## Installation
1. Clone the Repository
```
git clone https://github.com/yourusername/stock-ticker-telegram-bot.git
cd stock-ticker-telegram-bot
```

2. Install Dependencies
```
pip install -r requirements.txt
```

3. Set Up Environment Variables
Create a .env file in the project root and add your Telegram Bot Token and User ID. You can create a Telegram bot using BotFather to get the token.
```
BOT_TOKEN=your_telegram_bot_token
ALLOWED_USER_ID=your_telegram_user_id
```

4. Run the Bot
```
python bot.py
```

## Running in Docker
Build the Docker Image
docker build -t stock-ticker-telegram-bot .

Run the Container with Volume for Pickle Persistence
```
docker run -d --name stock-ticker-bot \
    -e BOT_TOKEN=your_telegram_bot_token \
    -e ALLOWED_USER_ID=your_telegram_user_id \
    -v $(pwd)/data:/usr/src/app/data \
    stock-ticker-telegram-bot
```
This will mount the data folder in your current directory to the container, allowing you to preserve the tickers.pkl and status.pkl files.

## Usage
Bot Commands
/add <ticker>: Add a stock ticker to the list.
Example: /add AAPL
/delete <ticker>: Remove a stock ticker from the list.
Example: /delete AAPL
/query: Query the tracked tickers and get the current price and 20EMA.
Automatic Notifications: The bot automatically checks the price of the tracked tickers every 10 minutes and notifies you if the price crosses above or below the 20-day EMA.

Example Interaction
```
/add AAPL
Ticker 'AAPL' added to the list.

/query
| Ticker |  Current |  20EMA |
|--------|----------|--------|
| AAPL   | 150.30   |  145.90|
```

File Structure
```
├── bot.py                # Main bot script
├── requirements.txt      # Project dependencies
├── Dockerfile            # Docker build file
├── data/                 # Folder where pickle files will be stored
│   ├── tickers.pkl       # Stores the list of tickers
│   └── status.pkl        # Stores the status of the ticker prices vs 20EMA
└── README.md             # This file
```

Logging
The bot uses Python's logging module to record warnings and errors. Logs are output to the console.
