import argparse
import datetime as dt
import json
import operator
from typing import List

import telebot
from binance import BinanceSocketManager
from binance.client import Client
from pricechange import PriceChange
from pricegroup import PriceGroup


show_only_pair = "USDT"  # Select nothing for all, only selected currency will be shown
show_limit = 1  # minimum top query limit
min_perc = 0.05  # min percentage change
price_changes = []
price_groups = {}
last_symbol = "X"
chat_ids = []


def set_chat_id(c):
    chat_ids.append(c)


def add_price_change_to_list(price_changes_list, ticker: dict):
    """Initialize price_changes object with data from ticker dict."""
    symbol = ticker["s"]
    price = float(ticker["c"])
    total_trades = int(ticker["n"])
    open_price = float(ticker["o"])
    volume = float(ticker["v"])
    event_time = dt.datetime.fromtimestamp(int(ticker["E"]) / 1000)
    price_changes_list.append(
        PriceChange(
            symbol=symbol,
            prev_price=price,
            price=price,
            total_trades=total_trades,
            open=open_price,
            volume=volume,
            isPrinted=False,
            event_time=event_time,
            prev_volume=volume,
        )
    )
    return price_changes_list


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

    def process_message(tickers):
        # print("stream: {} data: {}".format(msg['stream'], msg['data']))
        # print("Len {}".format(len(msg)))
        # print("Current Price Of {} is {}".format(msg[0]['s'], msg[0]['c']))

        get_price_changes(tickers)

        get_price_groups()

        if len(price_groups) > 0:
            anyPrinted = False

            sorted_price_group = sorted(
                price_groups, key=lambda k: price_groups[k]["tick_count"]
            )
            anyPrinted = printing_func(anyPrinted, sorted_price_group, msg="Top Ticks")

            sorted_price_group = sorted(
                price_groups, key=lambda k: price_groups[k]["total_price_change"]
            )
            anyPrinted = printing_func(
                anyPrinted, sorted_price_group, msg="Top Total Price Change"
            )

            sorted_price_group = sorted(
                price_groups,
                key=lambda k: abs(price_groups[k]["relative_price_change"]),
            )
            anyPrinted = printing_func(
                anyPrinted, sorted_price_group, msg="Top Relative Price Change"
            )

            sorted_price_group = sorted(
                price_groups, key=lambda k: price_groups[k]["total_volume_change"]
            )
            anyPrinted = printing_func(
                anyPrinted, sorted_price_group, msg="Top Total Volume Change"
            )

            # if anyPrinted:
            #     print("")

    def printing_func(anyPrinted, sorted_price_group, msg):
        if len(sorted_price_group) > 0:
            sorted_price_group = list(reversed(sorted_price_group))
            for s in range(show_limit):
                header_printed = False
                if s < len(sorted_price_group):
                    max_price_group = sorted_price_group[s]
                    max_price_group = price_groups[max_price_group]
                    if not max_price_group.isPrinted:
                        if not header_printed:
                            # print(msg)
                            send_to_all_chat_ids(msg)
                            header_printed = True
                        smsg = "".join([word[0] for word in msg.split()])
                        print(max_price_group.to_string(True, smsg))
                        send_to_all_chat_ids(max_price_group.to_string(False))
                        anyPrinted = True
        return anyPrinted

    def get_price_groups():
        for price_change in price_changes:
            # console_color = "green"
            if price_change.price_change_perc < 0:
                # console_color = "red"
                pass

            if (
                not price_change.isPrinted
                and abs(price_change.price_change_perc) > min_perc
                and price_change.volume_change_perc > min_perc
            ):

                price_change.isPrinted = True

                if price_change.symbol not in price_groups:
                    price_groups[price_change.symbol] = PriceGroup(symbol=price_change.symbol,
                                                                   tick_count=1,
                                                                   total_price_change=abs(
                                                                       price_change.price_change_perc),
                                                                   relative_price_change=price_change.price_change_perc,
                                                                   total_volume_change=price_change.volume_change_perc,
                                                                   last_price=price_change.price,
                                                                   last_event_time=price_change.event_time,
                                                                   open_price=price_change.open,
                                                                   volume=price_change.volume,
                                                                   is_printed=False)
                else:
                    price_groups[price_change.symbol].tick_count += 1
                    price_groups[
                        price_change.symbol
                    ].last_event_time = price_change.event_time
                    price_groups[price_change.symbol].volume = price_change.volume
                    price_groups[price_change.symbol].last_price = price_change.price
                    price_groups[price_change.symbol].isPrinted = False
                    price_groups[price_change.symbol].total_price_change += abs(
                        price_change.price_change_perc
                    )
                    price_groups[
                        price_change.symbol
                    ].relative_price_change += price_change.price_change_perc
                    price_groups[
                        price_change.symbol
                    ].total_volume_change += price_change.volume_change_perc

    def get_price_changes(tickers: List[dict]):
        """

        :param tickers: list with data for each ticker kept in separate dictionary
        :return:
        """
        for ticker in tickers:
            symbol = ticker["s"]

            # skip this symbol if pair does not contain required pattern (e.g. USDT)
            if show_only_pair not in symbol:
                continue

            # Extract data from dict for the ticker
            price = float(ticker["c"])
            total_trades = int(ticker["n"])
            open_price = float(ticker["o"])
            volume = float(ticker["v"])
            event_time = dt.datetime.fromtimestamp(int(ticker["E"]) / 1000)
            if len(price_changes) > 0:
                price_change = filter(lambda item: item.symbol == symbol, price_changes)
                price_change = list(price_change)
                if len(price_change) > 0:
                    price_change = price_change[0]
                    price_change.event_time = event_time
                    price_change.prev_price = price_change.price
                    price_change.prev_volume = price_change.volume
                    price_change.price = price
                    price_change.total_trades = total_trades
                    price_change.open = open_price
                    price_change.volume = volume
                    price_change.isPrinted = False
                else:
                    # initialize price_changes
                    # price_changes = add_price_change_to_list(price_changes, ticker)
                    price_changes.append(
                        PriceChange(
                            symbol=symbol,
                            prev_price=price,
                            price=price,
                            total_trades=total_trades,
                            open=open_price,
                            volume=volume,
                            isPrinted=False,
                            event_time=event_time,
                            prev_volume=volume,
                        )
                    )

            else:
                price_changes.append(
                    PriceChange(
                        symbol=symbol,
                        prev_price=price,
                        price=price,
                        total_trades=total_trades,
                        open=open_price,
                        volume=volume,
                        isPrinted=False,
                        event_time=event_time,
                        prev_volume=volume,
                    )
                )
        price_changes.sort(key=operator.attrgetter("price_change_perc"), reverse=True)
        # print(len(price_changes))

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
