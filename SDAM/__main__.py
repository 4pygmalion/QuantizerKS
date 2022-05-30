import os
import sys
import yaml
import argparse
import pandas as pd

SDAM_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SDAM_DIR)
LOG_DIR = os.path.join(ROOT_DIR, "log")
SAVE_DIR = os.path.join(ROOT_DIR, "results")
sys.path.append(ROOT_DIR)

from utils import get_logger
from SDAM.collector import DART, MarketValueCollector


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", type=str, required=True, help="DART API key")
    return parser.parse_args()


def load_config() -> dict:
    """DART OPEN API Key을 세팅하여 반환"""
    with open(os.path.join(SDAM_DIR, "config.yaml")) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    ARGS = get_args()
    CONFIG = load_config()
    CONFIG["DART"]["KEY"] = ARGS.key
    CONFIG["ENV"]["SAVE_DIR"] = SAVE_DIR
    os.makedirs(SAVE_DIR, exist_ok=True)

    LOGGER = get_logger("MAIN", file_path=os.path.join(LOG_DIR, "main.log"))
    DART_API = DART(CONFIG, logger=LOGGER)
    DART_API.set_stock_codes()

    rows = list()
    asset_names = {"유동자산", "유동부채", "비유동자산", "비유동부채"}
    for corp_name, corp_codes in DART_API.stock_codes.items():
        fs = DART_API.get_finance_sheet(corp_codes["dart_code"], 2022, 1)
        asset_info = DART_API.get_assets(fs, {"유동자산", "유동부채", "비유동자산", "비유동부채"})

        row = [asset_info.get(asset_name, 0) for asset_name in asset_names]
        rows.append(row)

    df = pd.DataFrame(rows, columns=list(asset_names))
    df.to_csv(os.path.join(SAVE_DIR, "dataframe.csv"), index=False)
    # print(df)
    # # for idx, corp_name, corp_code in enumerate(CORP_LIST.items()):
    #     dart_code, stock_code = corp_code.values()
    #     error_msg = DART_API.get_finance_sheet_from_dart(
    #         corp_name, 2022, 1, doctype="CFS"
    #     )
    #     if error_msg:
    #         continue

    #     current_asset = DART_API.get_asset("유동자산")
    #     non_current_asset = DART_API.get_asset("비유동자산")
    #     total_liab = DART_API.get_asset("부채총계")

    #     mvc = MarketValueCollector(stock_code)
    #     market_value = mvc.get_market_value("market_value")

    #     row = [
    #         corp_name,
    #         stock_code,
    #         dart_code,
    #         current_asset,
    #         total_liab,
    #         market_value,
    #     ]
