# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 10:24:20 2017

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

rdd = pd.read_excel('/Users/z013nx1/Documents/proj15aoutputCS.xlsx') #import text file with pipe delimiter
df_init = pd.DataFrame(rdd) #convert to pandas df
df_init['File Date'] = pd.to_datetime(df_init['File Date']) #convert date to timedate

tickers = df_init['Ticker'].drop_duplicates()
tickers2 = tickers.reset_index()
Master_File = tickers2.sort().drop('index', axis = 1)

#Initialize similarity numbers    
Master_File['month_cosine_similarity'] = 1.0
Master_File['month_jaccard_similarity'] = 1.0
Master_File['month_simple_similarity'] = 1.0

for i in range(-4, -8, -4):
    
    end_date = df_init['File Date'].max() + timedelta(weeks = i +4) # ending current month
    path = ("/Users/z013nx1/Documents/" + end_date.strftime("%B %d %Y") + ".txt") 
    print(end_date)
    print(path)
    File = pd.read_csv(path, sep = ',')
    col_name = end_date.strftime("%B %d %Y")
    File[col_name] = 1
    one = pd.merge(File, Master_File, how = 'outer', on='Ticker')
    
    columnNameCS = col_name + ' cosine_similarity'
    columnNameJS = col_name + ' jaccard_similarity'
    columnNameSS = col_name + ' simple_similarity'
    
    for i in range(len(one)):
        if one.ix[i, col_name] == 1.0:
            one.ix[i, columnNameCS] = one.ix[i, 'cosine_similarity']
            one.ix[i, columnNameJS] = one.ix[i, 'jaccard_similarity']
            one.ix[i, columnNameSS] = one.ix[i, 'simple_similarity']
        else:
            one.ix[i, columnNameCS] = one.ix[i, 'month_cosine_similarity']
            one.ix[i, columnNameJS] = one.ix[i, 'month_jaccard_similarity']
            one.ix[i, columnNameSS] = one.ix[i, 'month_simple_similarity']
            
            one = one.drop(['cosine_similarity', 'jaccard_similarity', 'simple_similarity', 'cosine_quintile', \
            'jaccard_quintile', 'simple_quintile', 'month_cosine_similarity', 'month_jaccard_similarity', \
            'month_simple_similarity', col_name, 'duplicate'], axis = 1)
            
    # cosine similarity quintile values
    # quantile set to 0.20 for quintile
    cos_quintile1 = one['cosine_similarity'].quantile(0.2)
    cos_quintile2 = one['cosine_similarity'].quantile(0.4)
    cos_quintile3 = one['cosine_similarity'].quantile(0.6)
    cos_quintile4 = one['cosine_similarity'].quantile(0.8)
    
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
    one['cosine_quintile'] = one.apply(lambda row: cos_quintile_rank(row), axis = 1)
    
    # jacaard similarity quintile values
    # quantile set to 0.20 for quintile
    jac_quintile1 = one['jaccard_similarity'].quantile(0.2)
    jac_quintile2 = one['jaccard_similarity'].quantile(0.4)
    jac_quintile3 = one['jaccard_similarity'].quantile(0.6)
    jac_quintile4 = one['jaccard_similarity'].quantile(0.8)
    
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
    one['jaccard_quintile'] = one.apply(lambda row: jac_quintile_rank(row), axis = 1)
    
    # simple similarity quintile values
    # quantile set to 0.20 for quintile
    simple_quintile1 = one['simple_similarity'].quantile(0.2)
    simple_quintile2 = one['simple_similarity'].quantile(0.4)
    simple_quintile3 = one['simple_similarity'].quantile(0.6)
    simple_quintile4 = one['simple_similarity'].quantile(0.8)
    
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
    one['simple_quintile'] = one.apply(lambda row: simple_quintile_rank(row), axis = 1)
    
    one.drop(['duplicate'], axis = 1) #final DF, dropping duplicate column which is no longer needed
    print (i)
            
            
            
for i in range(-8, -12, -4):
    
    end_date = df_init['File Date'].max() + timedelta(weeks = i +4) # ending current month
    previous_date = df_init['File Date'].max() + timedelta(weeks = i+8) # ending previous month
    path = ("/Users/z013nx1/Documents/" + end_date.strftime("%B %d %Y") + ".txt") 
    File = pd.read_csv(path, sep = ',')
    col_name = end_date.strftime("%B %d %Y")
    prev_col_name = previous_date.strftime("%B %d %Y")
    File[col_name] = 1
    one = pd.merge(one, File, how = 'outer', on='Ticker')
    
    columnNameCS = col_name + ' cosine_similarity'
    columnNameJS = col_name + ' jaccard_similarity'
    columnNameSS = col_name + ' simple_similarity'
    
    prevColumnNameCS = prev_col_name + ' cosine_similarity'
    prevColumnNameJS = prev_col_name + ' jaccard_similarity'
    prevColumnNameSS = prev_col_name + ' simple_similarity'
    
    for i in range(len(one)):
        if one.ix[i, col_name] == 1.0:
            one.ix[i, columnNameCS] = one.ix[i, 'cosine_similarity']
            one.ix[i, columnNameJS] = one.ix[i, 'jaccard_similarity']
            one.ix[i, columnNameSS] = one.ix[i, 'simple_similarity']
        else:
            one.ix[i, columnNameCS] = one.ix[i, prevColumnNameCS]
            one.ix[i, columnNameJS] = one.ix[i, prevColumnNameJS]
            one.ix[i, columnNameSS] = one.ix[i, prevColumnNameSS]
            
            one = one.drop(['cosine_similarity', 'jaccard_similarity', 'simple_similarity', 'cosine_quintile', \
            'jaccard_quintile', 'simple_quintile', 'month_cosine_similarity', 'month_jaccard_similarity', \
            'month_simple_similarity'], axis = 1)
            
            
            
# update file path based on end date
    
# strip out bulky columns    
df_clean = one.drop(['''UPDATE BASED ON OUTPUT ABOVE'''], axis = 1)         
            
#############
#############
#############
# FILE EXPORT
#############
#############
#############

path = '/Users/z013nx1/Documents/master_file.txt'
df_clean.to_csv(path, sep = ",")
