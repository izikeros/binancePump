import datetime as dt


class PriceChange:
    def __init__(
        self,
        symbol,
        prev_price,
        price,
        total_trades,
        open,
        volume,
        isPrinted,
        event_time,
        prev_volume,
    ):
        self.symbol = symbol
        self.prev_price = prev_price
        self.price = price
        self.total_trades = total_trades
        self.open = open
        self.volume = volume
        self.isPrinted = isPrinted
        self.event_time = event_time
        self.prev_volume = prev_volume

    def __repr__(self):
        return repr(self)
        # return repr(
        #     self.symbol,
        #     self.prev_price,
        #     self.price,
        #     self.total_trades,
        #     self.open,
        #     self.volume,
        #     self.isPrinted,
        #     self.event_time,
        #     self.prev_volume,
        # )

    @property
    def volume_change(self):
        return self.volume - self.prev_volume

    @property
    def volume_change_perc(self):
        return self.volume_change / self.prev_volume * 100

    @property
    def price_change(self):
        return self.price - self.prev_price

    @property
    def price_change_perc(self):
        if self.prev_price == 0 or self.price == 0:
            return 0
        else:
            return self.price_change / self.prev_price * 100

    def is_pump(self, lim_perc):
        return self.price_change_perc() >= lim_perc

    def is_dump(self, lim_perc):
        if lim_perc > 0:
            lim_perc = -lim_perc
        return self.price_change_perc() <= lim_perc


def add_price_change_to_list(price_changes_list, ticker: dict):
    """Initialize price_changes object with data from ticker dict."""
    symbol = ticker["s"]
    price = float(ticker["c"])
    total_trades = int(ticker["n"])
    open_price = float(ticker["o"])
    volume = float(ticker["v"])
    event_time = dt.datetime.fromtimestamp(int(ticker["E"]) / 1000)
    price_changes_list.append(
        PriceChange(
            symbol=symbol,
            prev_price=price,
            price=price,
            total_trades=total_trades,
            open=open_price,
            volume=volume,
            isPrinted=False,
            event_time=event_time,
            prev_volume=volume,
        )
    )
    return price_changes_list
