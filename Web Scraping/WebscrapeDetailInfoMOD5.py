# -*- coding: utf-8 -*-

from __future__ import division, print_function
import requests  # functions for interacting with web pages
from lxml import html  # functions for parsing HTML
from bs4 import BeautifulSoup  # DOM html manipulation
import os
import pandas as pd
import xlrd



#inputfilename= "finalpaymentservicelist2.xlsx"
inputfilename = "proj15aoutput4.xlsx"

xls_file = pd.ExcelFile(inputfilename)
df = xls_file.parse('Sheet1')
filename2 = "Riskoutput4.xlsx"


AllCIK = []
AllFiledate =  []
AllRiskBoolean =  []
AllReporttype =  []
AllReportticker =  []

for topctr in range(0,(len(df))):
    URLaddress =  (df.ix[topctr,'Report URL'])
    Filedate = (df.ix[topctr,'File Date'])
    CIK = (df.ix[topctr,'CIK']) 
    Ticker = (df.ix[topctr,'Ticker'])
    Reporttype = (df.ix[topctr,'Report Type'])           
#for topctr in range(0,(len(df))):
#    URLaddress =  (df.ix[topctr,'URL'])
#    filename =   (df.ix[topctr,'Company'] + ".xlsx")
    # -----------------------------------------------
    # the requests and lxml packages
    # -----------------------------------------------
#URLaddress= 'http://www.sec.gov/Archives/edgar/data/320193/000032019317000009/a10-qq32017712017.htm#s8706EEADEE38541BBC270E88E63C54AB'
#URLaddress= 'http://www.sec.gov/Archives/edgar/data/66740/000155837017005582/mmm-20170630x10q.htm#Item1A_RiskFactors__025242'
#URLaddress = 'http://www.sec.gov/Archives/edgar/data/66740/000110465906069356/a06-21556_110q.htm'
#URLaddress = 'http://www.sec.gov/Archives/edgar/data/1551152/000155115217000025/mmm-20170630x10q.htm'
#URLaddress = 'http://www.sec.gov/Archives/edgar/data/66740/000155837017005582/mmm-20170630x10q.htm'
#URLaddress = 'https://www.sec.gov/Archives/edgar/data/920760/000162828017009782/len-2017831x10qq3.htm'
#filename= "prototype2.xlsx"  
    filename = str(CIK) +"-"+ str(Filedate)+ ".xlsx"
    web_page = requests.get(URLaddress) 
    web_page_text = web_page.text
    print (web_page_text)
    # parse using LXML parser
    soup = BeautifulSoup(web_page_text, "lxml")
    subjectdatasaved = ""
    print (URLaddress,Filedate,filename)
    Allsubjectdata =[]
    paractr = 0
    subjectdata = headerdata = ""  
    #AllCIK.append(CIK)            
    #AllFiledate.append(Filedate)  
    #AllReporttype.append(Reporttype)
    #AllReportticker.append(Ticker)  
    for content in soup.findAll('text'):    
            for record in content.findAll('div'):                  
                for data in record.findAll('font'):   
                    subjectdata = data.text
                    paractr = paractr+1
                    print (subjectdata)
                    #print (paractr)
                    #print (len(subjectdata))
                    Allsubjectdata.append(subjectdata)
                    AllCIK.append(CIK)           
                    AllFiledate.append(Filedate)  
                    AllReporttype.append(Reporttype)
                    AllReportticker.append(Ticker)           
            # for data2 in record.findAll('th'):      
                #    headerdata = data2.text
    s1 = pd.Series(AllCIK) 
    s2 = pd.Series(Allsubjectdata) 
    s3 = pd.Series(AllFiledate) 
    s4 = pd.Series(AllReporttype) 
    s5 = pd.Series(AllReportticker)         
    #print (s2)      
    df2 = pd.DataFrame({'CIK':s1,'Information':s2,'File Date': s3,'Report Type':s4,'Ticker':s5})     
    #print (df2)
    writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
    df2.to_excel(writer, sheet_name= 'Sheet1')
    writer.save()
    writer.close()     
#    Riskbooleans  = False
#    for rowdetail in df2.Information:
#        if ("Risk Factor" in rowdetail):
#            Riskbooleans = True
#    AllRiskBoolean.append(Riskbooleans)        
#s3 = pd.Series(AllCIK)  
#s4 = pd.Series(AllFiledate)  
#s5 = pd.Series(AllRiskBoolean)   
      
#df3 = pd.DataFrame({'CIK':s3, 'Filedate':s4, 'Contain Risk?':s5})             
#writer2 = pd.ExcelWriter(filename2, engine = 'xlsxwriter')
#df3.to_excel(writer2, sheet_name= 'Sheet1')
#writer.save()
#writer.close()  

     
          
               

#print (isRisk)
#print (df2[isRisk])

#df3 = pd.DataFrame({'Risk': isRisk})
#print (df3)
#print (df3.index[df3['Risk']].tolist())

#print (RiskStartIdx)
      
#booleans2 = []
#for rowdetail2 in df2.Information:
#    if "Item 2" in rowdetail2:
#        booleans2.append(True)
#    else:
#        booleans2.append(False)      
        
#isRisk2 = pd.Series(booleans2)
#print (df2[isRisk2])

#print (df2[6359:6364])
      



#print (df2.index[df2['Information'].find("Risk Factor").tolist()      )



#if b.lower().find(a.lower()) != -1:
#    do_whatever
                
#writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
#df2.to_excel(writer, sheet_name= 'Sheet1')
#writer.save()
#writer.close()
    
   
