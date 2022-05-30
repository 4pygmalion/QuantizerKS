### how to install
```bash 
$ python -m pip install build
$ python setup.py
```

### How to use ?
```Python 3
import yaml
from SDAM import set_key, set_save_dir

set_key('YOUR_CERTKEY')
set_save_dir('SAVE_DIR')

with open('SDAM/config.yaml')) as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

dart_collector = DART(config)
dart_collector.get_finance_sheet_from_dart("삼성전자", 2021, 1, doctype="CFS")
current_asset = dart_collector.get_asset('유동자산')
total_liab = dart_collector.get_asset('부채총계')
print("Current asset:", current_asset)
print("total_liab:", total_liab)
```


### REQUIREMENT
- python3.9
- yaml
- pandas
- numpy
- beautifulsoap4
- xmltodict 
- requests 
