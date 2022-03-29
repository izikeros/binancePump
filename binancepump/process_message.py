import operator
from typing import List

from binancepump.configuration import min_perc
from binancepump.configuration import show_limit
from binancepump.configuration import show_only_pair
from binancepump.extract_data_from_ticker import extract_data_from_ticker
from binancepump.price_change import PriceChange
from binancepump.price_change import initialize_symbol_entry_in_price_changes_list
from binancepump.price_group import PriceGroup


def get_price_changes(price_changes: List[PriceChange], tickers: List[dict]):
    """
    requires: "E", "s", "c", "o", "n", "v"
    All information except "n" is available in all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-mini-ticker-stream

    If "n" is needed then use  all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-ticker-streams

    :param tickers: list with data for each ticker kept in separate dictionary
    :return:
    """
    for ticker in tickers:
        symbol = ticker["s"]

        # skip this symbol if pair does not contain required pattern (e.g. USDT)
        if show_only_pair not in symbol:
            continue

        first_run = len(price_changes) == 0

        if first_run:
            update_empty_price_change_list(price_changes=price_changes, ticker=ticker)
        else:
            (
                symbol,
                event_time,
                open_price,
                price,
                total_trades,
                volume,
            ) = extract_data_from_ticker(ticker)
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


def update_empty_price_change_list(price_changes, ticker):
    (
        symbol,
        event_time,
        open_price,
        price,
        total_trades,
        volume,
    ) = extract_data_from_ticker(ticker)

    # check if in the price_changes list there is already an entry for this symbol
    # TODO: KS: 2022-03-29: price_changes should be rather dict than list?
    symbol_price_change = filter(lambda item: item.symbol == symbol, price_changes)
    symbol_price_change = list(symbol_price_change)
    is_entry_for_this_symbol = len(symbol_price_change) > 0

    if is_entry_for_this_symbol:
        update_existing_symbol_entry(
            event_time, open_price, price, symbol_price_change, total_trades, volume
        )
    else:
        # initialize price_changes
        initialize_symbol_entry_in_price_changes_list(
            price_changes_list=price_changes, ticker=ticker
        )


def update_existing_symbol_entry(
    event_time, open_price, price, symbol_price_change, total_trades, volume
):
    symbol_price_change = symbol_price_change[0]
    symbol_price_change.event_time = event_time
    symbol_price_change.prev_price = symbol_price_change.price
    symbol_price_change.prev_volume = symbol_price_change.volume
    symbol_price_change.price = price
    symbol_price_change.total_trades = total_trades
    symbol_price_change.open = open_price
    symbol_price_change.volume = volume
    symbol_price_change.isPrinted = False


def get_price_groups(price_changes: List[PriceChange], price_groups: List[PriceGroup]):
    for price_change in price_changes:
        # console_color = "green"
        if price_change.price_change_perc < 0:
            # console_color = "red"
            pass

        not_printed = not price_change.isPrinted
        high_price_change = abs(price_change.price_change_perc) > min_perc
        high_volume_change = abs(price_change.volume_change_perc) > min_perc

        if not_printed and high_price_change and high_volume_change:
            price_change.isPrinted = True

            new_pump_and_dump = price_change.symbol not in price_groups
            if new_pump_and_dump:
                price_groups[price_change.symbol] = PriceGroup(
                    symbol=price_change.symbol,
                    tick_count=1,
                    total_price_change=abs(price_change.price_change_perc),
                    relative_price_change=price_change.price_change_perc,
                    total_volume_change=price_change.volume_change_perc,
                    last_price=price_change.price,
                    last_event_time=price_change.event_time,
                    open_price=price_change.open,
                    volume=price_change.volume,
                    is_printed=False,
                )
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


def process_message(tickers, price_groups, price_changes):
    # TODO: KS: 2022-03-29: what is the input here - trades?

    get_price_changes(price_changes=price_changes, tickers=tickers)

    get_price_groups(price_changes=price_changes, price_groups=price_groups)

    if len(price_groups) > 0:
        anyPrinted = False

        sorted_price_group = sorted(
            price_groups, key=lambda k: price_groups[k]["tick_count"]
        )
        anyPrinted = printing_func(
            anyPrinted=anyPrinted,
            sorted_price_group=sorted_price_group,
            msg="Top Ticks",
            price_groups=price_groups,
        )

        sorted_price_group = sorted(
            price_groups, key=lambda k: price_groups[k]["total_price_change"]
        )
        anyPrinted = printing_func(
            anyPrinted,
            sorted_price_group,
            msg="Top Total Price Change",
            price_groups=price_groups,
        )

        sorted_price_group = sorted(
            price_groups,
            key=lambda k: abs(price_groups[k]["relative_price_change"]),
        )
        anyPrinted = printing_func(
            anyPrinted,
            sorted_price_group,
            msg="Top Relative Price Change",
            price_groups=price_groups,
        )

        sorted_price_group = sorted(
            price_groups, key=lambda k: price_groups[k]["total_volume_change"]
        )
        anyPrinted = printing_func(
            anyPrinted,
            sorted_price_group,
            msg="Top Total Volume Change",
            price_groups=price_groups,
        )


def printing_func(anyPrinted, sorted_price_group, msg, price_groups):
    if len(sorted_price_group) > 0:
        sorted_price_group = list(reversed(sorted_price_group))
        for s in range(show_limit):
            header_printed = False
            if s < len(sorted_price_group):
                max_price_group = sorted_price_group[s]
                max_price_group = price_groups[max_price_group]
                if not max_price_group.isPrinted:
                    if not header_printed:
                        send_to_all_chat_ids(msg)
                        header_printed = True
                    smsg = "".join([word[0] for word in msg.split()])
                    print(max_price_group.to_string(True, smsg))
                    send_to_all_chat_ids(max_price_group.to_string(False))
                    anyPrinted = True
    return anyPrinted


def send_to_all_chat_ids(msg):
    pass
