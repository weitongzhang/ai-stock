from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "skills/stock-selection/a-share-market-flow-analyst/scripts/collect_market_breadth.py"
    spec = spec_from_file_location("collect_market_breadth", path)
    module = module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class FakeSeries(list):
    def map(self, fn):
        return FakeSeries(fn(value) for value in self)

    def sum(self):
        return sum(self)

    def __gt__(self, other):
        return FakeSeries(value > other for value in self)

    def __lt__(self, other):
        return FakeSeries(value < other for value in self)

    def __eq__(self, other):
        return FakeSeries(value == other for value in self)


class FakeFrame:
    columns = ["涨跌幅", "成交额"]

    def __init__(self):
        self.data = {"涨跌幅": FakeSeries([1, -1, 0]), "成交额": FakeSeries([100, 200, 300])}

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return 3


class FakeAk:
    @staticmethod
    def stock_zh_a_spot_em():
        raise ConnectionError("eastmoney unavailable")

    @staticmethod
    def stock_zh_a_spot():
        return FakeFrame()


def test_spot_collection_falls_back_to_sina():
    module = load_module()
    rows = []
    errors = []
    module.collect_spot(FakeAk(), rows, errors, retries=1, sleep_seconds=0)
    metrics = {row["metric"]: row for row in rows}
    assert metrics["上涨家数"]["value"] == 1
    assert metrics["下跌家数"]["value"] == 1
    assert metrics["平盘家数"]["value"] == 1
    assert metrics["全A行情降级状态"]["value"] == "已使用新浪备用源"
    assert metrics["上涨家数"]["source"] == "sina:stock_zh_a_spot"


if __name__ == "__main__":
    test_spot_collection_falls_back_to_sina()
