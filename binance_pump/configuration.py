from pathlib import Path

from pydantic import BaseModel

# from pydantic_yaml import YamlModel


class Configuration(BaseModel):
    STREAM = "/ws/!miniTicker@arr"
    # --- Traces ---
    # directory to store dumps from monitoring
    TRACES_DIRECTORY: Path = Path(__file__).parent.parent / "traces"

    SAVE_RETIRED_EVENT_TRACES: bool = True

    # messages can be saved in a file with jsonlines library - one json object per line
    SAVE_MESSAGE_TRACES: bool = True  # TODO: KS: 2022-04-18: implement

    # save config (in yaml format)
    SAVE_CONFIG: bool = False

    # save active event traces (json)
    SAVE_ACTIVE_EVENT_TRACES: bool = False

    SHOW_ONLY_PAIR: str = (
        "USDT"  # Select nothing for all, only selected currency will be shown
    )
    SHOW_LIMIT: int = 3000000  # How many top pairs to show for each sorting criterion
    PRICE_CHANGE_PERC_TH: float = 0.02  # min percentage change (default 0.05)
    TOTAL_PRICE_PERC_TH: float = 0.05  # min percentage change (default 0.05)
    VOLUME_CHANGE_PERC_TH: float = 0.1  # min percentage change (default 0.05)
    # TOTAL_VOLUME_PERC_TH: float = 0.05  # min percentage change (default 0.05)

    OUTDATING_METHOD = "linear"  # "linear" or "exponential"
    TICK_SUBTRACT_VALUE: float = 1
    TICK_REDUCE_MULTIPLIER: float = 0.9
    SKIP_SAVING_EVENTS_SHORTER_THAN_N_TICKS: int = 3  # in ticks

    DISPLAY_FOOTER = False

    ENDPOINT = "wss://stream.binance.com:9443"


conf = Configuration()
