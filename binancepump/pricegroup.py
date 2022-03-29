import numpy as np
from termcolor import colored


class PriceGroup:
    def __init__(
        self,
        symbol,
        tick_count,
        total_price_change,
        relative_price_change,
        total_volume_change,
        last_price,
        last_event_time,
        open,
        volume,
        isPrinted,
    ):
        self.symbol = symbol
        self.tick_count = tick_count
        self.total_price_change = total_price_change
        self.relative_price_change = relative_price_change
        self.total_volume_change = total_volume_change
        self.last_price = last_price
        self.last_event_time = last_event_time
        self.open = (open,)
        self.volume = volume
        self.isPrinted = isPrinted

    def __repr__(self):
        return repr(self)

    def __getitem__(self, key):
        return getattr(self, key)

    def to_string(self, isColored, smsg=""):
        self.isPrinted = True
        # fmt_1 = "Symbol:{}\t Time:{}\t Ticks:{}\t RPCh:{}\t TPCh:{}\t VCh:{}\t LP:{}\t LV:{}\t"
        # fmt_2 = "{}\t Time:{}\t Ticks:{}\t RPCh:{}\t TPCh:{}\t VCh:{}\t LP:{}\t LV:{}\t"
        time_fmt = "%H:%M:%S"
        # retval = fmt_2.format(
        #     self.symbol,
        #     self.last_event_time.strftime(time_fmt),
        #     self.tick_count,
        #     "{0:2.2f}".format(self.relative_price_change),
        #     "{0:2.2f}".format(self.total_price_change),
        #     "{0:2.2f}".format(self.total_volume_change),
        #     self.last_price,
        #     self.volume,
        # )
        s = self.symbol
        t = self.last_event_time.strftime(time_fmt)
        tck = str(self.tick_count)
        rpch = f"{self.relative_price_change:2.2f}"
        tpch = f"{self.total_price_change:2.2f}"
        vch = f"{self.total_volume_change:2.2f}"
        lp = str(self.last_price)
        lv = str(self.volume)
        llv = str(np.log10(self.volume))
        # retval = f"{smsg:5} | {s:10s} | {t} | Ticks: {tck:3s} | RPCh: {rpch:5s} |"
        # "TPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp} | Volume:{lv} | LogV {llv}"
        retval = f"{smsg:5} | {s:12s} | {t} | Ticks: {tck:3s} | RelPCh: {rpch:5s} | TotPch: {tpch:5s} | VCh: {vch:4s} | P: ${lp}"
        if not isColored:
            return retval
        else:
            return colored(retval, self.console_color)

    @property
    def console_color(self):
        if self.relative_price_change < 0:
            return "red"
        else:
            return "green"
