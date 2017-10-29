# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 20:26:11 2017

@author: z013nx1
"""


import pandas as pd
from __future__ import division, print_function
import requests  # functions for interacting with web pages
from lxml import html  # functions for parsing HTML
from bs4 import BeautifulSoup  # DOM html manipulation
import os
import pandas as pd
import xlrd
from contextlib import closing
from pyparsing import (makeHTMLTags, SkipTo, commonHTMLEntity, replaceHTMLEntity, 
    htmlComment, anyOpenTag, anyCloseTag, LineEnd, OneOrMore, replaceWith)
from pyparsing import ParserElement

#import text file of 10 companies from 2017-06-30 report date and 2016-06-30 report date
rdd = pd.read_excel('/Users/z013nx1/Downloads/webScrapeURL.xlsx') #import text file with pipe delimiter
df = pd.DataFrame(rdd) #convert to pandas df


scriptOpen,scriptClose = makeHTMLTags("script")
scriptBody = scriptOpen + SkipTo(scriptClose) + scriptClose
commonHTMLEntity.setParseAction(replaceHTMLEntity)

allsoup = []
for i in range(len(df)):
    r = requests.get(df.ix[i,'Report URL'])
    soup = BeautifulSoup(r.text, "lxml")
    targetHTML = str(soup)
    firstPass = (htmlComment | scriptBody | commonHTMLEntity | 
             anyOpenTag | anyCloseTag ).suppress().transformString(targetHTML)
    repeatedNewlines = LineEnd() + OneOrMore(LineEnd())
    repeatedNewlines.setParseAction(replaceWith("\n\n"))
    secondPass = repeatedNewlines.transformString(firstPass)
    allsoup.append(str(secondPass))

df.ix[2, 'Report URL']        
df['Soup'] = allsoup

df['RiskFactors'] = df['Soup'].str.contains('ITEM 1A.RISK FACTORS', regex=True)

RFText = []
        
for i in range(len(df)):
    if df.ix[i, 'RiskFactors']==True:
        start = 'ITEM 1A.RISK FACTORS'
        end = 'ITEM 2.'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[1].split(end)[0]
        RFText.append(rf)
    else:
        start = 'Cautionary Statements'
        end = 'Item 4.'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[1].split(end)[0]
        RFText.append(rf)
  
df['RiskFactorText'] = RFText
