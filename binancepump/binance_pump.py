import argparse
import json

import telebot
from binance import BinanceSocketManager
from binance.client import Client

show_only_pair = "USDT"  # Select nothing for all, only selected currency will be shown
show_limit = 1  # minimum top query limit
min_perc = 0.05  # min percentage change
price_changes = []
price_groups = {}
last_symbol = "X"
chat_ids = []


def set_chat_id(c):
    chat_ids.append(c)


def main(use_telegram_bot=False):
    # READ API CONFIG
    api_config = {}
    with open("api_config.json") as json_data:
        api_config = json.load(json_data)
        json_data.close()

    TOKEN = api_config["telegram_bot_token"]
    tb = telebot.TeleBot(TOKEN)  # create a new Telegram Bot object
    # if use_telegram_bot:
    #     TOKEN = api_config["telegram_bot_token"]
    #     tb = telebot.TeleBot(TOKEN)  # create a new Telegram Bot object
    # else:
    #     tb = None

    def send_message(chat_id, msg):
        try:
            tb.send_message(chat_id, msg)
        except:
            pass

    def send_to_all_chat_ids(msg):
        for chat_id in chat_ids:
            send_message(chat_id, msg)

    @tb.message_handler(commands=["start", "help"])
    def send_welcome(message):
        set_chat_id(message.chat.id)
        tb.reply_to(
            message,
            "Welcome to BinancePump Bot, Binance Top Tick Count, Top Price and Volume Change "
            "Feeds will be shared with you. One of it could be start of pump or dump, keep an eye "
            "on me!",
        )

    # ---- main starts here -----
    client = Client(api_config["api_key"], api_config["api_secret"])
    # client = AsyncClient(api_config["api_key"], api_config["api_secret"])
    # prices = client.get_all_tickers()
    # pairs = list(pd.DataFrame(prices)["symbol"].values)
    # pairs = [pair for pair in pairs if "BTC" in pair]
    # print(pairs)

    bm = BinanceSocketManager(client)
    conn_key = bm.ticker_socket()
    # bm.start()
    print("bm socket started")

    tb.polling()
    print("tb socket started")

    input("Press Enter to close connection...")
    bm._stop_socket(conn_key)  # or _exit_socket(conn_key)
    # bm.close()
    print("Socket Closed")
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binance pump or dump detector")
    parser.add_argument(
        "--use-telegram-bot",
        action="store_true",
        default=True,
        help="enable telegram bot",
    )
    args = parser.parse_args()
    main(args.use_telegram_bot)
