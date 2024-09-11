import os
import yfinance as yf
import pandas as pd
import pickle
import logging
from tabulate import tabulate
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import schedule
import asyncio

# Get ALLOWED_USER_ID and BOT_TOKEN from environment variables
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))  # Default to 0 if not provided
BOT_TOKEN = os.getenv("BOT_TOKEN", None)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN must be set as an environment variable.")

# Define the global variable for the file paths
TICKERS_FILE_PATH = '/data/tickers.pkl'
STATUS_FILE_PATH = '/data/status.pkl'  # To store previous state of price vs 20EMA

# Set up logging configuration
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Load or create the ticker list
def load_tickers():
    if os.path.exists(TICKERS_FILE_PATH):
        with open(TICKERS_FILE_PATH, 'rb') as f:
            return pickle.load(f)
    return []

def save_tickers(tickers_list):
    with open(TICKERS_FILE_PATH, 'wb') as f:
        pickle.dump(tickers_list, f)

# Load or create the status tracking dictionary
def load_status():
    if os.path.exists(STATUS_FILE_PATH):
        with open(STATUS_FILE_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

def save_status(status_dict):
    with open(STATUS_FILE_PATH, 'wb') as f:
        pickle.dump(status_dict, f)

# Check if the ticker is valid
def is_ticker_valid(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='5d')
        return not hist.empty
    except Exception as e:
        logging.error(f"Error fetching data for ticker '{ticker}': {e}")
        return False

# Add a ticker
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # Ignore requests from unauthorized users

    ticker = ' '.join(context.args).upper()

    if not is_ticker_valid(ticker):
        await update.message.reply_text(f"Invalid ticker: '{ticker}'. Cannot add it.")
        return

    tickers_list = load_tickers()

    if ticker not in tickers_list:
        tickers_list.append(ticker)
        save_tickers(tickers_list)
        await update.message.reply_text(f"Ticker '{ticker}' added to the list.")
    else:
        await update.message.reply_text(f"Ticker '{ticker}' is already in the list.")

# Delete a ticker
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # Ignore requests from unauthorized users

    ticker = ' '.join(context.args).upper()
    tickers_list = load_tickers()

    if ticker in tickers_list:
        tickers_list.remove(ticker)
        save_tickers(tickers_list)
        await update.message.reply_text(f"Ticker '{ticker}' removed from the list.")
    else:
        await update.message.reply_text(f"Ticker '{ticker}' not found in the list.")

# Query the 20EMA data
def get_20ema_and_price(ticker):
    stock_data = yf.download(ticker, period='1y', interval='1d')
    if stock_data.empty:
        return None, None

    stock_data['20EMA'] = stock_data['Close'].ewm(span=20, adjust=False).mean()
    latest_price = stock_data['Close'].iloc[-1]
    latest_20ema = stock_data['20EMA'].iloc[-1]

    return latest_price, latest_20ema

# Display the 20EMA table
async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return  # Ignore requests from unauthorized users

    tickers_list = load_tickers()
    if not tickers_list:
        await update.message.reply_text("No tickers found.")
        return

    data = []
    for ticker in tickers_list:
        price, ema_20 = get_20ema_and_price(ticker)
        if price is None or ema_20 is None:
            continue
        data.append({'Ticker': ticker, 'Current': f"{price:.2f}", '20EMA': f"{ema_20:.2f}"})

    if not data:
        await update.message.reply_text("No valid data found for the tickers.")
        return

    df = pd.DataFrame(data, columns=['Ticker', 'Current', '20EMA'])
    table_str = tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    await update.message.reply_text(f"```\n{table_str}\n```", parse_mode='Markdown')

# Check for 20EMA crossover and send a message if conditions are met
async def check_crossover_and_send(application):
    tickers_list = load_tickers()
    status_dict = load_status()

    data = []
    changed = False

    for ticker in tickers_list:
        price, ema_20 = get_20ema_and_price(ticker)
        if price is None or ema_20 is None:
            continue

        # Determine if the price crosses the 20EMA
        current_status = "above" if price > ema_20 else "below"
        previous_status = status_dict.get(ticker, None)

        # Only notify on status change
        if previous_status is not None and previous_status != current_status:
            ticker_name = f"!{ticker}"  # Add "!" to the ticker name for status change
            data.append({'Ticker': ticker_name, 'Current': f"{price:.2f}", '20EMA': f"{ema_20:.2f}"})
            status_dict[ticker] = current_status
            changed = True
        else:
            status_dict[ticker] = current_status

    # Only send message if there's a status change
    if changed:
        df = pd.DataFrame(data, columns=['Ticker', 'Current', '20EMA'])
        table_str = tabulate(df, headers='keys', tablefmt='grid', showindex=False)

        await application.bot.send_message(
            chat_id=ALLOWED_USER_ID,
            text=f"Status Change:\n```\n{table_str}\n```",
            parse_mode='Markdown'
        )

    # Save the status dictionary
    save_status(status_dict)

# Run the schedule job every 10 minutes
async def schedule_job(application):
    while True:
        schedule.run_pending()
        await asyncio.sleep(10)  # Sleep to avoid tight looping

# Set up the bot and handlers
async def main():
    # Create the application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Initialize the application
    await application.initialize()  # Required to initialize the application in v20+

    # Register handlers for /add, /delete, /query
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("query", query))

    # Schedule the job
    schedule.every(10).minutes.do(lambda: asyncio.create_task(check_crossover_and_send(application)))

    # Start the application and the scheduler
    await application.start()  # Start after initializing
    await application.updater.start_polling()

    # Run the schedule loop
    await schedule_job(application)


if __name__ == "__main__":
    asyncio.run(main())
