from binancepump import logger
from binancepump.extract_data_from_ticker import extract_data_from_ticker


class PriceChange:
    def __init__(
        self,
        symbol,
        prev_price,
        price,
        total_trades,
        open_price,
        volume,
        is_printed,
        event_time,
        prev_volume,
    ):
        """Initialize the PriceChange object with current data.
        If there was previous data, calculate dynamic properties reflecting
         change in price, volume, etc.
        """
        self.symbol = symbol
        self.prev_price = prev_price
        self.price = price
        self.total_trades = total_trades
        self.open_price = open_price
        self.volume = volume
        self.is_printed = is_printed
        self.event_time = event_time
        self.prev_volume = prev_volume

    def __repr__(self):
        symbol = f"symbol={self.symbol}"
        prev_price = f"prev_price={self.prev_price}"
        price = f"price={self.price}"
        total_trades = f"total_trades={self.total_trades}"
        open_price = f"open={self.open_price}"
        volume = f"volume={self.volume}"
        is_printed = f"is_printed={self.is_printed}"
        event_time = f"event_time={self.event_time}"
        prev_volume = f"prev_volume={self.prev_volume}"
        return f"PriceChange({symbol}, {prev_price}, {price}, {total_trades}, {open_price}, {volume}, {is_printed}, {event_time}, {prev_volume})"

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
        return self.price_change_perc() >= lim_perc

    def is_dump(self, lim_perc):
        if lim_perc > 0:
            lim_perc = -lim_perc
        return self.price_change_perc() <= lim_perc


def initialize_symbol_entry_in_price_changes_list(price_changes_list, ticker):
    """Initialize object in price_changes for given symbol"""
    (
        symbol,
        event_time,
        open_price,
        price,
        total_trades,
        volume,
    ) = extract_data_from_ticker(ticker)

    price_changes_list.append(
        PriceChange(symbol=symbol, prev_price=price, price=price, total_trades=total_trades,
                    open_price=open_price, volume=volume, is_printed=False, event_time=event_time,
                    prev_volume=volume)
    )
    logger.debug(f"    Initialized {symbol} in price_changes_list")
