import datetime
import operator
from typing import List

from binancepump.binancePump import price_groups, show_limit, show_only_pair, price_changes, \
    min_perc
from binancepump.pricechange import PriceChange
from binancepump.pricegroup import PriceGroup


def process_message(get_price_changes, get_price_groups, printing_func, tickers):
    # TODO: KS: 2022-03-29: what is the input here - trades?
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


def printing_func(send_to_all_chat_ids, anyPrinted, sorted_price_group, msg):
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
