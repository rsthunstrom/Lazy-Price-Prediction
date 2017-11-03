# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 20:26:11 2017

@author: z013nx1
"""

from __future__ import division, print_function
import pandas as pd
import requests  # functions for interacting with web pages
from bs4 import BeautifulSoup  # DOM html manipulation
from pyparsing import (makeHTMLTags, SkipTo, commonHTMLEntity, replaceHTMLEntity, 
    htmlComment, anyOpenTag, anyCloseTag, LineEnd, OneOrMore, replaceWith)
from pyparsing import ParserElement

#import text file of 10 companies from 2017-06-30 report date and 2016-06-30 report date
#This will be an input from web scraping DF in Michelle's web scrape code
#proj15output4
rdd = pd.read_excel('/Users/z013nx1/Downloads/Project/proj15aoutput4.xlsx') #import text file with pipe delimiter
#rdd = pd.read_excel('/Users/z013nx1/Downloads/webScrapeURL.xlsx') #import text file with pipe delimiter
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
    allsoup.append(str(secondPass.lower()))
    
df['Soup'] = allsoup #create new column from scraped and cleaned HTML data

#create boolean for Risk Factors
#need to determine which keywords we will use to parse the file
df['RiskFactors'] = df['Soup'].str.contains('risk factors', regex=True)

df['unregistered'] = df['Soup'].str.contains('unregistered sales of equity', regex=True)

df['Cautionary1'] = df['Soup'].str.contains('statements about Kroger', regex=True)

df['Cautionary2'] = df['Soup'].str.contains('forward-looking information', regex=True)

df['Cautionary3'] = df['Soup'].str.contains('forward-looking statements', regex=True)

df['Cautionary4'] = df['Soup'].str.contains('cautionary statement', regex=True)

RFText = [] #empty list for risk factors after they are parsed
        
#determine if risk factors are included in the file
#then parse the file to extract only the risk factors section
#start split determines when to start collecting text
#end split determines when to stop collecting text
#we collect after the start with [1] and before the end with [0]

for i in range(len(df)):
        
    if df.ix[i, 'Cautionary1']==True:
        #Kroger
        start = 'item 3.'
        end = 'statements about Kroger'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[0].split(end)[-1]
        RFText.append(rf)
        print('caution3', i)
        
    elif df.ix[i, 'Cautionary2']==True:
        #estee lauder 
        start = 'item 3.'
        end = 'forward-looking information'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[1].split(end)[-1]
        RFText.append(rf)
        print('caution3', i)
        
    elif df.ix[i, 'Cautionary3']==True:
        #Kraft Heinz
        start = 'item 3.'
        end = 'forward-looking statements'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[1].split(end)[-1]
        RFText.append(rf)
        print('caution1', i)

    elif df.ix[i, 'Cautionary4']==True:
        #general mills
        start = 'item 3.'
        end = 'cautionary statement'
        s = df.ix[i, 'Soup']
        rf = (s.split(start))[1].split(end)[-1]
        RFText.append(rf)
        print('caution2', i)

    elif df.ix[i, 'RiskFactors']==True:
        start = 'unregistered sales of equity'
        end = 'risk factors'
        s = df.ix[i, 'Soup']
        
        if df.ix[i, 'unregistered'] == True:
            if len(s.split(start)) == 2:
                rf = (s.split(start))[0].split(end)[-1]
                RFText.append(rf)
                print('RF length one with unreg', i)
            else:
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('RF length many with unreg', i)
        else:
            rf = (s.split(end))[-1]
            RFText.append(rf)
            print('RF no unreg', i)  
    else:
        RFText.append('NO RISK FACTORS')
        
df['RiskFactorText'] = RFText #create new column from risk factors
