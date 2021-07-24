import os
import sys
import json
import numpy as np
import pandas as np

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

    def __init__(self, config):
        self.config = config
        self.cert_key = config['DART']['KEY']


    def _URL_to_json(self, URL):
        pass

    def get_finance_sheet(self, year:int, report_code:int, doctype :str ='CFS'):
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
        # Requested parameters
        cert = 'crtfc_key={}'.format(self.cert_key)
        corp_code = 'corp_code={}'.format(self.corp_name)
        bsns_year = 'bsns_year={}'.format(str(year))
        report_code = 'reprt_code={}'.format(report_code)
        fs_div = 'fs_div={}'.format(doctype)


        # URL Type
        if doctype == 'CFS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?"
            param = [cert, corp_code, bsns_year, report_code, fs_div]
            target_URL = URL + '&'.join(param)
            sheet = self._URL_to_json(target_URL)

        elif doctype == 'IS':
            URL = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?"
            param = [cert, corp_code, bsns_year, report_code]
            target_URL = URL + '&'.join(param)
            sheet = self._URL_to_json(target_URL)

        return sheet