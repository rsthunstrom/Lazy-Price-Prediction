# -*- coding: utf-8 -*-


import requests  # functions for interacting with web pages
from lxml import html  # functions for parsing HTML

#import numpy as np
import pandas as pd
#import matplotlib.pylab as plt
import xlsxwriter
from bs4 import BeautifulSoup  # DOM html manipulation

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

AllURL.append("URL")

#for ctr, subject in enumerate(table.xpath('tr')):
#for ctrb, body in enumerate(table.xpath('tbody')):
for ctr, subject in enumerate(table.xpath('tr')):
        ticker = subject[0].text_content().replace("\n"," ") 
        compname = subject[1].text_content().replace("\n"," ") 
        reportlink = subject[2].text_content().replace("\n"," ")
        #report_url = subject[2].attrib["href"]  
        sector = subject[3].text_content().replace("\n"," ")
        subindustry = subject[4].text_content().replace("\n"," ")
        CIK = subject[7].text_content().replace("\n"," ")
        Allticker.append(ticker)
        Allcompname.append(compname)
        #Allreportlink.append(
        Allsector.append(sector)
        Allsubindustry.append(subindustry)
        AllCIK.append(CIK.lstrip('0'))
        for company in subject.xpath('td'):
            for companydetail in company.xpath('a'):      
                company_url = companydetail.attrib["href"] +"&type=10-Q&count=40"
    #             company_name = companydetail.attrib["title"]
                    #print ",<a href='%s'>%s</a>" %(companydetail.get("href"), link.text)
                if "https://www.sec.gov/cgi-bin/browse-edgar" in company_url:
                    AllURL.append(company_url)
                #Allcompany.append(company_name)  

s1 = pd.Series(Allcompname)
s2 = pd.Series(Allticker)
s3 = pd.Series(Allsector)
s4 = pd.Series(Allsubindustry)
s5 = pd.Series(AllCIK)             
s6 = pd.Series(AllURL)
#s5 = pd.Series(Allcompany)
#print s3

df2 = pd.DataFrame({'Company': s1,'Ticker':s2,'Sector':s3,'Subindustry':s4,'CIK':s5,'URL':s6})
#df2.drop(df2.index[0])
df2.drop(0, inplace=True)


#10-q code

#AllreportURL.append("ReportURL")
#AllCIK2.append("CIK") 
for topctr in range(1,(len(s6))):
#for topctr in range(1,3):
    URLaddress =  (s6.ix[topctr])
    Ticker3 =  (s2.ix[topctr])
    #filename =   (df.ix[topctr,'Company'] + ".xlsx")
    # -----------------------------------------------
    # the requests and lxml packages
    # -----------------------------------------------
    if (topctr not in (183,184,420, 421)):
        reportpage = requests.get(URLaddress)
        #web_page_text = web_page.text
        #reportpage = requests.get('https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000066740&type=10-Q')
        reporttree = html.fromstring(reportpage.text)
        #print_element (tree)   
        reporttables = reporttree.xpath('//table')        
        reporttable = reporttree.xpath('//table[@class="tableFile2"]')[0]
        #print_element(table)      
        for ctr2, subject2 in enumerate(reporttable.xpath('tr')):
                reporttype = subject2[0].text_content().replace("\n"," ") 
                if "Filings" not in reporttype:
                    reportdesc = subject2[2].text_content().replace("\n"," ")
                    reportdate = subject2[3].text_content().replace("\n"," ") 
                    Allreporttype.append(reporttype)
                    Allreportdesc.append(reportdesc)
                    Allreportdate.append(reportdate)
                    Allreportticker3.append(Ticker3)
                    for company2 in subject2.xpath('td'):
                        for companydetail2 in company2.xpath('a'):      
                            company_url2 = "https://www.sec.gov" + companydetail2.attrib["href"] 
                            if "https://www.sec.gov/Archives/edgar/data" in company_url2:
                                splitcompanyurl2= company_url2.split('/') 
                                #print(splitcompanyurl2[6])   
                                AllreportURL.append(company_url2)    
                                #print(company_url2)
                                AllCIK2.append(splitcompanyurl2[6])
                                print(topctr, ctr2, splitcompanyurl2[6])  



R1 = pd.Series(Allreporttype)
R2 = pd.Series(Allreportdesc)
R3 = pd.Series(Allreportdate)
R4 = pd.Series(AllreportURL)
R5 = pd.Series(AllCIK2)
R6 = pd.Series(Allreportticker3)

df3 = pd.DataFrame({'Report Type': R1,'Report Description':R2,'Report Date':R3,'Report URL':R4,'CIK':R5,'Ticker':R6})
#$df3.drop(0, inplace=True)



#sysout

filename3 = "SP500CompList.xlsx"

writer = pd.ExcelWriter(filename3, engine = 'xlsxwriter')
df2.to_excel(writer, sheet_name= 'Sheet1')
writer.save()
writer.close()



filename4 = "10QREPORT.xlsx"

writer2 = pd.ExcelWriter(filename4, engine = 'xlsxwriter')
df3.to_excel(writer2, sheet_name= 'Sheet1')
writer2.save()
writer2.close()
