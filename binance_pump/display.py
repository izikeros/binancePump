from typing import Dict
from typing import List

from configuration import SHOW_LIMIT
from pump_and_dump_event_tracker import PumpOrDumpEventTracker
from rich.console import Console

console = Console()


def display_interesting_coins(
    sorted_pnd_symbols: List[str],
    reason_msg: str,
    pnd_events: Dict[str, PumpOrDumpEventTracker],
):
    """Function that prints top PnD events from the list and send to messenger.

    Args:
        sorted_pnd_symbols: List of PriceGroups sorted by given criterion
                                    (e.g. the biggest relative price change).
        reason_msg: Message to be printed (reason for being interesting e.g. top relative volume change
        pnd_events: Dictionary of price groups.

    """
    if len(sorted_pnd_symbols) > 0:
        sorted_pnd_symbols = list(reversed(sorted_pnd_symbols))
        max_range = min(len(sorted_pnd_symbols), SHOW_LIMIT)
        for symbol_idx in range(max_range):
            # check if the symbol has been printed (e.g. due to being in the top N in other
            # ranking
            max_pnd_from_sorted_symbol = sorted_pnd_symbols[symbol_idx]
            max_pnd = pnd_events[max_pnd_from_sorted_symbol]

            if not max_pnd.is_printed:
                short_reason_message = create_short_message(reason_msg)
                # print the interesting symbol info to the console
                console.print(max_pnd.to_string(short_reason_message))
            else:
                print("printed!")


def create_short_message(msg):
    """Create a short message from a long message. Take first letters from each word.

    Args:
        msg: Long message.

    Returns:
        Short message.
    """
    short_msg = "".join([word[0] for word in msg.split()])
    return short_msg
