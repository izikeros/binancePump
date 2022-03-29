import numpy as np
from termcolor import colored


# TODO: KS: 2022-03-29: Consider using dataclasses.dataclass
class PriceGroup:
    def __init__(
        self,
        symbol: str,
        tick_count: int,
        total_price_change: float,
        relative_price_change: float,
        total_volume_change: float,
        last_price: float,
        last_event_time,
        open_price: float,
        volume: float,
        is_printed: bool,
    ):
        self.symbol = symbol
        self.tick_count = tick_count
        self.total_price_change = total_price_change
        self.relative_price_change = relative_price_change
        self.total_volume_change = total_volume_change
        self.last_price = last_price
        self.last_event_time = last_event_time
        self.open = (open_price,)
        self.volume = volume
        self.isPrinted = is_printed

    def __repr__(self):
        symbol = f"symbol={self.symbol}"
        tick_count = f"tick_count={self.tick_count}"
        total_price_change = f"total_price_change={self.total_price_change}"
        relative_price_change = f"relative_price_change={self.relative_price_change}"
        total_volume_change = f"total_volume_change={self.total_volume_change}"
        last_price = f"last_price={self.last_price}"
        last_event_time = f"last_event_time={self.last_event_time}"
        open_price = f"open_price={self.open}"
        volume = f"volume={self.volume}"
        is_printed = f"is_printed={self.isPrinted}"

        return (
            f"PriceGroup({symbol}, {tick_count}, {total_price_change},"
            f" {relative_price_change}, {total_volume_change},"
            f" {last_price}, {last_event_time}, {open_price},"
            f" {volume}, {is_printed}) "
        )

    def __getitem__(self, key):
        return getattr(self, key)

    def to_string(self, is_colored, smsg=""):
        self.isPrinted = True
        time_fmt = "%H:%M:%S"

        s = self.symbol
        t = self.last_event_time.strftime(time_fmt)
        tck = str(self.tick_count)
        rpch = f"{self.relative_price_change:2.2f}"
        tpch = f"{self.total_price_change:2.2f}"
        vch = f"{self.total_volume_change:2.2f}"
        lp = str(self.last_price)

        # TODO: KS: 2022-03-29: Add configuration parameter to display volume and log volume
        # last volume
        lv = str(self.volume)
        # last logarithmic volume
        llv = str(np.log10(self.volume))
        # retval = f"{smsg:5} | {s:10s} | {t} | Ticks: {tck:3s} | RPCh: {rpch:5s} |"
        # "TPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp} | Volume:{lv} | LogV {llv}"

        retval = f"{smsg:5} | {s:12s} | {t} | Ticks: {tck:3s} | RelPCh: {rpch:5s} | TotPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp}"
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
