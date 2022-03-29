from datetime import datetime

from binancepump.price_group import PriceGroup

COLOR_RED = "\x1b[31m"
COLOR_GREEN = "\x1b[32m"


class TestPriceGroup:
    def setup_method(self):
        cr_date = datetime(2021, 10, 31, 18, 23, 29, 227)

        self.PG = PriceGroup(
            symbol="ETHBTC",
            tick_count=10,
            total_price_change=0.1,
            relative_price_change=0.1,
            total_volume_change=0.1,
            last_price=0.1,
            last_event_time=cr_date,
            open_price=0.1,
            volume=0.1,
            is_printed=True,
        )

    def test_to_string__no_color(self):
        self.PG.relative_price_change = 2.2
        txt = self.PG.to_string(is_colored=False)
        assert txt.startswith("   ")

    def test_to_string__relative_change_negative(self):
        self.PG.relative_price_change = -3.2
        txt = self.PG.to_string(is_colored=True)
        assert txt.startswith(COLOR_RED)
        assert len(txt) > 70

    def test_to_string__relative_change_positive(self):
        self.PG.relative_price_change = 2.2
        txt = self.PG.to_string(is_colored=True)
        assert txt.startswith(COLOR_GREEN)
        assert len(txt) > 70

    def test_console_color__relative_change_positive(self):
        self.PG.relative_price_change = 2.2
        assert self.PG.console_color == "green"

    def test_console_color__relative_change_negative(self):
        self.PG.relative_price_change = -3.2
        assert self.PG.console_color == "red"
