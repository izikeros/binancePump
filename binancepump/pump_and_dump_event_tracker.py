from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

import numpy as np
from termcolor import colored


@dataclass
class PumpOrDumpEventTracker:
    """Pump and Dump event class."""

    symbol: str
    tick_count: int
    absolute_price_change: float
    relative_price_change: float
    total_volume_change: float
    last_price: float
    last_event_time: datetime
    open_price: Tuple[float]
    volume: float
    is_printed: bool

    def __getitem__(self, key):
        return getattr(self, key)

    def to_string(self, is_colored, smsg=""):
        self.is_printed = True
        time_fmt = "%H:%M:%S"

        s = self.symbol
        t = self.last_event_time.strftime(time_fmt)
        tck = str(self.tick_count)
        rpch = f"{self.relative_price_change:2.2f}"
        # tpch = f"{self.absolute_price_change:2.2f}"
        vch = f"{self.total_volume_change:2.2f}"
        lp = str(self.last_price)
        op = str(self.open_price)

        # TODO: KS: 2022-03-29: Add configuration parameter to display volume and log volume
        # last volume
        lv = str(self.volume)
        # last logarithmic volume
        llv = str(np.log10(self.volume))
        # retval = f"{smsg:5} | {s:10s} | {t} | Ticks: {tck:3s} | RPCh: {rpch:5s} |"
        # "TPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp} | Volume:{lv} | LogV {llv}"

        #retval = f"{smsg:5} | {s:12s} | {t} | Ticks: {tck:3s} | RelPCh: {rpch:5s} | TotPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp}"
        smsg = f"{smsg}"
        retval = f"{smsg:5} | {s:12s} | {t} | Ticks: {tck:3s} | RelPCh: {rpch:5s} | VCh: {vch:4s} | P: ${lp} | oP: ${op}"
        if not is_colored:
            return retval
        else:
            # TODO: KS: 2022-03-29: Replace termcolor with rich
            return colored(retval, self.console_color)

    @property
    def console_color(self):
        if self.relative_price_change < 0:
            return "red"
        else:
            return "green"
