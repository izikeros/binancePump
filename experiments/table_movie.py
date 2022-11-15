"""Same as the table_movie.py but uses Live to update"""
import time
from contextlib import contextmanager

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.table import Table

i = 0
TABLE_DATA = [
    [
        str(i),
        "Star Wars Ep. [b]IV[/]: [i]A New Hope",
        "$11,000,000",
        "$1,554,475",
        "$775,398,007",
    ],
    [
        "May 21, 1980",
        "Star Wars Ep. [b]V[/]: [i]The Empire Strikes Back",
        "$23,000,000",
        "$4,910,483",
        "$547,969,004",
    ],
    [
        "May 25, 1983",
        "Star Wars Ep. [b]VI[/b]: [i]Return of the Jedi",
        "$32,500,000",
        "$23,019,618",
        "$475,106,177",
    ],
    [
        "May 19, 1999",
        "Star Wars Ep. [b]I[/b]: [i]The phantom Menace",
        "$115,000,000",
        "$64,810,870",
        "$1,027,044,677",
    ],
    [
        "May 16, 2002",
        "Star Wars Ep. [b]II[/b]: [i]Attack of the Clones",
        "$115,000,000",
        "$80,027,814",
        "$656,695,615",
    ],
    [
        "May 19, 2005",
        "Star Wars Ep. [b]III[/b]: [i]Revenge of the Sith",
        "$115,500,000",
        "$380,270,577",
        "$848,998,877",
    ],
]

console = Console()

BEAT_TIME = 0.04


@contextmanager
def beat(length: int = 1) -> None:
    yield
    time.sleep(length * BEAT_TIME)


while 1:
    console.clear()
    table = Table(show_footer=False)
    table_centered = Align.center(table)
    with Live(table_centered, console=console, screen=False, refresh_per_second=3):
        for row in TABLE_DATA:
            table.add_row(*row)
        i += 1
        TABLE_DATA[0][0] = str(i)
        time.sleep(50 * BEAT_TIME)
