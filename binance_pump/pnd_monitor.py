#!/usr/bin/env python3
"""
Pump & Dump monitor
- fetching data from Binance websocket (online, real-time) or from a trace file (offline)
- detecting pump & dump events
"""
import argparse
import json
from datetime import datetime
from typing import NoReturn

import jsonlines
import rel
import websocket
from binance_pump.configuration import conf
from binance_pump.logger import logger
from binance_pump.process_message import process_message
from binance_pump.utlis import clear_console_screen
from binance_pump.utlis import seconds_to_h_m_s

# Registered Event Listener.
# Provides standard (pyevent) interface and functionality without external dependencies
rel.safe_read()


price_changes = {}
pnd_events = {}
retired_pnd_events = []

start_time = datetime.now()
message_counter = 0

# set filename for output files
todays_date = datetime.now().strftime("%y%m%d_%H%M%S")
active_trace_file_path = conf.TRACES_DIRECTORY / f"{todays_date}_active_trace.json"
retired_trace_file_path = conf.TRACES_DIRECTORY / f"{todays_date}_retired_trace.json"
config_file_path = conf.TRACES_DIRECTORY / f"{todays_date}_config.yaml"
messages_file_path = conf.TRACES_DIRECTORY / f"{todays_date}_messages.jsonl"
messages_input_file_path = conf.TRACES_DIRECTORY / "220419_071958_messages.jsonl"


def on_message(ws, message):
    global message_counter
    if message_counter is None:
        message_counter = 0
    else:
        message_counter += 1

    # Convert response to JSON
    json_message = json.loads(message)

    clear_console_screen()
    logger.debug(f"Received message with {len(json_message)} symbols")

    process_message(
        tickers=json_message,
        pnd_events=pnd_events,
        price_changes=price_changes,
        retired_pnd_events=retired_pnd_events,
        message_id=message_counter,
    )

    if conf.DISPLAY_FOOTER:
        display_status_line(message_counter)
    # save pnd_events (list of non-serializable objects) with pickle
    if conf.SAVE_ACTIVE_EVENT_TRACES:
        with open(active_trace_file_path, "w") as f:
            pnd_events_json = {k: event.json() for k, event in pnd_events.items()}
            json.dump(pnd_events_json, f)

    if conf.SAVE_RETIRED_EVENT_TRACES:
        with open(retired_trace_file_path, "w") as f:
            retired_pnd_events_json = [event.json() for event in retired_pnd_events]
            json.dump(retired_pnd_events_json, f)

    if conf.SAVE_MESSAGE_TRACES:
        with jsonlines.open(messages_file_path, mode="a") as writer:
            writer.write(json_message)

    if message_counter > 10:
        print("")


def display_status_line(message_count: int) -> NoReturn:
    time_now = datetime.now()
    elapsed_time = time_now - start_time
    mc_str = f"Message counter: {message_count}"
    rr_str = "Rate: %.2f" % (message_count / elapsed_time.total_seconds())
    rt_str = f"Running time: {seconds_to_h_m_s(elapsed_time.total_seconds())}"
    n_events_str = "Number of events: %d" % len(pnd_events)
    print(", ".join([mc_str, rr_str, rt_str, n_events_str]))


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def run_on_websockets():
    stream = conf.STREAM
    socket = conf.ENDPOINT + stream
    if conf.SAVE_CONFIG:
        with open(config_file_path, "w") as f:
            config_yaml = conf.yaml()
            f.write(config_yaml)
    ws = websocket.WebSocketApp(
        socket,
        on_message=on_message,
        on_close=on_close,
    )
    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()


def run_on_traces():
    """Run pump & dump detection on a messaged saved in a file as a trace."""
    with jsonlines.open(messages_input_file_path, mode="r") as reader:
        for obj in reader:
            on_message(None, json.dumps(obj))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pump and dump detection.")

    parser.add_argument(
        "--websocket",
        action="store_true",
        default=False,
        help="run on traces (offline)",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        default=False,
        help="run on real-time websocket data",
    )
    args = parser.parse_args()

    if args.websocket:
        run_on_websockets()
    elif args.trace:
        run_on_traces()
    else:
        parser.print_help()
