from typing import Dict
from typing import List

from binance_pump.configuration import conf
from binance_pump.pump_and_dump_event_tracker import PumpOrDumpEventTracker
from rich.console import Console

console = Console()


def display_interesting_coins(
    sorted_pnd_symbols: List[str],
    pnd_events: Dict[str, PumpOrDumpEventTracker],
):
    """Function that prints top PnD events from the list and send to messenger.

    Args:
        sorted_pnd_symbols: List of PriceGroups sorted by given criterion
                                    (e.g. the biggest relative price change).
        pnd_events: Dictionary of price groups.

    """
    if len(sorted_pnd_symbols) > 0:
        sorted_pnd_symbols = list(reversed(sorted_pnd_symbols))
        max_range = min(len(sorted_pnd_symbols), conf.SHOW_LIMIT)
        for symbol_idx in range(max_range):
            # check if the symbol has been printed (e.g. due to being in the top N in other
            # ranking
            max_pnd_from_sorted_symbol = sorted_pnd_symbols[symbol_idx]
            max_pnd = pnd_events[max_pnd_from_sorted_symbol]

            # print the interesting symbol info to the console
            console.print(max_pnd.to_string())
