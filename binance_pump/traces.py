import json
from pathlib import Path
from typing import List

import numpy as np

from pump_and_dump_event_tracker import PumpOrDumpEventTracker


class Traces:
    def __init__(self, traces_dir: Path):
        self.traces: List[PumpOrDumpEventTracker] = []
        self.traces_dir = traces_dir

    def _load_traces_as_json(self, filename):
        # load trace
        with open(self.traces_dir / filename) as f:
            traces_json = json.load(f)
        return traces_json

    def get_events(self, filename):
        traces_json = self._load_traces_as_json(filename)
        # convert json to event models
        self.traces = [PumpOrDumpEventTracker.parse_raw(t) for t in traces_json]

    def sort_events_by_price(self, reverse=True):
        self.traces.sort(key=lambda x: x.max_total_price_change, reverse=reverse)

    def sort_events_by_length(self, reverse=True):
        self.traces.sort(key=lambda x: x.length, reverse=reverse)

    def remove_short_events(self, min_length=3):
        self.traces = [t for t in self.traces if len(t.price_history) >= min_length]

    def lent(self):
        return len(self.traces)


# TODO: KS: 2022-04-19: add this as method to ActiveTraces
def new_pnd(coin, pnd_events):
    pnd_events[coin.symbol] = PumpOrDumpEventTracker(
        symbol=coin.symbol,
        tick_count=1,
        actuality=2,
        total_price_change=coin.price_change,
        total_price_change_perc=coin.price_change_perc,
        price_change=coin.price_change,
        price_change_perc=coin.price_change_perc,
        initial_price_change_perc=coin.price_change_perc,
        max_total_price_change_prc=-np.inf,
        price_history=[coin.price],
        volume_history=[coin.volume],
        timestamps=[coin.event_time],
        length=1,
        volume_change_perc=coin.volume_change_perc,
        initial_volume_change_perc=coin.volume_change_perc,
        last_price=coin.prev_price,
        last_event_time=coin.event_time,
        open_price=coin.price,
        volume=coin.volume,
        is_printed=False,
    )
    coin.is_added = True


# TODO: KS: 2022-04-19: add this as method to Traces
def existing_pnd(coin, pnd_events, is_pnd):
    s = coin.symbol
    o = pnd_events[s].open_price
    c = coin.price
    l = pnd_events[s].last_price
    total_price_change_perc = 100 * abs(c - o) / o

    prev_v = coin.prev_volume

    if is_pnd:
        pnd_events[s].tick_count += 1
        pnd_events[s].actuality += 2
    else:
        pnd_events[s].tick_count += 1
        pnd_events[s].actuality += 0
    pnd_events[s].total_price_change = abs(c - o)
    pnd_events[s].total_price_change_perc = total_price_change_perc
    pnd_events[s].price_change = c - l
    pnd_events[s].price_change_perc = 100 * (c - l) / l
    pnd_events[s].max_total_price_change_prc = max(
        pnd_events[s].max_total_price_change_prc, total_price_change_perc
    )
    pnd_events[s].price_history.append(c)
    pnd_events[s].volume_history.append(coin.volume)
    pnd_events[s].timestamps.append(coin.event_time)
    pnd_events[s].length += 1
    pnd_events[s].volume_change_perc = 100 * (coin.volume - prev_v) / prev_v
    pnd_events[s].last_price = coin.price
    pnd_events[s].last_event_time = coin.event_time
    pnd_events[s].volume = coin.volume
