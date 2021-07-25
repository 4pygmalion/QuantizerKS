import os
import sys
import yaml

import pandas as pd
import time

STRATEGY_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(STRATEGY_DIR)
sys.path.append(ROOT_DIR)

from SDAM.collector import DART, MarketValueCollector
from SDAM import set_key, set_save_dir

if __name__ == "__main__":
    
    # Set your current environment
    set_key('b34dba1d3305ded5cf8022dab7ac5fe90c867e8b')
    set_save_dir('/Users/hoheon/Documents/repositories/SDAM/strategies/results')
    with open(os.path.join(ROOT_DIR, 'SDAM/config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # DART
    dart_collector = DART(config)
    enlisting_corps = dart_collector.get_listed_corp()

    # NET Asset (=유동자산 - 부채총계)
    rows = []
    for idx, (corp_name, corp_code) in enumerate(enlisting_corps.items()):
        if idx >= 30:
            break
        print(idx, corp_name)
        dart_collector.get_finance_sheet_from_dart(corp_name, 2021, 1, doctype="CFS")
        current_asset = dart_collector.get_asset('유동자산')
        total_liab = dart_collector.get_asset('부채총계')
    
        mvc = MarketValueCollector(enlisting_corps[corp_name])
        market_value = mvc.get_market_value('market_value')

        row = [corp_name, corp_code, current_asset, total_liab, market_value]
        rows.append(row)



    # Save data
    colnames = ['CorpName', 'Code', 'CurrnetAsset', 'TotalLiab', 'MarketValue']
    data = pd.DataFrame(rows, columns=colnames)
    data.to_csv(os.path.join(config['ENV']['SAVE_DIR']), 'ncav.csv', index=False)