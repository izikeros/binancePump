import datetime as dt
from typing import List

from binance_pump.utlis import color_me
from pydantic import BaseModel


class PumpOrDumpEventTracker(BaseModel):
    """Pump and Dump event class."""

    symbol: str

    # for how many ticks the event has been active
    tick_count: int

    # in each iteration add two tick if the event is active and subtract one tick if the event is inactive
    # if the event is inactive, the actuality will be decreasing
    actuality: float  # TODO: KS: 2022-04-10: implement

    # difference between first price event was qualified as PnD and current price
    total_price_change: float

    # difference between first price event was qualified as PnD
    # and current price relative to first price expressed in %
    total_price_change_perc: float

    # price change since last tick
    price_change: float

    # percentage price change since last tick
    price_change_perc: float

    # price change that triggered the event
    initial_price_change_perc: float

    # maximum price change (%) observed when pnd event was active
    max_total_price_change_prc: float

    # prices observed when pnd event was active
    price_history: List[float]

    # prices observed when pnd event was active
    volume_history: List[float]

    # timestamps related to price_history and volume_history
    timestamps: List[dt.datetime]

    # trace length
    length: int

    # percentage volume change since last tick
    volume_change_perc: float

    # volume change that triggered the event
    initial_volume_change_perc: float

    # todo: consider something like aggregated volume change

    # price from last tick
    last_price: float

    # time of last tick
    last_event_time: dt.datetime

    # price from the open (of the candle?)
    open_price: float

    volume: float

    # was this event already printed because fulfills other criteria for PnD?
    is_printed: bool

    def __getitem__(self, key):
        return getattr(self, key)

    def to_string(self):
        self.is_printed = True
        time_fmt = "%H:%M:%S"

        s = self.symbol.rjust(13)
        # t = self.last_event_time.strftime(time_fmt)

        pch = color_me(f"PCh {self.price_change:.4f}".ljust(12), self.price_change)
        rpch = color_me(
            f"PCh {self.price_change_perc/100:2.3%}".ljust(12), self.price_change_perc
        )
        tpchp = color_me(
            f"TPCh {self.total_price_change_perc/100:2.3%}".ljust(12),
            self.total_price_change_perc,
        )
        vch = color_me(
            f"VCh {self.volume_change_perc/100:2.3%}".ljust(12), self.volume_change_perc
        )
        lp = f"LP {self.last_price:.4f}".ljust(14)
        mT = f"Tcks {self.actuality}".ljust(10)

        retval = f"{s} | {mT} | {pch} | {rpch} | {vch} | {tpchp} | {lp}"
        return retval

    def to_dict(self, columns=("price_change_perc", "volume_change_perc", "actuality")):
        dct = {}
        if "price_change_perc" in columns:
            dct["price_change_perc"] = self.price_change_perc

        if "actuality" in columns:
            dct["actuality"] = self.actuality

        if "volume_change_perc" in columns:
            dct["volume_change_perc"] = self.volume_change_perc
        return dct

    @property
    def console_color(self):
        if self.price_change_perc < 0:
            return "red"
        else:
            return "green"
