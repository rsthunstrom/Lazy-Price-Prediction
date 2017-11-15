########Backup Plan##########




# library(rattle)
library(dplyr)
library(lubridate)
library(zoo)
library(tidyverse)
library(data.table)
library(plyr)
library(reshape2)
library(binr)
library(survival)
library(bsts)
library(sqldf)

# rattle()
getwd()

sp500 <- read.csv(file = 'SP500CompList.csv', header = TRUE) #SP500CompList.csv
data <- read.csv(file = 'LM_10X_Summaries_2016.csv', header = TRUE) #LM_10X_Summaries_2016.csv
pe_score <- read.csv(file = 'PEimport.csv', header = TRUE) #PEimport.csv

filterdata <- semi_join(data, sp500) #filters to just our sp500 data.
filterdata <- inner_join(filterdata, sp500)
filterdata <- left_join(filterdata, pe_score)

# write.csv(filterdata, file ='Backup_Data.CSV')

new_data <- filterdata

summary(new_data$NetFileSize)

# Normalizinf the variables we are looking at

data_norm <- new_data %>% mutate_at(c('N_Unique_Words',
                                             'N_Negative',
                                             'N_Positive',
                                             'NetFileSize'), 
                                    funs(scale(.) %>% as.vector))
                                       

#normalize Net File size
# new_data$NetFileSize <- (new_data$NetFileSize - mean(new_data$NetFileSize)) / sd(new_data$NetFileSize)

ymd(data_norm$FILING_DATE, quiet = TRUE)

write.csv(data_norm, file = 'Backup_Norm_V2.csv')


data_norm_trim <- data_norm[which(data_norm$FILING_DATE > 20050101),] #adjust for our data range
data_norm_trim$date <- as.yearmon(as.character(data_norm_trim$FILING_DATE), "%Y%m")

# dt <- lapply(split(new_data, new_data$date), function(x) {
#   x$key <- with(x, cut(new_data$NetFileSize, quantile(new_data$NetFileSize),
#                              labels = 1:5, include.lowest = TRUE))
#   x
# })



summary(data_norm_trim$NetFileSize)

# data_norm_trim$id <- rownames(data_norm_trim)
# melt(data_norm_trim)
# 
# data_norm_trim <-data.frame(words = unlist(words))


data_norm_trim$date <- as.factor(data_norm_trim$date)

#create quantile column
data_norm_trim$qtile <- NA
data_norm_trim$full_qtile <- NA

# get full dataset quantile not monthly - Gotta put these in the 5 bins
# data_norm_trim$full_qtile <- quantile(data_norm_trim$NetFileSize,
#                                       probs = seq(0, 1, .2))

# data_norm_trim$full_qtile <- bins.quantiles(data_norm_trim$NetFileSize,
#                                             target.bins = 5,
#                                             max.breaks = 5,
#                                             verbose = TRUE)

# quantiles for full data set
data_norm_trim$full_qtile <- cut(data_norm_trim$NetFileSize, c(-Inf, -0.500344773168835,
                                                               -0.311306718162741,
                                                               -0.00679489673429272,
                                                               0.604942607515019,
                                                               Inf), labels = c('1', '2', '3', '4', '5'))
colnames(data_norm_trim)[36] <- 'filesize_qtile'

data_norm_trim$unique_words_qtile <- NA
data_norm_trim$neg_words_qtile <- NA
data_norm_trim$pos_words_qtile <- NA

#This gives the break points for each bin
data_norm_trim$pos_words_qtile <- bins.quantiles(data_norm_trim$N_Positive,
                                            target.bins = 5,
                                            max.breaks = 5,
                                            verbose = TRUE)

data_norm_trim$unique_words_qtile <- cut(data_norm_trim$N_Unique_Words, c(-Inf, -0.514037536926028,
                                                               -0.116301310082204,
                                                               0.387829357442343,
                                                               1.08386775441904,
                                                               Inf), labels = c('1', '2', '3', '4', '5'))

data_norm_trim$neg_words_qtile <- cut(data_norm_trim$N_Negative, c(-Inf, -0.530422294028695,
                                                                   -0.298893396996553,
                                                                   0.0476809147099462,
                                                                   0.643040935649741,
                                                                    Inf), labels = c('1', '2', '3', '4', '5'))

data_norm_trim$pos_words_qtile <- cut(data_norm_trim$N_Positive, c(-Inf, -0.524931184759076,
                                                                   -0.308671204572745,
                                                                   0.0381608391223152,
                                                                   0.691021156665958,
                                                                   Inf), labels = c('1', '2', '3', '4', '5'))
qtvars <- 

qtdf <- data_norm_trim[c(31, 2, 34, 36:39)]

write.csv(qtdf, file = 'ticker_quantiles.csv')

qtdf$date <- as.factor(qtdf$date)
qtdf$FILING_DATE<- as.Date(as.character(qtdf$FILING_DATE), format="%Y %m %d")


date_seq <- seq(as.Date("2005-01-06"), by = "month", length.out = 144)
date_last_day<- LastDayInMonth(date_seq)
head(date_last_day)

fssql <- sqldf("select FILING_DATE, filesize_qtile, Ticker INTO portfolio from qtdf where filesize_qtile
               = '1' or filesize_qtile = '5' group by FILING_DATE")




############# Stuart starting here #####################
new_data1 <- data_norm_trim
head(new_data1)
str(new_data1)

### convert to date type
new_data1$Date<- as.Date(as.character(new_data1$FILING_DATE), format="%Y %m %d")

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




#split by month and run quantile - gives me an error but close
# data_norm_trim <- ddply(data_norm_trim, ~ date,
#                         row.names = NULL, transform,
#                         qtile = quantile(data_norm_trim$NetFileSize))


portfolio <- data.frame(date = as.Date(character()),
                        Q1_quintile=character(),
                        Q5_quintile=character())






write.csv(portfolio, file = 'portfolio.csv')


# dt <- as.data.table(new_data)
# dt[,list(value, date, findInterval(value, quantile(value, c())))]

# monthquantile <- function(NetFileSize, date) {
#   for(i in 'date') {
#     new_data$quantile <- ntile(new_data$NetFileSize, 5)
#     
#   }
# }
# monthquantile(new_data)
