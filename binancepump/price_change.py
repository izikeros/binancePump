from dataclasses import dataclass


@dataclass
class PriceChange:
    """Initialize the PriceChange object with current data.
    If there was previous data, calculate dynamic properties reflecting
     change in price, volume, etc.
    """

    symbol: str
    prev_price: float
    price: float
    total_trades: int
    volume: float
    is_printed: bool
    event_time: str
    prev_volume: float

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
            return 100 * self.price_change / self.prev_price

    def is_pump(self, lim_perc):
        return self.price_change_perc >= lim_perc

    def is_dump(self, lim_perc):
        if lim_perc > 0:
            lim_perc = -lim_perc
        return self.price_change_perc <= lim_perc
