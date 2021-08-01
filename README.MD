### REQUIREMENT
- python3.9
- yaml
- pandas
- numpy
- beautifulsoap4
- xmltodict 


### how to install
`bash 
<p> $ python -m pip install build </p>
<p> $ python setup.py </p>
`

### How to use ?
```
import yaml
from SDAM import set_key, set_save_dir
In [ ]:
set_key('YOUR_CERTKEY')
set_save_dir('SAVE_DIR')

```


<p> dart = DART(config) </p>
<p>dart.get_finance_sheet_from_dart("삼성전자", 2019, 1)</p>
<p>dart.get_asset('유동자산'))</p>
`
