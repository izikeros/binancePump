import operator
from typing import List, Dict

from binancepump import logger
from binancepump.configuration import PRICE_MIN_PERC, VOLUME_MIN_PERC
from binancepump.configuration import SHOW_LIMIT
from binancepump.configuration import SHOW_ONLY_PAIR
from binancepump.extract_data_from_ticker import extract_data_from_ticker
from binancepump.price_change import PriceChange
from binancepump.pump_and_dump_event_tracker import PumpOrDumpEventTracker


def update_price_changes(
    price_changes: Dict[str, PriceChange], tickers: List[dict]
) -> Dict[str, PriceChange]:
    """
    requires: "E", "s", "c", "o", "n", "v"
    All information except "n" is available in all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-mini-ticker-stream

    If "n" is needed then use  all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-ticker-streams

    :param price_changes:
    :param tickers: list with data for each ticker kept in separate dictionary
    :return:
    """
    # global price_changes_list
    for ticker in tickers:
        symbol = ticker["s"]

        # skip this symbol if pair does not contain required pattern (e.g. USDT)
        if SHOW_ONLY_PAIR not in symbol:
            continue
        logger.debug("  Calculating price change for for symbol: %s", symbol)

        (
            symbol,
            event_time,
            open_price,
            price,
            total_trades,
            volume,
        ) = extract_data_from_ticker(ticker)

        pc = price_changes.get(symbol, None)
        if pc is None:
            price_changes[symbol] = PriceChange(
                symbol=symbol,
                prev_price=price,
                price=price,
                total_trades=total_trades,
                open_price=open_price,
                volume=volume,
                is_printed=False,
                event_time=event_time,
                prev_volume=volume,
            )
        else:
            prev_price = price_changes[symbol].price
            prev_volume = price_changes[symbol].volume
            price_changes[symbol].event_time = event_time
            price_changes[symbol].prev_price = prev_price
            price_changes[symbol].prev_volume = prev_volume
            price_changes[symbol].price = price
            price_changes[symbol].total_trades = total_trades
            price_changes[symbol].open_price = open_price
            price_changes[symbol].volume = volume
            price_changes[symbol].is_printed = False
            logger.debug("    Updated existing entry for symbol: %s", symbol)

    # sort dictionary of objects by property price_change_perc

    price_changes_list = sorted(
        price_changes.values(),
        key=operator.attrgetter("price_change_perc"),
        reverse=True,
    )

    # use list of objects and create dictionary of objects with symbol as key
    price_changes = {pc.symbol: pc for pc in price_changes_list}
    return price_changes


def update_pnd_events(
    price_changes: Dict[str, PriceChange], pnd_events: List[PumpOrDumpEventTracker]
):
    for coin in price_changes.values():
        # console_color = "green"
        if coin.price_change_perc < 0:
            # console_color = "red"
            pass

        not_printed = not coin.is_printed
        high_price_change = abs(coin.price_change_perc) > PRICE_MIN_PERC
        high_volume_change = abs(coin.volume_change_perc) > VOLUME_MIN_PERC

        if not_printed and high_price_change and high_volume_change:
            coin.is_printed = True

            new_pump_and_dump = coin.symbol not in pnd_events
            if new_pump_and_dump:
                pnd_events[coin.symbol] = PumpOrDumpEventTracker(
                    symbol=coin.symbol,
                    tick_count=1,
                    absolute_price_change=abs(coin.price_change_perc),
                    relative_price_change=coin.price_change_perc,
                    total_volume_change=coin.volume_change_perc,
                    last_price=coin.price,
                    last_event_time=coin.event_time,
                    open_price=coin.price,
                    volume=coin.volume,
                    is_printed=False,
                )
            else:
                s = coin.symbol
                pnd_events[s].tick_count += 1
                pnd_events[s].last_event_time = coin.event_time
                pnd_events[s].volume = coin.volume
                pnd_events[s].last_price = coin.price
                pnd_events[s].is_printed = False
                pnd_events[s].absolute_price_change += abs(coin.price_change_perc)
                pnd_events[s].relative_price_change += coin.price_change_perc
                pnd_events[s].total_volume_change += coin.volume_change_perc


def display_interesting_pairs(
    sorted_pnd_events: List[PumpOrDumpEventTracker],
    reason_msg: str,
    pnd_events: Dict[str, PumpOrDumpEventTracker],
):
    """Function that prints top PnD events from the list and send to messenger.

    Args:
        sorted_pnd_events: List of PriceGroups sorted by given criterion
                                    (e.g. the biggest relative price change).
        reason_msg: Message to be printed (reason for being interesting e.g. top relative volume change
        pnd_events: Dictionary of price groups.

    """
    if len(sorted_pnd_events) > 0:
        sorted_pnd_events = list(reversed(sorted_pnd_events))
        for symbol_idx in range(SHOW_LIMIT):
            if symbol_idx < len(sorted_pnd_events):
                # check if the symbol has been printed (e.g. due to being in the top N in other
                # ranking
                max_pnd_from_sorted = sorted_pnd_events[symbol_idx]
                max_pnd = pnd_events[max_pnd_from_sorted]

                if not max_pnd.is_printed:
                    short_reason_message = create_short_message(reason_msg)
                    # print the interesting symbol info to the console
                    print(max_pnd.to_string(True, short_reason_message))


def create_short_message(msg):
    """Create a short message from a long message. Take first letters from each word.

    Args:
        msg: Long message.

    Returns:
        Short message.
    """
    short_msg = "".join([word[0] for word in msg.split()])
    return short_msg


def process_message(tickers, price_groups, price_changes):
    # TODO: KS: 2022-03-29: what is the input here - trades?

    # calculate price changes for each symbol of interest
    price_changes = update_price_changes(price_changes=price_changes, tickers=tickers)

    update_pnd_events(price_changes=price_changes, pnd_events=price_groups)

    # criteria tuple format: (sorting criterion, Label for the criterion)
    criteria = [
        # ("tick_count", "Ticks"),
        ("absolute_price_change", "Price Change"),
        # ("relative_price_change", "Relative Price Change"),
        ("total_volume_change", "Volume Change"),
    ]

    are_any_pnd_events = len(price_groups)
    if are_any_pnd_events:
        for i, criterion in enumerate(criteria):
            # print(f"Reason: {criterion[1]}")
            sorted_pnd_events = sorted(
                price_groups, key=lambda k: price_groups[k][criterion[0]]
            )

            display_interesting_pairs(
                sorted_pnd_events=sorted_pnd_events,
                reason_msg=criterion[1],
                pnd_events=price_groups,
            )
    # TODO: KS: 2022-04-04: modify ticks count for each event (to eliminate events that are not
    #  active for a long time)
