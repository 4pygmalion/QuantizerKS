# NCAV(Net Current Asset Value)

import os
import sys
import yaml
import pandas as pd

STRATEGY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(STRATEGY_DIR)
LOG_DIR = os.path.join(ROOT_DIR, "log")
SAVE_DIR = os.path.join(ROOT_DIR, "results")
sys.path.append(ROOT_DIR)

from SDAM.collector import DART, MarketValueCollector
from SDAM import set_key, set_save_dir
from utils import get_logger

if __name__ == "__main__":
    COMMIT_BATCH = 100

    # Set your current environment
    set_key("125494f0d66cc9a1352fe47a74f8c78d4f2ed294")
    set_save_dir(SAVE_DIR)
    with open(os.path.join(ROOT_DIR, "SDAM/config.yaml")) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # DART
    logger = get_logger(name="NCAV", file_path=os.path.join(LOG_DIR, "NCAV.txt"))
    dart_collector = DART(config, logger=logger)
    enlisting_corps = dart_collector.get_listed_corp()

    # NET Asset (=유동자산 - 부채총계)
    rows = []
    for idx, (corp_name, corp_codes) in enumerate(enlisting_corps.items()):
        dart_code, stock_code = corp_codes.values()

        error_msg = dart_collector.get_finance_sheet_from_dart(
            corp_name, 2021, 1, doctype="CFS"
        )
        if error_msg:
            continue

        current_asset = dart_collector.get_asset("유동자산")
        total_liab = dart_collector.get_asset("부채총계")

        mvc = MarketValueCollector(stock_code)
        market_value = mvc.get_market_value("market_value")

        row = [corp_name, stock_code, dart_code, current_asset, total_liab, market_value]
        rows.append(row)

        if idx % COMMIT_BATCH == 0:

            # Save data
            colnames = [
                "CorpName",
                "StockCode",
                "DartCode",
                "CurrnetAsset",
                "TotalLiab",
                "MarketValue",
            ]
            data = pd.DataFrame(rows, columns=colnames)

            data["NetAsset"] = data["CurrnetAsset"] - data["TotalLiab"]
            data["NetAsset/MarketValue"] = data["NetAsset"] / data["MarketValue"]
            file_name = os.path.join(config["ENV"]["SAVE_DIR"], "ncav.csv")
            data.to_csv(file_name, index=False)
