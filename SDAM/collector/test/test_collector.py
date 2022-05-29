import os
import sys
import yaml
import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTOR_DIR = os.path.dirname(TEST_DIR)
ROOT_DIR = os.path.dirname(COLLECTOR_DIR)


sys.path.append(ROOT_DIR)
from collector import DART, MarketValueCollector


@pytest.fixture(scope="module")
def config():
    with open(os.path.join(ROOT_DIR, "config.yaml")) as f:
        _config = yaml.safe_load(f)
    yield _config


@pytest.fixture(scope="module")
def dart_collector(config):
    dart = DART(config)
    yield dart


@pytest.mark.parametrize(
    "corp_names, expecteds",
    [
        pytest.param("삼성전자", "00126380", id="Samsung_electrics"),
        pytest.param("고려아연", "00102858", id="Korea Zinc"),
    ],
)
def test_search_corp_code(dart_collector, corp_names, expecteds):
    assert expecteds == dart_collector.cope_code_map[corp_names]["dart_code"]


@pytest.mark.parametrize(
    "corp_name, year, quarter, doctype, account_name, expected",
    [
        pytest.param("삼성전자", 2019, 1, "CFS", "유동자산", 177388524000000),
        pytest.param("한국ANKOR유전", 2020, 1, "CFS", "유동자산", 237832),
    ],
)
def test_get_asset(
    dart_collector, corp_name, year, quarter, doctype, account_name, expected
):
    dart_collector.set_finance_sheet_from_dart(corp_name, year, quarter, doctype)
    assert expected == dart_collector.get_asset(account_name)


def test_get_issued_stocks(dart_collector):
    result = dart_collector.get_issued_stocks(
        "00102858",
        2022,
        1,
    )
    assert 18870000 == result


@pytest.mark.parametrize(
    "stock_code, attr, expected",
    [pytest.param("010130", "n_stocks", 18870000, id="KoreaZinc_N_stock")],
)
def test_get_market_value(stock_code, attr, expected):
    mvc = MarketValueCollector(stock_code)
    assert expected == mvc.get_market_value(attr)
