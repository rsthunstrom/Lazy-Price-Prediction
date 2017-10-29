# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 20:26:11 2017

@author: z013nx1
"""

from __future__ import division, print_function
import pandas as pd
import requests  # functions for interacting with web pages
from bs4 import BeautifulSoup  # DOM html manipulation
import pandas as pd
from pyparsing import (makeHTMLTags, SkipTo, commonHTMLEntity, replaceHTMLEntity, 
    htmlComment, anyOpenTag, anyCloseTag, LineEnd, OneOrMore, replaceWith)
from pyparsing import ParserElement

#import text file of 10 companies from 2017-06-30 report date and 2016-06-30 report date
#This will be an input from web scraping DF in Michelle's web scrape code

rdd = pd.read_excel('/Users/z013nx1/Downloads/webScrapeURL.xlsx') #import text file with pipe delimiter
df = pd.DataFrame(rdd) #convert to pandas df


#URL Functions to determie tags
scriptOpen,scriptClose = makeHTMLTags("script")
scriptBody = scriptOpen + SkipTo(scriptClose) + scriptClose
commonHTMLEntity.setParseAction(replaceHTMLEntity)

allsoup = [] #empty list for soup ie the html data

for i in range(len(df)):
    r = requests.get(df.ix[i,'Report URL']) #request from URL
    soup = BeautifulSoup(r.text, "lxml") #convert to soup
    targetHTML = str(soup) #convert to strin
    firstPass = (htmlComment | scriptBody | commonHTMLEntity | 
             anyOpenTag | anyCloseTag ).suppress().transformString(targetHTML) #remove HTML tags
    repeatedNewlines = LineEnd() + OneOrMore(LineEnd())
    repeatedNewlines.setParseAction(replaceWith("\n\n"))
    secondPass = repeatedNewlines.transformString(firstPass) #remove additional HTML tags
    allsoup.append(str(secondPass))
    
df['Soup'] = allsoup #create new column from scraped and cleaned HTML data

#create boolean for Risk Factors
#need to determine which keywords we will use to parse the file
df['RiskFactors'] = df['Soup'].str.contains('ITEM 1A.RISK FACTORS', regex=True) 

RFText = [] #empty list for risk factors after they are parsed
        
#determine if risk factors are included in the file
#then parse the file to extract only the risk factors section
#start split determines when to start collecting text
#end split determines when to stop collecting text
#we collect after the start with [1] and before the end with [0]

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
  
df['RiskFactorText'] = RFText #create new column from risk factors
