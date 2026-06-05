from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from skill_lab.market_data.calendar import FileTradeCalendar, WeekdayTradeCalendar


def test_weekday_trade_calendar_navigation():
    calendar = WeekdayTradeCalendar()
    assert calendar.is_trade_date("2026-06-05")
    assert not calendar.is_trade_date("2026-06-06")
    assert calendar.previous_trade_date("2026-06-08") == "2026-06-05"
    assert calendar.next_trade_date("2026-06-05") == "2026-06-08"
    assert calendar.latest_trade_date_on_or_before("2026-06-07") == "2026-06-05"


def test_file_trade_calendar():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "calendar.csv"
        path.write_text("date,is_trade_date\n2026-06-05,1\n2026-06-08,1\n2026-06-06,0\n", encoding="utf-8")
        calendar = FileTradeCalendar(path)
        assert calendar.is_trade_date("2026-06-05")
        assert not calendar.is_trade_date("2026-06-06")
        assert calendar.next_trade_date("2026-06-05") == "2026-06-08"


if __name__ == "__main__":
    test_weekday_trade_calendar_navigation()
    test_file_trade_calendar()
