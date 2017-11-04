# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 14:52:53 2017

@author: z013nx1
"""

from __future__ import division, print_function
import pandas as pd
from datetime import timedelta

#Consumer Staple only dataset
#proj15aoutput4CS
rdd = pd.read_excel('/Users/z013nx1/Documents/proj15aoutputCS.xlsx') #import text file with pipe delimiter
df = pd.DataFrame(rdd) #convert to pandas df


df['File Date'] = pd.to_datetime(df['File Date']) #convert date to timedate

start_time = df['File Date'].max() #2017-11-01

#create a file for each month for the last 10 years
for i in range(-4, -6240, -4):
    start_date = df['File Date'].max() + timedelta(weeks = i) #beginning current month
    end_date = df['File Date'].max() + timedelta(weeks = i +4) # ending current month
    ly_start = df['File Date'].max() + timedelta(weeks = i - 56) #beginning ly month
    ly_end = df['File Date'].max() + timedelta(weeks = i - 44) #ending ly month
    
    df_current = df[(df['File Date'] < end_date) & (df['File Date'] >= start_date)]
    df_ly = df[(df['File Date'] < ly_end) & (df['File Date'] >= ly_start)]
    
    df_current['Current'] = 1 #assign categorical flag to identify which last year to keep
    df_ly['Current'] = 0 #assign categorical flag to identify which last year to keep
    
    df_current_ticks = df_current['Ticker'] #get current tickers to analysis
    df_ly_keep = df_ly[df_ly['Ticker'].isin(df_current_ticks)] #only keep last year stocks in current
    frames = [df_current, df_ly_keep] #DFs to join
    df_join = pd.concat(frames) #Set current and LY DFs
    df_final = df_join.reset_index() #reset index for processing
    print(df_final)
