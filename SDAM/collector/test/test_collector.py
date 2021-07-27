import os
import sys
import yaml
import pytest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
COLLECTOR_DIR = os.path.dirname(TEST_DIR)
ROOT_DIR = os.path.dirname(COLLECTOR_DIR)


sys.path.append(ROOT_DIR)
from collector import DART, MarketValueCollector

@pytest.fixture(scope='module')
def config():
    with open(os.path.join(ROOT_DIR, 'config.yaml')) as f:
        _config = yaml.safe_load(f)
    yield _config


@pytest.fixture(scope='module')
def dart_collector(config):
    key = "b34dba1d3305ded5cf8022dab7ac5fe90c867e8b"
    dart = DART(config)
    yield dart


@pytest.mark.parametrize(
    'corp_names, expecteds',
    [pytest.param('삼성전자', '00126380', id='Samsung_electrics'),
     pytest.param('고려아연', '00102858', id='Korea Zinc')
    ]
    )
def test_search_corp_code(dart_collector, corp_names, expecteds):
    assert expecteds == dart_collector.search_corp_code(corp_names)


@pytest.mark.parametrize(
    "corp_name, year, quarter, doctype",
    [pytest.param("삼성전자", 2019, 1, "CFS")]
)
def test_get_finantial_sheet(dart_collector, corp_name, year, quarter, doctype):
    with open(os.path.join(TEST_DIR, 'data/samsung_2019_1Q.txt')) as f:
        expected = f.readlines()
    assert expected == dart_collector.get_finance_sheet_from_dart(corp_name, year, quarter, doctype)


@pytest.mark.parametrize(
    "stock_code"
)
def test_mvc(stock_code):
    MarketValueCollector(stock_code)