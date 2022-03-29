import datetime


def extract_data_from_ticker(ticker):
    # Extract data from dict for the ticker
    symbol = ticker["s"]
    price = float(ticker["c"])
    total_trades = int(ticker.get("n", 0))
    open_price = float(ticker["o"])
    volume = float(ticker["v"])
    event_time = datetime.datetime.fromtimestamp(int(ticker["E"]) / 1000)
    return (
        symbol,
        event_time,
        open_price,
        price,
        total_trades,
        volume,
    )
