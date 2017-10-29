# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 16:40:04 2017

@author: z013nx1
"""

# libs required
import pandas as pd
import re, math
from collections import Counter
import numpy as np

##################
##################
##################
# IMPORT TEXT FILE
##################
##################
##################


df_sort = df.sort_values(['Ticker', 'File Date']) #sort by ticker and year

df_sort['text_list'] = df_sort.groupby(('Ticker', 'File Date'))['RiskFactorText'].apply(lambda x: list(x)).tolist() #create list from text

df_sort.reset_index(drop = 'index') #reset index after sort

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
for i in range(len(df_sort)-1):
    if df_sort.ix[i, 'Ticker'] == df_sort.ix[i+1, 'Ticker']:
        cos_value = calc_cosine(df_sort.ix[i, 'text_list'][0], df_sort.ix[i+1, 'text_list'][0])
        cos_sim.append(cos_value)
        j_value = calc_jaccard(df_sort.ix[i, 'text_list'][0], df_sort.ix[i+1, 'text_list'][0])
        jac_sim.append(j_value)
        simple_value = calc_simple(df_sort.ix[i, 'text_list'][0], df_sort.ix[i+1, 'text_list'][0])
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
df_sort['cosine_similarity'] = cos_sim
df_sort['jaccard_similarity'] = jac_sim
df_sort['simple_similarity'] = simple_sim
df_sort['duplicate'] = duplicate

df_final = df_sort[df_sort['duplicate'] != 1] #remove any rows which are the duplicate for each ticker

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

df_final.to_csv('/Users/z013nx1/Documents/stocksWithSimilarityMetricsQuintiles.txt') # export to text
