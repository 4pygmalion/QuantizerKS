import os
import sys
import json
import xmltodict
import numpy as np
import pandas as np

from io import BytesIO
from zipfile import ZipFile
from bs4 import BeautifulSoup
from urllib.request import urlopen


COLLECTOR_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(COLLECTOR_DIR)

sys.path.append(ROOT_DIR)
from error_handler import AccountNotFound

class DART(object):
    '''
    The purpose of this class is to retrieve the financial information from DART
    (http://dart.fss.or.kr/)

    Parameters
    ----------
    cert_key: cert key (https://opendart.fss.or.kr/intro/main.do)
    corp_code : unique key in Open Dart (is not differ in stock code) **
    is_consolidation: 연결 또는 별도 재무재표 여부
        (default: True (연결))

    Example
    -------
    >>> CRTFC_KEY="7gidszaxcd9qyh4idjosaidj"
    >>> corp_code="00126380"

    >>> corp_dart = DART(CRTFC_KEY, corp_code)
    >>> corp_dart.get_finance_sheet(start_date=2020, report_code=11013)
    '''

    def __init__(self, config, is_consolidation = True):
        
        self.config = config
        self.mapper = config['DART']['MAPPER']
        self.cert = f"crtfc_key={config['DART']['KEY']}"
        self.cope_code_map = self._get_corpcode()   
        self.is_consolidation = is_consolidation


    def _get_corpcode(self) -> list:
        ''' Get XML file from DART API and parse it

        Return
        ------

        list: including
            OrderedDict(['corp_code', '0043728'],
                        ['corp_name', '다코])
        '''

        request_url = "https://opendart.fss.or.kr/api/corpCode.xml?"+self.cert
        xml_zip = urlopen(request_url).read()
        zip_file = ZipFile(BytesIO(xml_zip))
        file = zip_file.namelist()[0]
    
        with zip_file.open(file) as corpcode_xml:
            corp_xml =  xmltodict.parse(corpcode_xml.read())
        return corp_xml['result']['list']
    

    def search_corp_code(self, corp_name:str) -> str:
        for element in self.cope_code_map:
            if element['corp_name'] == corp_name:
                return element['corp_code']


    def get_finance_sheet_from_dart(self, 
    corp_name:str, 
    year:int, 
    quarter:int, 
    doctype :str ='CFS') -> list:
        '''
        Parameters
        ----------
        year: 회계년도.

        report_code: int. in range from 1, to 4

        doctype: str.
            'CFS':  연결
            'IS' 손익계산서
            'IS: Income statetment
            defualt: CFS (연결재무재표)


        Return
        ------
        list: 
            0 index: header
            


        '''


        corp_code = self.search_corp_code(corp_name)
        
        # Requested parameters
        corp_code = 'corp_code={}'.format(corp_code)
        bsns_year = 'bsns_year={}'.format(str(year))
        report_code = 'reprt_code={}'.format(self.mapper[quarter])
        fs_div = 'fs_div={}'.format(doctype)


        # URL Type
        if doctype == 'CFS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"
            param = [self.cert, corp_code, bsns_year, report_code, fs_div]
        elif doctype == 'IS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?"
            param = [self.cert, corp_code, bsns_year, report_code]

        target_URL = URL + '&'.join(param)

        binary_txt = urlopen(target_URL).read()
        self.account_sets =  json.loads(binary_txt)['list']  # list including dictionary
        

    def get_asset(self, asset_name):
        '''
        계정명칭(예, 유동자산, 유동부채 등)에 해당하는 당기 금액을 반환합니다.

        Parameter
        ---------
        asset_name: str. 계정명칭
            예) "유동자산"

        Return
        ------
        int: 계정명칭의 보고서내 당기금액
        '''
        # for each account name (각 계정명에 대해서 자산을 찾음)
        for item in self.account_sets:
            if asset_name == item['account_nm'] :
                return item['thstrm_amount']
        
        raise AccountNotFound(f"{asset_name} was not founded in finantial sheet")



# if __name__ == "__main__":
#     import os
#     import sys
#     import yaml

#     COLLECTOR_DIR = os.path.dirname(os.getcwd())
#     COLLECTOR_DIR = os.path.dirname(os.path.abspath(__file__))

#     ROOT_DIR = os.path.dirname(COLLECTOR_DIR)
    
#     with open('/Users/hoheon/Documents/repositories/SDAM/SDAM/config.yaml') as f:
#     # with open(os.path.join(ROOT_DIR, 'config.yaml')) as f:
#         config = yaml.load(f, Loader=yaml.FullLoader)

#     dart = DART(config)
#     dart.get_finance_sheet_from_dart("삼성전자", 2019, 1)
#     print("유동자산", dart.get_asset('유동자산'))
#     print("아이스크림", dart.get_asset('김우유'))
 