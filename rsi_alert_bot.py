import asyncio
from telegram import Bot
from tradingview_ta import TA_Handler, Interval
import datetime

# ==== Your Telegram Bot Details ====
TOKEN = '7742039389:AAEejXtpmLu1hkI-G0Q1zjDokagDiVBoamo'
CHAT_ID = '5108088721'

# ==== Settings ====
STOCKS = ['RELIANCE', 'WIPRO', 'TCS', 'GANESHHOUC']  # NSE stocks without .NS
OVERSOLD = 30  # RSI below 30 = alert
CHECK_INTERVAL = 60  # check every 60 seconds
NO_ALERT_SENT_TODAY = False  # to control "No alert" message

# ==== Initialize Bot ====
bot = Bot(token=TOKEN)

# ==== Function to send Telegram Message ====
async def send_telegram(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# ==== Function to check RSI ====
async def monitor_rsi():
    global NO_ALERT_SENT_TODAY
    alerted_stocks = set()

    while True:
        now = datetime.datetime.now()
        if now.hour == 0 and now.minute == 0:  # Reset at midnight
            NO_ALERT_SENT_TODAY = False
            alerted_stocks.clear()

        alerts = []

        for stock in STOCKS:
            try:
                handler = TA_Handler(
                    symbol=stock,
                    screener="india",
                    exchange="NSE",
                    interval=Interval.INTERVAL_1_DAY
                )
                analysis = handler.get_analysis()
                rsi = analysis.indicators['RSI']

                if rsi < OVERSOLD and stock not in alerted_stocks:
                    alerts.append(f"🔻 {stock} RSI is {rsi:.2f} — OVERSOLD")
                    alerted_stocks.add(stock)

                elif rsi >= OVERSOLD and stock in alerted_stocks:
                    alerted_stocks.remove(stock)

            except Exception as e:
                print(f"Error checking {stock}: {e}")

        if alerts:
            message = "\n".join(alerts)
            await send_telegram(message)
            NO_ALERT_SENT_TODAY = True

        elif not NO_ALERT_SENT_TODAY:
            await send_telegram("✅ No RSI alerts today.")
            NO_ALERT_SENT_TODAY = True

        await asyncio.sleep(CHECK_INTERVAL)

# ==== Start Monitoring ====
asyncio.run(monitor_rsi())
