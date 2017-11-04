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

#import text file of Consumer Staple companies
#This will be an input from web scraping DF in Michelle's web scrape code
rdd = pd.read_excel('/Users/z013nx1/Downloads/Project/proj15aoutputCS.xlsx') #import text file with pipe delimiter
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
    if df.ix[i, 'Report Type']=='10-K':

        if df.ix[i, 'Ticker']=='PEP':

            if df.ix[i, 'Report Date'] IN ['2/15/17', '2/11/16', '2/12/15'] :
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-2]
                RFText.append(rf)
                print('Pepsi', i)

            else:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('Pepsi Before 2014', i)


        elif df.ix[i, 'Ticker']=='PM':
            start = 'unresolved staff comments'
            end = 'the following risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('PM', i)

        elif df.ix[i, 'Ticker']=='PG':

            if df.ix[i, 'Report Date'] IN ['8/8/14', '8/8/13', '8/8/12', '8/10/11', '8/13/10', '8/14/09']:

                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[0].split(end)[-1]
                RFText.append(rf)
                print('PG 2014, 13, 12, 11, 10, 09', i)

            else:

                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('PG', i)

        elif df.ix[i, 'Ticker']=='SSY':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('SSY', i)

        elif df.ix[i, 'Ticker']=='TSN':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('TSN', i)

        elif df.ix[i, 'Ticker']=='EL':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('EL', i)

        elif df.ix[i, 'Ticker']=='GIS':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('GIS', i)

        elif df.ix[i, 'Ticker']=='HSY':

            if df.ix[i, 'Report Date'] =='2017-02-21':
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('HSY 2017', i)

            else:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[0].split(end)[-1]
                RFText.append(rf)
                print('HSY', i)

        elif df.ix[i, 'Ticker']=='HRL':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('HRL', i)

        elif df.ix[i, 'Ticker']=='SJM':
            if df.ix[i, 'Report Date'] IN ['2011-06-28', '2010-06-24', '2008-06-27']:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('SJM 2011', i)
            else:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[0].split(end)[-1]
                RFText.append(rf)
                print('SJM', i)

        elif df.ix[i, 'Ticker']=='K':
            if df.ix[i, 'Report Date'] IN ['2009-02-24','2008-02-25']:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('K', i)
            else:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[0].split(end)[-1]
                RFText.append(rf)
                print('K', i)

        elif df.ix[i, 'Ticker']=='KMB':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('KMB', i)

        elif df.ix[i, 'Ticker']=='KHC':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('KHC', i)

        elif df.ix[i, 'Ticker']=='KR':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[0].split(end)[-1]
            RFText.append(rf)
            print('KR', i)

        elif df.ix[i, 'Ticker']=='MKC':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[0].split(end)[-1]
            RFText.append(rf)
            print('MKC', i)

        elif df.ix[i, 'Ticker']=='TAP':

            if df.ix[i, 'Report Date'] IN ['2011-02-22', '2010-02-19']:
                start = 'unresolved sec staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('TAP', i)

            else:
                start = 'unresolved staff comments'
                end = 'risk factors'
                s = df.ix[i, 'Soup']
                rf = (s.split(start))[1].split(end)[-1]
                RFText.append(rf)
                print('TAP', i)

        elif df.ix[i, 'Ticker']=='MDLZ':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('MDLZ', i)

        elif df.ix[i, 'Ticker']=='MNST':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('MNST', i)

        elif df.ix[i, 'Ticker']=='WMT':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[0].split(end)[-1]
            RFText.append(rf)
            print('WMT', i)

        elif df.ix[i, 'Ticker']=='WBA':

            start = 'unresolved staff comments'
            end = 'risk factors'
            s = df.ix[i, 'Soup']
            rf = (s.split(start))[1].split(end)[-1]
            RFText.append(rf)
            print('WBA', i)

    elif df.ix[i, 'Report Type']=='10-Q':

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
            elif:
                rf = (s.split(end))[-1]
                RFText.append(rf)
                print('RF no unreg', i)
        else:
            RFText.append('NO RISK FACTORS')
            print('NO RISK FACTORS', i)

df['RiskFactorText'] = RFText #create new column from risk factors
