#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

import jsonlines
import rel
import websocket
from binance_pump import logger
from binance_pump.process_message import process_message
from binance_pump.configuration import conf
from binance_pump.utlis import clear_console_screen, seconds_to_h_m_s



DISPLAY_FOOTER = False
rel.safe_read()
endpoint = "wss://stream.binance.com:9443"

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
    logger.debug("Received message with %d symbols", len(json_message))

    process_message(
        tickers=json_message,
        pnd_events=pnd_events,
        price_changes=price_changes,
        retired_pnd_events=retired_pnd_events,
        message_id=message_counter,
    )
    #logger.debug("Message processed")

    if DISPLAY_FOOTER:
        time_now = datetime.now()
        elapsed_time = time_now - start_time
        mc_str = "Message counter: %d" % message_counter
        rr_str = "Rate: %.2f" % (message_counter / elapsed_time.total_seconds())
        rt_str = "Running time: %s" % seconds_to_h_m_s(elapsed_time.total_seconds())
        n_events_str = "Number of events: %d" % len(pnd_events)
        print(", ".join([mc_str, rr_str, rt_str, n_events_str]))

    # save pnd_events (list of non-serializable objects) with pickle
    if conf.SAVE_ACTIVE_EVENT_TRACES:
        with open(active_trace_file_path, "wt") as f:
            pnd_events_json = {k: event.json() for k, event in pnd_events.items()}
            json.dump(pnd_events_json, f)

    if conf.SAVE_RETIRED_EVENT_TRACES:
        with open(retired_trace_file_path, "wt") as f:
            retired_pnd_events_json = [event.json() for event in retired_pnd_events]
            json.dump(retired_pnd_events_json, f)

    if conf.SAVE_MESSAGE_TRACES:
        with jsonlines.open(messages_file_path, mode="a") as writer:
            writer.write(json_message)

    if message_counter > 10:
        print("")
        pass


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def run_on_websockets():
    with open(Path(__file__).parent.parent / "api_config.json") as json_data:
        api_config = json.load(json_data)
        json_data.close()
    stream = "/ws/!miniTicker@arr"
    socket = endpoint + stream
    if conf.SAVE_CONFIG:
        with open(config_file_path, "wt") as f:
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
    with jsonlines.open(messages_input_file_path, mode="r") as reader:
        for obj in reader:
            on_message(None, json.dumps(obj))


if __name__ == "__main__":
    # run_on_websockets()
    run_on_traces()
