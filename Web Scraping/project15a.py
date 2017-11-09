# -*- coding: utf-8 -*-


import requests  # functions for interacting with web pages
from lxml import html  # functions for parsing HTML

#import numpy as np
import pandas as pd
#import matplotlib.pylab as plt
import xlsxwriter
from bs4 import BeautifulSoup  # DOM html manipulation

# -*- coding: utf-8 -*-

import xlrd





def print_element(element):
    print ("<%s %s>%s ..." % (element.tag, element.attrib, element.text_content()[:200].replace("\n", " ")))


# -----------------------------------------------
# the requests and lxml packages
# -----------------------------------------------

#page = requests.get('https://en.wikipedia.org/wiki/List_of_online_payment_service_providers')


page = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

tree = html.fromstring(page.text)
#print_element (tree)

tables = tree.xpath('//table')
    
table = tree.xpath('//table[@class="wikitable sortable"]')[0]
#print_element(table)


Allticker = []
Allcompname = []
Allreportlink = []
Allsector = []
Allsubindustry = []
AllCIK = []
AllURL = []   
Allcompany = []

Allreporttype = []
Allreportdesc = []
Allreportdate = []
AllreportURL = []
AllCIK2 = []
AllreportURL3 = []
AllCIK3 = []
Allreporttype3 = []
Allfiledate3 = []
Allreportticker3 = []


inputfilename= "10QREPORTa1K.xlsx"
#inputfilename= "bad.xlsx"

xls_file = pd.ExcelFile(inputfilename)
df = xls_file.parse('Sheet1')
for topctr2 in range(0,(len(df))):
    URLaddress2 =  (df.ix[topctr2,'Report URL'])
    #filename =   (df.ix[topctr,'Company'] + ".xlsx") 
#for topctr2 in range(1,(len(R4))):
#for topctr in range(1,3):
#    URLaddress2 =  (R4.ix[topctr])
    
    Filedate2 = (df.ix[topctr2,'Report Date'])
    CIK2 = (df.ix[topctr2,'CIK'])
    Ticker = (df.ix[topctr2,'Ticker'])    
    reportpage2 = requests.get(URLaddress2)
    reporttree2 = html.fromstring(reportpage2.text)
    reporttables2 = reporttree2.xpath('//table')        
    reporttable2 = reporttree2.xpath('//table[@class="tableFile"]')[0]
    #print_element(reporttable2)
    
    #AllreportURL3.append("ReportURL")
    #AllCIK3.append("CIK")
    
    for ctr3, subject3 in enumerate(reporttable2.xpath('tr')):
            detailreporttype = subject3[3].text_content().replace("\n"," ") 
    #        detailreportdesc = subject3[1].text_content().replace("\n"," ")
    #        reportdate = subject3[3].text_content().replace("\n"," ") 
    #        Allreportdesc.append(reportdesc)
    #        Allreportdate.append(reportdate)
    #        print (detailreporttype)
         

            if "10-K" in detailreporttype:
                    Allreporttype3.append(detailreporttype)
                    print (CIK2)
                #AllURL.append(company_url)
                #Allcompany.append(company_name)  
                #for index3, item3 in enumerate(reporttable2.xpath('tr')):
                    for company3 in subject3.xpath('td'):
                        for companydetail3 in company3.xpath('a'):      
                            company_url3 = "https://www.sec.gov" + companydetail3.attrib["href"] 
                            splitcompanyurl3= company_url3.split('/')
                            #print(company_url3)
                            #print(splitcompanyurl3[4])  
                            AllreportURL3.append(company_url3)  
                            #AllCIK3.append(splitcompanyurl3[4]) 
                            Allfiledate3.append(Filedate2)
                            AllCIK3.append(CIK2)
                            Allreportticker3.append(Ticker)
                        
T4 = pd.Series(Allreporttype3)
T1 = pd.Series(Allfiledate3)
T2 = pd.Series(AllCIK3)
T3 = pd.Series(AllreportURL3)
T5 = pd.Series(Allreportticker3)
#print(T3)

df4 = pd.DataFrame({'File Date': T1,'CIK':T2,'Report URL':T3, 'Report Type':T4, 'Ticker':T5})
#print(df4)

filename3 = "proj15aoutput4badoneK.xlsx"

writer = pd.ExcelWriter(filename3, engine = 'xlsxwriter')
df4.to_excel(writer, sheet_name= 'Sheet1')
writer.save()
writer.close()
