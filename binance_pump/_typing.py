from price_change import PairChange
from pump_and_dump_event_tracker import PumpOrDumpEventTracker

PnDEventsT = dict[str, PumpOrDumpEventTracker]
PriceChangesT = dict[str, PairChange]
RetiredPnDEventsT = list[PumpOrDumpEventTracker]
