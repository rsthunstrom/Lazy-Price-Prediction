# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 14:52:53 2017

@author: z013nx1
"""

from __future__ import division, print_function
import pandas as pd
from datetime import timedelta
import re, math
from collections import Counter
import numpy as np
from __future__ import division, print_function
import pandas as pd
import requests  # functions for interacting with web pages
from bs4 import BeautifulSoup  # DOM html manipulation
from pyparsing import (makeHTMLTags, SkipTo, commonHTMLEntity, replaceHTMLEntity, 
    htmlComment, anyOpenTag, anyCloseTag, LineEnd, OneOrMore, replaceWith)
from pyparsing import ParserElement

#Consumer Staple only dataset
#proj15aoutput4CS
rdd = pd.read_excel('/Users/z013nx1/Documents/proj15aoutputCS.xlsx') #import text file with pipe delimiter
df_init = pd.DataFrame(rdd) #convert to pandas df


df_init['File Date'] = pd.to_datetime(df_init['File Date']) #convert date to timedate

start_time = df_init['File Date'].max() #2017-11-01

#create a file for each month for the last 10 years
for i in range(-4, -8, -4):

    start_date = df_init['File Date'].max() + timedelta(weeks = i) #beginning current month
    end_date = df_init['File Date'].max() + timedelta(weeks = i +4) # ending current month
    ly_start = df_init['File Date'].max() + timedelta(weeks = i - 56) #beginning ly month
    ly_end = df_init['File Date'].max() + timedelta(weeks = i - 44) #ending ly month
    
    df_current = df_init[(df_init['File Date'] < end_date) & (df_init['File Date'] >= start_date)]
    df_ly = df_init[(df_init['File Date'] < ly_end) & (df_init['File Date'] >= ly_start)]
    
    df_current['Current'] = 1 #assign categorical flag to identify which last year to keep
    df_ly['Current'] = 0 #assign categorical flag to identify which last year to keep
    
    df_current_ticks = df_current['Ticker'] #get current tickers to analysis
    df_ly_keep = df_ly[df_ly['Ticker'].isin(df_current_ticks)] #only keep last year stocks in current
    frames = [df_current, df_ly_keep] #DFs to join
    df_join = pd.concat(frames) #Set current and LY DFs
    df = df_join.reset_index() #reset index for processing
    
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
    
    df['Soup'] = allsoup    
    
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
                if df.ix[i, 'Report Date'] in ('2017-02-15 00:00:00', '2016-02-11 00:00:00', '2015-02-12 00:00:00'):
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
                if df.ix[i, 'Report Date'] in ('2014-08-08 00:00:00', '2013-08-08 00:00:00', '2012-08-08 00:00:00', '2011-08-10 00:00:00', '2010-08-13 00:00:00', '2009-08-14 00:00:00'):
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
                if df.ix[i, 'Report Date'] in ('2011-06-28 00:00:00','2010-06-24 00:00:00', '2010-06-24 00:00:00', '2008-06-27 00:00:00'):
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
                if df.ix[i, 'Report Date'] in ('2009-02-24 00:00:00', '2008-02-25 00:00:00'):
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
                if df.ix[i, 'Report Date'] in ('2011-02-22 00:00:00', '2010-02-19 00:00:00'):
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
                start = 'unregistered sales of equity'
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
                print('NO RISK FACTORS', i)
    
    df['RiskFactorText'] = RFText #create new column from risk factors

    
    ##################
    ##################
    ##################
    # IMPORT TEXT FILE
    ##################
    ##################
    ##################
    
    
    df_sort = df.sort_values(['Ticker', 'File Date']) #sort by ticker and year
    
    df_sort['text_list'] = df_sort.groupby(('Ticker', 'File Date'))['RiskFactorText'].apply(lambda x: list(x)).tolist() #create list from text
    
    df_new = df_sort.reset_index(drop = 'index') #reset index after sort
    
    ##################################
    ##################################
    ##################################
    # FUNCTIONS FOR SIMILARITY METRICS
    ##################################
    ##################################
    ##################################
    
    
    WORD = re.compile(r'\w+')
    
    # Cosine similarity function
    def get_cosine(vec1, vec2):
         intersection = set(vec1.keys()) & set(vec2.keys())
         numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
         sum1 = sum([vec1[x]**2 for x in vec1.keys()])
         sum2 = sum([vec2[x]**2 for x in vec2.keys()])
         denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
         if not denominator:
            return 0.0
         else:
            return float(numerator) / denominator
    
    # Jaccard Similarity Function
    def get_jaccard(vec1, vec2):
        return float(len(vec1.intersection(vec2))*1.0/len(vec1.union(vec2)))
    
    def get_simple(vec1, vec2):
        return float(len(vec1.intersection(vec2))*1.0 / len(vec1))
    
    # Word Vector Format needed for cosine similarity (ie words with counts)
    def text_to_vector(text):
         words = WORD.findall(text)
         return Counter(words)
    
    # Word Vector Format needed for jaccard similarity (vector of words)
    def text_to_vector_js(text):
         words = WORD.findall(text)
         return words
    
    def text_to_vector_simple(text):
         words = WORD.findall(text)
         return words
    
    # function to calculate cosine similarity when two quarters are passed
    def calc_cosine(quarterCurrent, quarterOld):
        text1 = quarterCurrent
        text2 = quarterOld
        vector1 = text_to_vector(text1)
        vector2 = text_to_vector(text2)
        cosine = get_cosine(vector1, vector2)
        return cosine
    
    # function to calculate jaccard similarity when two quarters are passed
    def calc_jaccard(quarterCurrent, quarterOld):
        textjs1 = quarterCurrent
        textjs2 = quarterOld
        vectorjs1 = set(text_to_vector_js(textjs1))
        vectorjs2 = set(text_to_vector_js(textjs2))
        jaccard = get_jaccard(vectorjs1, vectorjs2)
        return jaccard
    
    # function to calculate simple similarity when two quarters are passed
    def calc_simple(quarterCurrent, quarterOld):
        textsimple1 = quarterCurrent
        textsimple2 = quarterOld
        vectorsimple1 = set(text_to_vector_simple(textsimple1))
        vectorsimple2 = set(text_to_vector_simple(textsimple2))
        simple = get_simple(vectorsimple1, vectorsimple2)
        return simple
    
    ################################
    ################################
    ################################
    # SIMILARITY METRIC CALCULATIONS
    ################################
    ################################
    ################################
    
    #empty list for similarity metrics
    cos_sim = []
    jac_sim = []
    simple_sim = []
    duplicate = []
    
    #loop through each row and calculate similarity measures if the tickers are the same
    #assign a duplicate if the two quarters have already been analyzed so we can exclude later
    for i in range(len(df_new)-1):
        if df_new.ix[i, 'Ticker'] == df_new.ix[i+1, 'Ticker']:
            cos_value = calc_cosine(df_new.ix[i, 'text_list'][0], df_new.ix[i+1, 'text_list'][0])
            cos_sim.append(cos_value)
            j_value = calc_jaccard(df_new.ix[i, 'text_list'][0], df_new.ix[i+1, 'text_list'][0])
            jac_sim.append(j_value)
            simple_value = calc_simple(df_new.ix[i, 'text_list'][0], df_new.ix[i+1, 'text_list'][0])
            simple_sim.append(simple_value)
            duplicate.append(0)
        else:
            cos_sim.append(0)
            jac_sim.append(0)
            simple_sim.append(0)
            duplicate.append(1)
    
    # append a 0 for the last row in the file, which by default is a duplicate
    cos_sim.append(0)
    jac_sim.append(0)
    simple_sim.append(0)
    duplicate.append(1)
    
    # append similarity lists as a column in dataframe
    df_new['cosine_similarity'] = cos_sim
    df_new['jaccard_similarity'] = jac_sim
    df_new['simple_similarity'] = simple_sim
    df_new['duplicate'] = duplicate
    
    df_final = df_new[df_new['duplicate'] != 1] #remove any rows which are the duplicate for each ticker
    
    #######################
    #######################
    #######################
    # QUINTILE CALCULATIONS
    #######################
    #######################
    #######################
    
    # cosine similarity quintile values
    # quantile set to 0.20 for quintile
    cos_quintile1 = df_final['cosine_similarity'].quantile(0.2)
    cos_quintile2 = df_final['cosine_similarity'].quantile(0.4)
    cos_quintile3 = df_final['cosine_similarity'].quantile(0.6)
    cos_quintile4 = df_final['cosine_similarity'].quantile(0.8)
    
    # function for determining quintile
    def cos_quintile_rank (row):
        if row['cosine_similarity'] <= cos_quintile1:
            return 1
        if row['cosine_similarity'] <= cos_quintile2:
            return 2
        if row['cosine_similarity'] <= cos_quintile3:
            return 3
        if row['cosine_similarity'] <= cos_quintile4:
            return 4
        if row['cosine_similarity'] > cos_quintile4:
            return 5
    
    # apply quintile based on each rows value
    df_final['cosine_quintile'] = df_final.apply(lambda row: cos_quintile_rank(row), axis = 1)
    
    # jacaard similarity quintile values
    # quantile set to 0.20 for quintile
    jac_quintile1 = df_final['jaccard_similarity'].quantile(0.2)
    jac_quintile2 = df_final['jaccard_similarity'].quantile(0.4)
    jac_quintile3 = df_final['jaccard_similarity'].quantile(0.6)
    jac_quintile4 = df_final['jaccard_similarity'].quantile(0.8)
    
    # function for determining quintile
    def jac_quintile_rank (row):
        if row['jaccard_similarity'] <= jac_quintile1:
            return 1
        if row['jaccard_similarity'] <= jac_quintile2:
            return 2
        if row['jaccard_similarity'] <= jac_quintile3:
            return 3
        if row['jaccard_similarity'] <= jac_quintile4:
            return 4
        if row['jaccard_similarity'] > jac_quintile4:
            return 5
    
    # apply quintile based on each rows value
    df_final['jaccard_quintile'] = df_final.apply(lambda row: jac_quintile_rank(row), axis = 1)
    
    # simple similarity quintile values
    # quantile set to 0.20 for quintile
    simple_quintile1 = df_final['simple_similarity'].quantile(0.2)
    simple_quintile2 = df_final['simple_similarity'].quantile(0.4)
    simple_quintile3 = df_final['simple_similarity'].quantile(0.6)
    simple_quintile4 = df_final['simple_similarity'].quantile(0.8)
    
    # function for determining quintile
    def simple_quintile_rank (row):
        if row['simple_similarity'] <= simple_quintile1:
            return 1
        if row['simple_similarity'] <= simple_quintile2:
            return 2
        if row['simple_similarity'] <= simple_quintile3:
            return 3
        if row['simple_similarity'] <= simple_quintile4:
            return 4
        if row['simple_similarity'] > simple_quintile4:
            return 5
    
    # apply quintile based on each rows value
    df_final['simple_quintile'] = df_final.apply(lambda row: simple_quintile_rank(row), axis = 1)
    
    df_final.drop(['duplicate'], axis = 1) #final DF, dropping duplicate column which is no longer needed
    
    #############
    #############
    #############
    # FILE EXPORT
    #############
    #############
    #############
    
    df_clean = df_final.drop(['Soup', 'Current', 'RiskFactors', 'unregistered', 'Cautionary1', \
    'Cautionary2', 'Cautionary3', 'Cautionary4', 'RiskFactorText', 'text_list'], axis = 1)
    df_clean.to_csv('/Users/z013nx1/Documents/November2017.txt', sep = ",") # export to text
