import json

from binancepump import logger

import rel
import websocket
from binancepump.process_message import process_message


rel.safe_read()
endpoint = "wss://stream.binance.com:9443"

price_changes = {}
price_groups = {}


def on_message(ws, message):
    json_message = json.loads(message)
    logger.debug("Received message with %d symbols", len(json_message))
    process_message(
        tickers=json_message, price_groups=price_groups, price_changes=price_changes
    )


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


if __name__ == "__main__":
    with open("api_config.json") as json_data:
        api_config = json.load(json_data)
        json_data.close()
    stream = f"/ws/!miniTicker@arr"
    socket = endpoint + stream

    ws = websocket.WebSocketApp(
        socket,
        on_message=on_message,
        on_close=on_close,
    )
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
