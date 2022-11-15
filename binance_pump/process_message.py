from binance_pump import logger
import operator
from typing import Dict
from typing import List

from binance_pump.configuration import conf

from binance_pump.price_change import PriceChange
from binance_pump.pump_and_dump_event_tracker import PumpOrDumpEventTracker
from binance_pump.display import display_interesting_coins
from binance_pump.pnd_criteria import criteria
from binance_pump.price_change import existing_price_change, new_price_change
from traces import new_pnd, existing_pnd

DISPLAY_FOOTER = True

# define named tuple with fields: sorting criterion, label for the criterion, threshold
# NOTE: threshold is not used in this version
# TODO: KS: 2022-04-10: unify usage criterions for qualifying event as PnD and display Criterions


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

    for ticker in tickers:
        symbol = ticker["s"]

        # skip this symbol if pair does not contain required pattern (e.g. USDT)
        if conf.SHOW_ONLY_PAIR not in symbol:
            continue
        logger.debug("  Calculating price change for for symbol: %s", symbol)

        pc = price_changes.get(symbol, None)
        if pc is None:
            new_price_change(price_changes=price_changes, ticker=ticker)
        else:
            existing_price_change(price_changes=price_changes, ticker=ticker)

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
    price_changes: Dict[str, PriceChange], pnd_events: Dict[str, PumpOrDumpEventTracker]
):
    for coin in price_changes.values():

        # expecting significant rise or drop in price
        high_price_change = abs(coin.price_change_perc) > conf.PRICE_CHANGE_PERC_TH

        # expecting rising volume
        high_volume_change = coin.volume_change_perc > conf.VOLUME_CHANGE_PERC_TH

        # Condition for PnD: percentage price change is high and percentage volume change is high
        is_pnd = high_price_change and high_volume_change
        new_pump_and_dump = coin.symbol not in pnd_events
        if is_pnd and new_pump_and_dump:
            logger.debug("  PnD event for symbol: %s detected", coin.symbol)
            new_pnd(coin, pnd_events)
        elif not (coin.is_added or new_pump_and_dump):
            existing_pnd(coin, pnd_events, is_pnd)


def tick_reduce(
    tick_value,
    method="linear",
    tick_subtract_value=conf.TICK_SUBTRACT_VALUE,
    tick_reduce_multiplier=conf.TICK_REDUCE_MULTIPLIER,
):
    """Reduce event importance if was not active in given iteration."""
    tick_new_value = tick_value
    if method == "linear":
        tick_new_value = tick_value - tick_subtract_value
    elif method == "exponential":
        tick_new_value = tick_value * tick_reduce_multiplier
    return tick_new_value


def outdate_events(
    pnd_events: Dict[str, PumpOrDumpEventTracker],
    retired_pnd_events: List[PumpOrDumpEventTracker],
):
    """Update actuality for all (active) pnd events.

    Args:
        pnd_events: List of PnD events.

    """
    keys_to_remove = []
    for k, v in pnd_events.items():
        if pnd_events[k].actuality > 0:
            pnd_events[k].actuality = tick_reduce(
                pnd_events[k].actuality, method=conf.OUTDATING_METHOD
            )

        # delete element
        if pnd_events[k].actuality == 0:
            keys_to_remove.append(k)

    for k in keys_to_remove:
        skip_n = conf.SKIP_SAVING_EVENTS_SHORTER_THAN_N_TICKS
        save_trace = True
        if skip_n is not None:
            if pnd_events[k].tick_count < skip_n:
                save_trace = False

        if save_trace:
            retired_pnd_events.append(pnd_events[k])

        del pnd_events[k]
    return pnd_events


def process_message(
    tickers,
    pnd_events: Dict[str, PumpOrDumpEventTracker],
    price_changes: dict[str, PriceChange],
    retired_pnd_events: List[PumpOrDumpEventTracker],
    message_id: int
):
    # calculate price changes for each symbol of interest
    price_changes = update_price_changes(price_changes=price_changes, tickers=tickers)

    # update pnd events
    update_pnd_events(price_changes=price_changes, pnd_events=pnd_events)

    # criteria tuple format: (sorting criterion, Label for the criterion)
    are_any_pnd_events = len(pnd_events)
    if are_any_pnd_events:
        for i, criterion in enumerate(criteria):
            sorted_pnd_events = sorted(
                pnd_events, key=lambda k: pnd_events[k][criterion.type]
            )

            display_interesting_coins(sorted_pnd_symbols=sorted_pnd_events, pnd_events=pnd_events)
    if DISPLAY_FOOTER:
        print(
            f"#{message_id} | PnD Events | tracked: {len(pnd_events)}, Retired: {len(retired_pnd_events)}"
        )

    outdate_events(pnd_events=pnd_events, retired_pnd_events=retired_pnd_events)
