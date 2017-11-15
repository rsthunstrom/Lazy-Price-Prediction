########Backup Plan##########




# library(rattle)
library(dplyr)
library(lubridate)
library(zoo)
library(tidyverse)
library(data.table)


# rattle()
getwd()

sp500 <- read.csv(file = 'SP500CompList.csv', header = TRUE) #SP500CompList.csv
data <- read.csv(file = 'LM_10X_Summaries_2016.csv', header = TRUE) #LM_10X_Summaries_2016.csv
pe_score <- read.csv(file = 'PEimport.csv', header = TRUE) #PEimport.csv

filterdata <- semi_join(data, sp500) #filters to just our sp500 data.
filterdata <- inner_join(filterdata, sp500)
filterdata <- left_join(filterdata, pe_score)

# write.csv(filterdata, file ='Backup_Data.CSV')

############# Stuart starting here #####################
new_data1 <- read.csv("Backup_Norm.csv", header = TRUE)
head(new_data1)
str(new_data1)

### convert to date type
new_data1$Date<- as.Date(as.character(new_data1$FILING_DATE), format="%Y %m %d")

#normalize Net File size
new_data1$NormFileSize <- (new_data1$NetFileSize - mean(new_data1$NetFileSize)) / sd(new_data1$NetFileSize)

#### sort in ascending date order
sorted_data<- new_data1[order(new_data1$Date),]
head(sorted_data)
str(sorted_data)


### convert ticker to character from factor
sorted_data$Ticker<- as.character(sorted_data$Ticker)

# last day of the month feature (will need this)
#print(LastDayInMonth((sorted_data$Date[1])))

#### might need this, but not using now
##firstDayMonth=function(x)
#{           
#  x=as.Date(as.character(x))
#  day = format(x,format="%d")
#  monthYr = format(x,format="%Y-%m")
#  y = tapply(day,monthYr, min)
#  first=as.Date(paste(row.names(y),y,sep="-"))
#  as.factor(first)
#}
##


###### import S&P 500 ticker list

ticker_data <- read.csv("SP500CompList.csv", header = TRUE)
head(ticker_data)
str(ticker_data)

ticker_list<- as.character(ticker_data$Ticker)
date_column<- c("Date")


### create an empty matrix for each sim score using. Then convert to DF
columns<-  length(ticker_list) + 1
norm_file_size_data <- as.data.frame(matrix(nrow = nrow(new_data1), ncol = columns))

names(norm_file_size_data) <- c(date_column, ticker_list)

## Check
head(norm_file_size_data)

#### fill the dataframe with the nomalized file size data
for(i in 1:nrow(sorted_data)) {
  col_name<- sorted_data$Ticker[i] 
  id_col<- which(names(norm_file_size_data) == col_name)
  norm_file_size_data[(i: nrow(sorted_data)), id_col]<- sorted_data$NormFileSize[i]
  norm_file_size_data$Date[i]<- as.Date(sorted_data$Date[i], format = "%Y %m %d")
  print(i)
}

#### convert Date to Date format
norm_file_size_data$Date<- as.Date(norm_file_size_data$Date)

### check
as.Date(as.character(new_data1$FILING_DATE), format="%Y %m %d")

str(norm_file_size_data)
head(norm_file_size_data)
tail(norm_file_size_data)
head(norm_file_size_data_short)
##### Cut size  of data frame down to begin from 2000-01-01

norm_file_size_data_short <- norm_file_size_data[which(norm_file_size_data$Date > c("2007-01-01")),]

###### Write intetrmediate data into csv file #####################
write.csv(norm_file_size_data_short, file = "norm_file_size_data_short.csv")


###### up to here ###########################################

















##### Josh's code

##new_data1 <- filterdata

#normalize Net File size
new_data1$NetFileSize <- (new_data1$NetFileSize - mean(new_data1$NetFileSize)) / sd(new_data1$NetFileSize)

ymd(new_data1$FILING_DATE, quiet = TRUE)

write.csv(new_data1, file = 'Backup_Norm.csv')

attach(new_data1)
new_data1 <- new_data1[which(FILING_DATE > 20000101),] #adjust for our data range
new_data1$date <- as.yearmon(as.character(new_data1$FILING_DATE), "%Y%m")

# dt <- lapply(split(new_data, new_data$date), function(x) {
#   x$key <- with(x, cut(new_data$NetFileSize, quantile(new_data$NetFileSize),
#                              labels = 1:5, include.lowest = TRUE))
#   x
# })



portfolio <- data.frame('Date', 'Q1_quintile', 'Q5_quintile')



# dt <- as.data.table(new_data)
# dt[,list(value, date, findInterval(value, quantile(value, c())))]

# monthquantile <- function(NetFileSize, date) {
#   for(i in 'date') {
#     new_data$quantile <- ntile(new_data$NetFileSize, 5)
#     
#   }
# }
# monthquantile(new_data)
