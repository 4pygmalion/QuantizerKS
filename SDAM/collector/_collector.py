import os
import sys
import json
import xmltodict
import numpy as np
import pandas as pd

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
        self.cope_code_map = self.get_listed_corp()   
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
    
    def get_listed_corp(self, market:list = ['KOSPI', 'KOSDAQ']) -> dict:
        ''' 상장된 기업의 기업명, 종목코드를 반환합니다.
        
        Return
        ------
        dict: (corp_name, corp_code).  
            corp_name, corp_code are string type.

        Note
        ----
        장외거래시장도 있는 것 같음
        '''
        
        data = pd.read_csv(os.path.join(COLLECTOR_DIR, 
                            self.config['DATA']['MARKET']),
                            encoding='cp949')
        # data['단축코드'] = 
        data = data.loc[data['시장구분'].isin(market)]
        data['단축코드'] = data['단축코드'].apply(lambda x: "{:06}".format((int(x))) \
                                            if sum([char.isalpha() for char in x]) == 0 \
                                            else str(x))
                    
        listing_corps = dict()
        for corp_info in self._get_corpcode():
            if not corp_info['stock_code']:
                continue
            if corp_info['stock_code'] in list(data['단축코드']):
                listing_corps[corp_info['corp_name']] = {'dart_code':corp_info['corp_code'],
                                                        'stock_code':corp_info['stock_code']}
        return listing_corps



    def get_finance_sheet_from_dart(self, 
    corp_name:str, 
    year:int, 
    quarter:int, 
    doctype :str ='CFS') -> list:
        '''
        Parameters
        ----------
        year: 회계년도.
        report_code: int. 
            in range from 1, to 4
        doctype: str.
            'CFS':  연결재무재표 (Consolidated Finantial Statement)
            'IS' 손익계산서 (Income statetment)

        Return
        ------
        None
        '''

        # Requested parameters
        corp_code = 'corp_code={}'.format(self.cope_code_map[corp_name]['dart_code'])
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
                return int(item['thstrm_amount'])
        
        raise AccountNotFound(f"{asset_name} was not founded in finantial sheet")



class MarketValueCollector(object):
    '''Market Value Data collecter from NAVER finance

    Parameters
    ----------
    corp_code: '014680'
    '''
    
    def __init__(self, corp_code:str):
        self.corp_code = corp_code
        self.bs_obj = self._get_html()
        
        if self._check_redirection():
            raise ValueError("Ticker not existed")
        
    def _check_redirection(self):
        '''To check rediction due to not existing ticker
        
        return
        ------
        bool
        '''
        return self.bs_obj.find('title').get_text() == '네이버 :: 세상의 모든 지식, 네이버'
        
    def _get_html(self):
        '''Get html from naver stock using BS4 '''

        URL = 'https://finance.naver.com/item/main.nhn?code={}'.format(self.corp_code)
        html = urlopen(URL)
        bs_obj = BeautifulSoup(html, "html.parser")      
        
        return bs_obj


    def get_market_value(self, attr:str) -> int:
        '''
        Parameters
        ----------
            attr: str.
                'price': 현재가격
                'n_stock': 발행주식수
                'market_value': 시가총액 
        '''
        if attr == 'price':
            market_sum = self.bs_obj.find('p', attrs={'class': 'no_today'})
            spans = market_sum.find_all('span')[1:]
            csv = [tag.get_text() for tag in spans]
            current_price = ''.join(csv)
            current_price = int(current_price.replace(',', ''))
            return current_price

        elif attr == 'n_stocks':
            print(self.bs_obj)
            q = self.bs_obj.find('th', text='상장주식수')
            # print(q)
            # print(q.next_sibling)
            #.next_sibling
            q = q.get_text()
            q = int(q.replace(',', ''))
            return q

        elif attr == 'market_value':
            n_sum = self.get_market_value('price') * self.get_market_value('n_stocks')
            return n_sum



if __name__ == "__main__":
    import os
    import sys
    import yaml
    import pandas as pd
    # COLLECTOR_DIR = os.path.dirname(os.getcwd())
    COLLECTOR_DIR = os.path.dirname(os.path.abspath(__file__))

    ROOT_DIR = os.path.dirname(COLLECTOR_DIR)
    
    with open('/Users/hoheon/Documents/repositories/SDAM/SDAM/config.yaml') as f:
    # with open(os.path.join(ROOT_DIR, 'config.yaml')) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    dart = DART(config)
    a = dart.get_listed_corp()

    print(a)
 