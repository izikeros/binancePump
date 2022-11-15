import datetime
from dataclasses import dataclass

from binance_pump.logger import logger


@dataclass
class PairChange:
    """Keep data about change in price and volume.

    Initialize if there was no previous data about this pair.

    If there was previous data, calculate change in price, volume, total trades, etc..

    Attributes:
        symbol: pair name
        price_change_perc: change in price in percentage
        volume_change_perc: change in volume in percentage
        price_change: change in price
        volume_change: change in volume
        price: current price
        volume: current volume
        total_trades: current total trades
        is_added: flag if this pair is already in the list of PnD events

    """

    symbol: str
    prev_price: float
    price: float  # current price
    open_price: float  # open price (marking "o" - for candle open?
    total_trades: int
    volume: float
    is_added: bool
    event_time: datetime.datetime
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


def extract_data_from_ticker(ticker: dict):
    """Extract data from ticker and return a dict.

    This is a helper function that extracs data from the


    """
    # Extract data from dict for the ticker
    symbol = ticker["s"]
    price = float(ticker["c"])
    total_trades = int(ticker.get("n", 0))
    open_price = float(ticker["o"])
    volume = float(ticker["v"])
    event_time = datetime.datetime.fromtimestamp(int(ticker["E"]) / 1000)
    ticker_dict = {
        "symbol": symbol,
        "price": price,
        "total_trades": total_trades,
        "open_price": open_price,
        "volume": volume,
        "event_time": event_time,
    }
    return ticker_dict


def existing_price_change(price_changes: dict[str, PairChange], ticker: dict):
    ticker_dict = extract_data_from_ticker(ticker)
    s = ticker_dict["symbol"]
    prev_price = price_changes[s].price
    prev_volume = price_changes[s].volume
    price_changes[s].event_time = ticker_dict["event_time"]
    price_changes[s].prev_price = prev_price
    price_changes[s].prev_volume = prev_volume
    price_changes[s].price = ticker_dict["price"]
    price_changes[s].total_trades = ticker_dict["total_trades"]
    price_changes[s].open_price = ticker_dict["open_price"]
    price_changes[s].volume = ticker_dict["volume"]
    price_changes[s].is_added = False
    logger.debug(f"    Updated PairChange entry for symbol: {s}")


def new_price_change(price_changes: dict[str, PairChange], ticker: dict):
    ticker_dict = extract_data_from_ticker(ticker)

    new_price_change_item = PairChange(
        symbol=ticker_dict["symbol"],
        prev_price=ticker_dict["price"],
        price=ticker_dict["price"],
        total_trades=ticker_dict["total_trades"],
        open_price=ticker_dict["open_price"],
        volume=ticker_dict["volume"],
        is_added=False,
        event_time=ticker_dict["event_time"],
        prev_volume=ticker_dict["volume"],
    )
    price_changes[ticker_dict["symbol"]] = new_price_change_item
    logger.debug(f"    Added new PairChange entry for symbol: {ticker_dict['symbol']}")
