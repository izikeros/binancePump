from collections import namedtuple

from configuration import TOTAL_PRICE_PERC_TH

Criterion = namedtuple("Criterion", ["type", "label", "threshold"])
criteria = [
    # ("tick_count", "Ticks"),
    Criterion(
        type="total_price_change_perc",
        label="Total Price Change Prc",
        threshold=TOTAL_PRICE_PERC_TH,
    ),
    # Criterion(
    #     type="price_change_perc",
    #     label="Price Change Prc",
    #     threshold=PRICE_PERC_TH,
    # ),
    # Criterion(
    #     type="volume_change_perc",
    #     label="Volume Change Prc",
    #     threshold=VOLUME_PERC_TH,
    # ),
]
