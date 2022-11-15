import operator

from _typing import PnDEventsT
from _typing import PriceChangesT
from _typing import RetiredPnDEventsT
from binance_pump.configuration import conf
from binance_pump.display import display_interesting_coins
from binance_pump.logger import logger
from binance_pump.pnd_criteria import criteria
from binance_pump.price_change import existing_price_change
from binance_pump.price_change import new_price_change
from binance_pump.pump_and_dump_event_tracker import PumpOrDumpEventTracker
from traces import existing_pnd
from traces import new_pnd

DISPLAY_FOOTER = True

# define named tuple with fields: sorting criterion, label for the criterion, threshold
# NOTE: threshold is not used in this version
# TODO: KS: 2022-04-10: unify usage criterions for qualifying event as PnD and display Criterions


def update_price_changes(
    price_changes: PriceChangesT, tickers: list[dict]
) -> PriceChangesT:
    """
    requires: "E", "s", "c", "o", "n", "v"
    All information except "n" is available in all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-mini-ticker-stream

      {
        "e": "24hrMiniTicker",  // Event type
        "E": 123456789,         // Event time
        "s": "BNBBTC",          // Symbol
        "c": "0.0025",          // Close price
        "o": "0.0010",          // Open price
        "h": "0.0025",          // High price
        "l": "0.0010",          // Low price
        "v": "10000",           // Total traded base asset volume
        "q": "18"               // Total traded quote asset volume
      }

    If "n" is needed then use  all market tickers stream:
    https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-ticker-streams

    :param price_changes:
    :param tickers: list with data for each ticker kept in separate dictionary
    :return:
    """
    # select tickers of interest - skip, if pair does not contain required pattern (e.g. USDT)
    n_before = len(tickers)
    sel_tickers = [t for t in tickers if conf.SHOW_ONLY_PAIR in t["s"]]
    n_after = len(sel_tickers)

    logger.debug(f"{n_before} tickers received, {n_after} kept for analysis")
    for ticker_dict in sel_tickers:
        symbol = ticker_dict["s"]

        # get price changes object for given symbol
        pc = price_changes.get(symbol)
        if pc is None:
            new_price_change(price_changes=price_changes, ticker=ticker_dict)
        else:
            existing_price_change(price_changes=price_changes, ticker=ticker_dict)

    # sort list of objects (price_changes.values() by object property: price_change_perc
    price_changes_list = sorted(
        price_changes.values(),
        key=operator.attrgetter("price_change_perc"),
        reverse=True,
    )

    # use list of objects and create dictionary of objects with symbol as key
    # dictionary is now sorted by price_change_perc
    price_changes = {pc.symbol: pc for pc in price_changes_list}
    return price_changes


def update_pnd_events(price_changes: PriceChangesT, pnd_events: PnDEventsT):
    for price_change in price_changes.values():

        # expecting significant rise or drop in price
        high_price_change = (
            abs(price_change.price_change_perc) > conf.PRICE_CHANGE_PERC_TH
        )

        # expecting rising volume
        high_volume_change = (
            price_change.volume_change_perc > conf.VOLUME_CHANGE_PERC_TH
        )

        # is P&D if high increase in volume and price
        #   Condition for PnD: percentage price change is high and percentage volume change is high
        is_pnd = high_price_change and high_volume_change

        # check if this event is already in the list of PnD events or is new
        new_pump_and_dump = price_change.symbol not in pnd_events

        if is_pnd and new_pump_and_dump:
            logger.debug(f"  PnD event for symbol: {price_change.symbol} detected")
            new_pnd(price_change, pnd_events)
        elif not (price_change.is_added or new_pump_and_dump):
            existing_pnd(price_change, pnd_events, is_pnd)


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
    pnd_events: dict[str, PumpOrDumpEventTracker],
    retired_pnd_events: list[PumpOrDumpEventTracker],
):
    """Update actuality for all (active) pnd events.

    Args:
        pnd_events: List of PnD events.

    """
    keys_to_remove = []
    for k, _ in pnd_events.items():
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
    pnd_events: PnDEventsT,
    price_changes: PriceChangesT,
    retired_pnd_events: RetiredPnDEventsT,
    message_id: int,
):
    """Process message from Binance websocket.

    There are three lists of objects passed into this function. They are updated in place.

    - update price changes
    - update PnD events

    Args:
        tickers: List of tickers.
        pnd_events: List of PnD events.
        price_changes: List of price changes.
        retired_pnd_events: List of retired PnD events.
        message_id: Message ID.

    Returns:
        None
    """
    n_tickers = len(tickers)
    logger.debug(f"Processing message {message_id} with {n_tickers} tickers")

    # calculate price changes for each symbol of interest
    price_changes = update_price_changes(price_changes=price_changes, tickers=tickers)

    # update pnd events
    #  - add new pnd events
    #  - update existing pnd events
    #  - retire old pnd events (when "pump and dump" is over)
    update_pnd_events(price_changes=price_changes, pnd_events=pnd_events)

    # criteria tuple format: (sorting criterion, Label for the criterion)
    are_any_pnd_events = len(pnd_events)
    if are_any_pnd_events:
        for criterion in criteria:
            sorted_pnd_events = sorted(
                pnd_events, key=lambda k: pnd_events[k][criterion.type]
            )

            display_interesting_coins(
                sorted_pnd_symbols=sorted_pnd_events, pnd_events=pnd_events
            )
    if DISPLAY_FOOTER:
        print(
            f"#{message_id} | PnD Events | tracked: {len(pnd_events)}, Retired: {len(retired_pnd_events)}"
        )

    outdate_events(pnd_events=pnd_events, retired_pnd_events=retired_pnd_events)
