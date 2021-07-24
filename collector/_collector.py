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

class DART(object):
    '''
    The purpose of this class is to retrieve the financial information from DART
    (http://dart.fss.or.kr/)

    Parameters
    ----------
    cert_key: cert key (https://opendart.fss.or.kr/intro/main.do)
    corp_code : unique key in Open Dart (is not differ in stock code) **

    Example
    -------
    >>> CRTFC_KEY="7gidszaxcd9qyh4idjosaidj"
    >>> corp_code="00126380"

    >>> corp_dart = DART(CRTFC_KEY, corp_code)
    >>> corp_dart.get_finance_sheet(start_date=2020, report_code=11013)
    '''

    def __init__(self, key, config):
        self.config = config
        self.cert = f"crtfc_key={config['DART']['KEY']}"
        self.cope_code_map = self._get_corpcode()   

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


    def _URL_to_json(self, URL:str):
        req = urlopen(URL)
        result = req.read()
        return json.loads(result)


    def get_finance_sheet_from_dart(self, corp_name:str, year:int, report_code:int, doctype :str ='CFS'):
        '''
        Parameters
        ----------
        year: 회계년도.

        report_code: int
            1분기보고서 : 11013
            반기보고서 : 11012
            3분기보고서 : 11014
            사업보고서 : 11011

        doctype: str.
            'CFS':  Consolidate Financial sheet
            'IS: Income statetment
            defualt: CFS (연결재무재표)



        Return
        ------
        None


        '''
        corp_code = self.search_corp_code(corp_name)
        
        # Requested parameters
        corp_code = 'corp_code={}'.format(corp_code)
        bsns_year = 'bsns_year={}'.format(str(year))
        report_code = 'reprt_code={}'.format(report_code)
        fs_div = 'fs_div={}'.format(doctype)


        # URL Type
        if doctype == 'CFS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"
            param = [self.cert, corp_code, bsns_year, report_code, fs_div]
        elif doctype == 'IS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?"
            param = [self.cert, corp_code, bsns_year, report_code]

        target_URL = URL + '&'.join(param)
        return target_URL


# if __name__ == "__main__":
# import yaml
# with open('C:/Users/HoHeon/OneDrive/PythonProject/SDAM/config.yaml') as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)

# dart = DART(config)
# a = dart.cope_code_map
# # a = dart.get_finance_sheet_from_dart("11013", 2019, "11013")
# print(type(a))
# # print(a[0])

# for element in a['result']['list']:
#     if element['corp_name'] == '고려아연':
#         print(element)
# import sys
# sys.path.append('C:/Users/HoHeon/OneDrive/PythonProject/SDAM/collector')