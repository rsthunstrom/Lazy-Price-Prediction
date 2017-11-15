########Backup Plan##########




# library(rattle)
library(dplyr)
library(lubridate)
library(zoo)
library(tidyverse)
library(data.table)
library(survival)
library(rowr)
library(mondate)
library("DataCombine")
install.packages("zoo")
install.packages("pscl")
install.packages("rpart")
install.packages("fma")
install.packages("forecast")
install.packages("car")
install.packages("MASS")
install.packages("TTR")
install.packages("lubridate")
install.packages("DataCombine")

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
new_data <- read.csv("Backup_Norm.csv", header = TRUE)
head(new_data)
str(new_data)

### convert to date type
new_data$Date<- as.Date(as.character(new_data$FILING_DATE), format="%Y %m %d")

#normalize Net File size
#new_data$NormFileSize <- (new_data$NetFileSize - mean(new_data$NetFileSize)) / sd(new_data$NetFileSize)

#### sort in ascending date order
sorted_data<- new_data[order(new_data$Date),]
head(sorted_data)
str(sorted_data)


##### Cut size  of data frame down to begin from 2005-01-01

sorted_data_short <- sorted_data[which(sorted_data$Date > c("2004-01-01")),]

### convert ticker to character from factor
sorted_data_short$Ticker<- as.character(sorted_data_short$Ticker)

###### Write intetrmediate data into csv file #####################
write.csv(sorted_data_short, file = "sorted_data_short.csv")

head(sorted_data_short)
str(sorted_data)
which(sorted_data_short$Date == c("2004-04-15"))



###### import S&P 500 ticker list

ticker_data <- read.csv("SP500CompList.csv", header = TRUE)
head(ticker_data)
str(ticker_data)

ticker_list<- as.character(ticker_data$Ticker)
date_column<- c("Date")


### create an empty matrix for each sim score using. Then convert to DF
columns<-  length(ticker_list) + 1
norm_file_size_data <- as.data.frame(matrix(nrow = nrow(sorted_data_short), ncol = columns))

names(norm_file_size_data) <- c(date_column, ticker_list)

## Check
head(norm_file_size_data)

#### fill the dataframe with the Gross File Size size data
for(i in 1:nrow(sorted_data_short)) {
  col_name<- sorted_data_short$Ticker[i] 
  id_col<- which(names(norm_file_size_data) == col_name)
  ###changing the variaBLE OF INTEREST HERE
  norm_file_size_data[(i: nrow(sorted_data_short)), id_col]<- sorted_data_short$N_Positive[i] - sorted_data_short$N_Negative[i]
  norm_file_size_data$Date[i]<- as.Date(sorted_data_short$Date[i], format = "%Y %m %d")
  print(i)
}

#### convert Date to Date format
norm_file_size_data$Date<- as.Date(norm_file_size_data$Date)

### check
as.Date(as.character(new_data$FILING_DATE), format="%Y %m %d")

str(norm_file_size_data_short)
head(norm_file_size_data)
tail(norm_file_size_data)


##### now compute yoy metrics 
look_back <- 11*30
print(last(norm_file_size_data$Date) - look_back)

### the first filing in 2005
print(norm_file_size_data$Date[1807])

print(norm_file_size_data[(1807-look_back), (1:5)])
print(norm_file_size_data[1807, 1:5])

### saving some data
# Save an object to a file
saveRDS(norm_file_size_data, file = "n_posminusnegative.rds")
# Restore the object
#readRDS(file = "norm_file_size_data1.rds")


#### initialize new DF
yoy_file_size <- data.frame()
head(yoy_file_size)
str(yoy_file_size)

### compute year over year metric
for(i in 1807: nrow(norm_file_size_data)) {
 difference<- norm_file_size_data[i, (2:ncol(norm_file_size_data))] / norm_file_size_data[(i - look_back), (2:ncol(norm_file_size_data))] 
 yoy_file_size <- rbind(yoy_file_size, difference) 
 print(i)
}

#### Add in Date Column to be first column and rename it
yoy_file_size<- cbind(norm_file_size_data$Date[1807:nrow(norm_file_size_data)], yoy_file_size)
#colnames(df)[colnames(df) == 'oldName'] <- 'newName'
colnames(yoy_file_size)[colnames(yoy_file_size) == "norm_file_size_data$Date[1807:nrow(norm_file_size_data)]"] <- "Date"

yoy_file_size$Date<- norm_file_size_data$Date[1807:nrow(norm_file_size_data)]
head(yoy_file_size)
str(yoy_file_size$Date)
str(yoy_file_size)
print(tail(colnames(yoy_file_size)))
###### write this file to CSV ############
write.csv(yoy_file_size, file = "N_POSNEG.csv")

str(yoy_file_size)
#### saving some data
# Save an object to a file
saveRDS(yoy_file_size, file = "N_POSNEG.rds")
# Restore the object
#readRDS(file = "yoy_file_size1.rds")


##### work on building quintiles


##### first create a list of end of month dates for the range (2005-01-06 to 2016-12-20)

date_seq <- seq(as.Date("2005-01-06"), by = "month", length.out = 144)

## check
print(date_seq)

### convert this list to last day of the month
date_last_day<- LastDayInMonth(date_seq)
## check
print(date_last_day)

date_last_day_DF <- as.data.frame(as.matrix(date_last_day, nrow = length(date_last_day), ncol = 1, stringsAsFactors=F))
date_last_day_DF$V1<- as.Date(date_last_day_DF$V1)
colnames(date_last_day_DF) <- c("Last_Date")

## check
print(date_last_day_DF)
str(date_last_day_DF)


quintiles_DF<- as.data.frame(matrix(data = NA, nrow = length(date_last_day), ncol = 5))

port_last_day<- cbind(date_last_day_DF, quintiles_DF)
colnames(port_last_day) <- c("Last_Date", "Q1", "Q2", "Q3", "Q4", "Q5")
str(port_last_day)
# check
print(port_last_day)


###run the loop here, looping across the DF, finding nearest date and pulling that row and then sorting by score, finding quintile
#### and write tickers (col names) into a list and write into the data frame



## testing final Df assembly
row_id<- max(which(yoy_file_size$Date == port_last_day$Last_Date[2]))
row_id<- max(which(yoy_file_size$Date == c("2005-01-08")))
print(row_id)



###### testing 
test_row<- yoy_file_size[30, 2: 506]
str(test_row)


sorted_test_row<- test_row[, order(test_row, na.last = "TRUE")]
sorted_rm<- sorted_test_row[ , apply(sorted_test_row, 2, function (x) !any(is.na(x)))]

divide<- trunc(length(sorted_rm)/5) -1
# ranges:
# 1: divide
# divide + 1: 2* divide +1
# 2* divide +2: 3*divide +2
#3*divide + 3: 4*divide + 3
# 4*divide + 4: 5*divide + 4

Q1_list<- colnames(sorted_rm[,1:83])
Q2_list<- colnames(sorted_rm[,84:167])
Q3_list<- colnames(sorted_rm[,168:251])
Q4_list<- colnames(sorted_rm[,252:335])
Q5_list<- colnames(sorted_rm[,336:421])

print(Q1_list)
print(Q2_list)
print(Q3_list)
print(Q4_list)
print(Q5_list)

head(sorted_rm)
tail(sorted_rm)

print(sorted_subset)
head(sorted_test_row, n = 100)
tail(sorted_test_row)

print(test_row[182])
print(test_row[442])
print(test_row[337])
print(test_row[246])
print(test_row[60])
print(test_row[285])

print(test_row[505])
print(test_row[426])
print(test_row[70])
print(test_row[493])
print(test_row[183])
print(test_row[134])

print(yoy_file_size[27:40, 1:4])
print(yoy_file_size$Date[27:40])


#### looping over last day of month to get the sorted quintiles

for (i in 1: nrow(port_last_day)){
  row_id<- max(which(LastDayInMonth(yoy_file_size$Date) == port_last_day$Last_Date[i]))
  if (row_id > 0){
    test_row<- yoy_file_size[row_id, 2: ncol(yoy_file_size)]
    sorted_test_row<- test_row[, order(test_row, na.last = "TRUE")]
    sorted_rm<- sorted_test_row[ , apply(sorted_test_row, 2, function (x) !any(is.na(x)))]
    divide<- trunc(length(sorted_rm)/5) -1
    end_q1<- divide
    begin_q2<- divide + 1
    end_q2<- 2* divide + 1
    begin_q3<- 2* divide + 2
    end_q3<- 3* divide + 2
    begin_q4<- 3* divide + 3
    end_q4<- 4* divide + 3
    begin_q5<- 4* divide + 4
    end_q5<- length(sorted_rm)
    
    port_last_day$Q1[i]<- list(c(colnames(sorted_rm[, 1:end_q1])))
    port_last_day$Q2[i]<- list(c(colnames(sorted_rm[, begin_q2:end_q2])))
    port_last_day$Q3[i]<- list(c(colnames(sorted_rm[, begin_q3:end_q3])))
    port_last_day$Q4[i]<- list(c(colnames(sorted_rm[,  begin_q4:end_q4])))
    port_last_day$Q5[i]<- list(c(colnames(sorted_rm[, begin_q5:end_q5])))
    print(i)
  }
}

### check:
head(port_last_day)
str(port_last_day)
print(port_last_day$Q5[[4]])
print(port_last_day[4,])

max(which(yoy_file_size$Date == port_last_day$Last_Date[4]))
#### saving some data
# Save an object to a file
saveRDS(port_last_day, file = "n_POSNEG.rds")
# Restore the object
readRDS(file = "my_data.rds")




###### Read in the stock price data ################################################

### list of stock tickers to read in for staples universe  #########################################
### load SP500 symbols
symbols<- ticker_data$Ticker
head(symbols)
print(symbols[84])

### removing ticker BF.B, as had data issues with it #######
symbols<- symbols[-84]
print(symbols)


string_begin <- 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol='
string_end <- '&outputsize=full&apikey=NTRDFP32SIWS6GU0&datatype=csv'

### iterate over the tickers in symbols to fill up the dataframe with stock prices
stock_data <- data.frame()
datalist = list()
for(i in seq_along(symbols)) {
  URL <- paste0(string_begin, symbols[i], string_end)
  dat <- read.csv(URL)
  print(symbols[i])
  print(nrow(dat))
  colnames(dat) <- c('timestamp', 'open', 'high', 'low', symbols[i], 'volume')
  #  assign(paste0(symbols[i],"_data"), dat)
  dat2 <- dat[, c('timestamp', symbols[i])]
  #  length(dat2)<- 213
  if (i <2){
    stock_data<- dat2
  } else{
    stock_data <- cbind.fill(stock_data, dat2[2], fill = NA)
  }
  
}

print(symbols)

## Look at the data
head(stock_data)
str(stock_data)


## convert timestamp to Dates.
stock_data$timestamp <- LastDayInMonth(stock_data$timestamp)

#### sort into descending order ####################
stock_data2<- stock_data[order(stock_data$timestamp),]
### reset the index(rownames) for the ordered stock_data2 ###########
rownames(stock_data2) <- seq(length=nrow(stock_data2))
print(stock_data2$timestamp)
### Begin process of converting from stock prices to returns

## trim to Jan 2004 to sept 2017
stock_data3<- stock_data2[47:214,]
stock_data3<- stock_data3[1:165,]
print(stock_data2$timestamp)
print(stock_data3$timestamp)

str(stock_data3)

# compute difference of log stock prices (log differences), need to get FF RF for
# excess return calculation
#stocks_diff = as.data.frame(100*apply(log(stocks_subset), 2, diff) - FF_data_3$RF) # Excess returns
stocks_log_prices <- as.data.frame(apply(stock_data3[,2:ncol(stock_data3)], 2, log))
symbols_log <- lapply(symbols, function(x) paste0(x,"_logprice"))

#add names to stocks_log_prices
names(stocks_log_prices) <- symbols_log
# Check
head(stocks_log_prices)
tail(stocks_log_prices)
#print(stock_data2$timestamp[-1])
# Apply the difference function to compute log differnces
stocks_log_diff <- as.data.frame(apply(stocks_log_prices, 2, diff))

# add names to stocks_log_diff
symbols_log_diff <- lapply(symbols, function(x) paste0(x,"_log_diff"))
names(stocks_log_diff) <- symbols_log_diff
# Check
head(stocks_log_diff)
tail(stocks_log_diff)
# Add the timestamp.
stocks_log_diff_2 <- cbind(stock_data3$timestamp[-1], stocks_log_diff)
names(stocks_log_diff_2) <- c('timestamp',symbols_log_diff)

# check
head(stocks_log_diff_2)
print(stocks_log_diff_2)
print(tail(stocks_log_diff_2))
as.character(quintiles_data$port_calc_date[i])
rower<- which(stocks_log_diff_2 == as.character(quintiles_data$port_calc_date[3]))

#print(stocks_log_diff_2[140:145,])

### Now functions to return a cumulative return.
## arguments = stock ticker and date (month ending date)
## returns the stock return for that month (so filing occured in the month before)

#### 1 month stock return function  #######
## arguments = stock ticker and date (month ending date)
## returns the stock return for that month (so filing occured in the month before)
one_month_return <- function(stock_ticker, return_date) { 
  file_row<- which(stocks_log_diff_2 == return_date)
  begin_row <- file_row 
  end_one_month_row <- file_row 
  column_name_end <- c('_log_diff')
  col_name <-  paste0(stock_ticker, column_name_end)
  id_col<- which(names(stocks_log_diff_2) == col_name)
  if (length(id_col) > 0){
  #  print(stocks_log_diff_2[begin_row,])
  #  print(stocks_log_diff_2[end_one_month_row,])
     sum_one<- sum(stocks_log_diff_2[begin_row:begin_row, id_col])
  #  print(sum_one)
    exp_one <- expm1(sum_one) 
     return(exp_one)
  } else{
      return(0)
  }
}


### test function
one_month_return('AAPL', '2014-10-31')
checker1<- which(stocks_log_diff_2 == return_date)

##### Write portfolio return functions ########
### equal weighted portfolio return from stock returns
#### one month portfolio return function #####
### given ticker list and month the portfolio is active,  returns equal weighted portfolio return for that month
### Note file_date == month before, so we have indexed forward when import the portfolio quintiles

one_month_port_return <- function(ticker_list, port_month) { 
  
  # find stock correct row in log difference DF based on file_date    
  
  ## initialize matrix n x 1, n = number of tickers
  return_list <- c(0, "2000-01-01")
  n<- length(ticker_list)
  stock_returns <- matrix(ncol = 1, nrow = n)
  ## loop over the list of stocks in ticker_list and get return for each ticker
  ## write into a list called stock_returns
  print("one_month_port_return")
  print(ticker_list)
  for(i in seq_along(ticker_list)) {
    
    stock_returns[i,1] <- one_month_return(ticker_list[i], port_month)
    print(c(stock_returns[i,1], ticker_list[i]))
  }
  ### return the mean of element in stock_returns, as equal weighted portfolio
  ### return.
  port_average<- mean(stock_returns, na.rm=TRUE)
  print(port_average)
  return_list<- c(port_average, port_month)
  # just return the portfolio return. 
  return(return_list[1])
}

#### test this function #######

test_tickers = c("IBM","EBAY", "INTC")
test_tickers_2 = c("SYMC","KO",   "AMZN", "ESRX", "VFC" , "FDX",  "CSCO" ,"BAC")
print(test_tickers)

print(test_tickers[[1]])
test_date <- c('2013-07-31')

#test_date_3<- as.yearmon(test_date)
#print(test_date_3)

port_return<- one_month_port_return(test_tickers, test_date)
port_return_2<- one_month_port_return(test_tickers_2, test_date)
print(port_return)



### Using this
#### get monthly quintiles data #######

quintiles_data <- port_last_day

##### check 
print(quintiles_data)
print(quintiles_data$Last_Date)
str(quintiles_data)

print(quintiles_data$Q1_port_clean[144])
print(quintiles_data$Q5_port_clean[144])
print(quintiles_data$Q5_clean[144])
print(quintiles_data$Q1_clean[144])

### change date into yearmon and convert to the last day of the month
#quintiles_data$Date <- as.Date(quintiles_data$Date, format = "%B %d %Y")
#quintiles_data$Date <- LastDayInMonth(quintiles_data$Date)

####### Index the date forward by a month. The portfolio was created on the last day of the month
#### so need to get returns for the FOLLOWING MONTH 

quintiles_data$port_calc_date<-  as.Date(as.mondate(quintiles_data$Last_Date) + 1)
print(quintiles_data$port_calc_date)
print(quintiles_data$Last_Date)
###3 right now Fama frenchdata  goes to september 2017 , so trim portfolio
#quintiles_data<- quintiles_data[1:72,]

### get begninning and ending month of the similarity data
begin_month <- as.yearmon(quintiles_data$port_calc_date[1])
end_month <- as.yearmon(quintiles_data$port_calc_date[nrow(quintiles_data)])

#print(LastDayInMonth(as.Date(sim_data$Date[1])))

#### Loop through the data dataframe to prep data as character
quintiles_data$Q1_clean <- lapply(quintiles_data$Q1, as.character)
quintiles_data$Q5_clean <- lapply(quintiles_data$Q5, as.character)
quintiles_data$Q3_clean <- lapply(quintiles_data$Q3, as.character)
quintiles_data$Q4_clean <- lapply(quintiles_data$Q4, as.character)
quintiles_data$Q2_clean <- lapply(quintiles_data$Q2, as.character)

####### portfolio generator code #######################################

#### Needs to be indexed forward by one month (i + 1)


## takes monthly quintile sort and creates and tracks portfolios according to rules:
## first month Q1 and Q5 go into portfolios
## stocks stay in the portfolio for 3 months, or 1 month or 2 months (a variable) then
## removed and each month assess this and see which stocks adding and which deleting
## i = 1 is the first month. in this case then portfolio = quintiles
## i = 2, in this case, Q1_curent_port = Q1_current_port (prior month) + any new names from Q1, Q5 quintiles
### loop over the entire DF going month by month creating the portfolios

# set variable for number of month a stock is in a portfolio
duration <- 3
i<- 1
Q1_current_port <- c()
Q5_current_port <- c()
for (i in 1:nrow(quintiles_data)){
  if (i == 1) {
    Q1_string<- quintiles_data$Q1_clean[1]
    Q1_current_port<- strsplit(Q1_string[[1]], " ")[[1]]
    quintiles_data$Q1_port_clean[i] <- list(unique(c(Q1_current_port)))
    
    Q5_string<- quintiles_data$Q5_clean[1]
    Q5_current_port<- strsplit(Q5_string[[1]], " ")[[1]]
    quintiles_data$Q5_port_clean[i] <- list(unique(c(Q5_current_port)))
    
  } else if (2 <= i && i <= 3){
    Q1_string<- quintiles_data$Q1_clean[i]
    Q1_string_new<- strsplit(Q1_string[[1]], " ")[[1]]
    Q1_current_unlisted<- c(unlist(quintiles_data$Q1_current_port))
    Q1_adds <- Q1_string_new[which(!(Q1_string_new%in%Q1_current_unlisted))]
    
    Q1_current_port <- c(Q1_current_unlisted, Q1_adds)
    quintiles_data$Q1_port_clean[i] <- list(unique(Q1_current_port))
    
    Q5_string<- quintiles_data$Q5_clean[i]
    Q5_string_new<- strsplit(Q5_string[[1]], " ")[[1]]
    Q5_adds <- Q5_string_new[which(!(Q5_string_new%in%Q5_current_port))]
    
    Q5_current_port <- c(Q5_current_port, Q5_adds)
    quintiles_data$Q5_port_clean[i] <- list(unique(Q5_current_port))
    
  } else{
    Q1_string<- quintiles_data$Q1_clean[i]
    Q1_string_new<- strsplit(Q1_string[[1]], " ")[[1]]
    
    #    print(Q1_string_new)
    Q1_subtract<- c(unlist(quintiles_data$Q1_port_clean[[(i - duration)]]))
    #    print(Q1_subtract)
    Q1_current_unlisted<- c(unlist(Q1_current_port))
    #    print(Q1_current_unlisted)
    #    Q1_updated_port<- Q1_current_unlisted[!is.na(which(!(Q1_subtract %in% Q1_current_unlisted)))]
    Q1_updated_port<- setdiff(Q1_current_unlisted, Q1_subtract)
    if (length(Q1_updated_port) == 0){
      Q1_updated_port <- Q1_current_unlisted
    }
    print(Q1_updated_port)
    Q1_adds <- Q1_string_new[!is.na(which(!(Q1_string_new %in% c(unlist(Q1_updated_port)))))]
    #    print(Q1_adds)
    Q1_current_port<- append(Q1_updated_port, Q1_adds)
    
    quintiles_data$Q1_port_clean[i] <- list(unique(c(Q1_current_port)))
    
    Q5_string<- quintiles_data$Q5_clean[i]
    Q5_string_new<- strsplit(Q5_string[[1]], " ")[[1]]
    Q5_subtract<- c(unlist(quintiles_data$Q5_port_clean[[(i - duration)]]))
    Q5_current_unlisted<- c(unlist(Q5_current_port))
    #    Q5_updated_port<- Q5_current_unlisted[!is.na(which(!(Q5_subtract %in% Q5_current_unlisted)))]
    Q5_updated_port<- setdiff(Q5_current_unlisted, Q5_subtract)
    if (length(Q5_updated_port) == 0){
      Q5_updated_port <- Q5_current_unlisted
    }
    
    Q5_adds <- Q5_string_new[!is.na(which(!(Q5_string_new %in% c(unlist(Q5_updated_port)))))]
    
    Q5_current_port<- append(Q5_updated_port, Q5_adds)
    quintiles_data$Q5_port_clean[i] <- list(unique(c(Q5_current_port)))
    
  }
}


###### now import fama french data and combine the DF ##############

###### create a dataframe with the returns data for each month in sim_data #####

#### note for the file size data comparing Q3 and Q5 #######


##### create a dataframe with Q1 and Q5 returns ##########
##### run the loop here ####### 
# initialize two empty matrices to take the data
port_return <- matrix(, nrow = nrow(quintiles_data), ncol = 2)
#Q5_port_return <- matrix(, nrow = nrow(sim_data), ncol = 1)

for (i in 1:nrow(quintiles_data)){
  port_calc_date<- as.character(quintiles_data$port_calc_date[i])
  print(port_calc_date)
#  string_Q1<- c(unlist(quintiles_data$Q1_port_clean[i]))
  #  string_Q1<- c(quintiles_data$Q1_clean[i])
  #  print(string_Q1[[1]])
  #  new_string_Q1<- strsplit(string_Q1[[1]], " ")[[1]]
  #  print(new_string_Q1)
#  string_Q5<- c(unlist(quintiles_data$Q5_port_clean[i]))  been using this
  string_Q5<- c(unlist(quintiles_data$Q5_clean[i]))
  #  print(string_Q5)
  #  new_string_Q5<- strsplit(string_Q5[[1]], " ")[[1]]
  #  print(new_string_Q5)
  string_Q1<- c(unlist(quintiles_data$Q1_clean[i]))
  ### call port return function ######
  port_return[i,1] <- as.numeric(one_month_port_return(c(string_Q1), port_calc_date))
  port_return[i,2] <- as.numeric(one_month_port_return(c(string_Q5), port_calc_date))
  #  port_return[i,1] <- as.numeric(one_month_port_return(as.character(new_string_Q1), port_calc_date))
  #  port_return[i,2] <- as.numeric(one_month_port_return(as.character(new_string_Q5), port_calc_date))
  #  portfolio_filler(port_return_data)
}

#### testing 


#### convert matrix into a dataframe
port_return_DF <- data.frame(port_return)
colnames(port_return_DF) <- c("Q1_return", "Q5_return")
print(port_return_DF)
mean(port_return_DF$Q1_return)
mean(port_return_DF$Q5_return)

###### read in fremch fama data #############################################

#french_fama <- read.csv("F_F_Research_Data_Factors.CSV", header = TRUE)
french_fama <- read.table("F_F_Research_Data_Factors.txt", header = TRUE)

head(french_fama)
tail(french_fama)
str(french_fama)

## format in French Fama data is 192601 for Jan 1926

#### convert integer date (YYYYmm) to yearmon class (month year)
french_fama$Date <- as.yearmon(as.character(french_fama$Date), "%Y%m")

### figure out he begin and end row for french fama data to match sim_data dataframe months
id_month_row_start<- which(french_fama$Date == begin_month)
id_month_row_end<- which(french_fama$Date == end_month)

#### subset french_fama data to start from begin date in sim_data and end date in sim_data
returns_dataframe<- french_fama[id_month_row_start:id_month_row_end,]

head(returns_dataframe)
tail(returns_dataframe)

### reset the index(rownames) for the returns_dataframe subset ###########
rownames(returns_dataframe) <- seq(length=nrow(returns_dataframe))

### Now combine the Q1 and Q5 portfolio returns with the fremnch-fama dataframe
#### add portfolio returns (port_return_DF) to french-fama dataframe (returns_dataframe)

combined_dataframe <- cbind(returns_dataframe, port_return_DF)

##### create Q1_adj_return and Q5_adj_return columns in combined_dataframe
## Adjusted return = port return -RF (risk free rate)

combined_dataframe$Q1_adj_return <- combined_dataframe$Q1_return -combined_dataframe$RF
combined_dataframe$Q5_adj_return <- combined_dataframe$Q5_return -combined_dataframe$RF

#### Check ####
print(combined_dataframe)

#### compute means of the adjusted returns

mean(combined_dataframe$Q1_adj_return)
mean(combined_dataframe$Q5_adj_return)
mean(combined_dataframe$Q5_adj_return -combined_dataframe$Q1_adj_return)

#### write completed DF into a CSV file
write.csv(combined_dataframe, file = "combined_DF_files_N_POSNEG.csv")
saveRDS(combined_dataframe, file = "n_POSNEG.rds")
# Restore the object
#readRDS(file = "my_data.rds")

##### recovering data

combined_dataframe<- read.csv(file = "combined_DF_files_N_POSNEG.csv")
str(combined_dataframe)

combined_dataframe$Q1_return <- 100* (combined_dataframe$Q1_return)
combined_dataframe$Q5_return <- 100* (combined_dataframe$Q5_return)
combined_dataframe$Q1_adj_return <- (combined_dataframe$Q1_return) - combined_dataframe$RF
combined_dataframe$Q5_adj_return <- (combined_dataframe$Q5_return) - combined_dataframe$RF
combined_dataframe$Q1Q5_adj_return <- (combined_dataframe$Q5_return - combined_dataframe$Q1_return)- combined_dataframe$RF



##### Now create linear regression model for Q1 portfolio 

linear_model_Q1<- lm(Q1_adj_return ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q1)

sink("summaryQ1_N_POSNEG_2.txt")
summary(linear_model_Q1)
sink()

plot(combined_dataframe$Date, combined_dataframe$Q1_adj_return)


##### Now create linear regression model for Q5

linear_model_Q5<- lm(Q5_adj_return ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5)

sink("summaryQ5_N_POSNEG_2.txt")
summary(linear_model_Q5)
sink()

plot(combined_dataframe$Date, combined_dataframe$Q5_adj_return)

##### Now create linear regression model for Q5-Q1

linear_model_Q5Q1<- lm((Q5_adj_return -Q1_adj_return) ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5Q1)

sink("summaryQ5Q1_N_POSNEG.txt")
summary(linear_model_Q5Q1)
sink()

##### Now create linear regression model for Q5-Q1

linear_model_Q1Q5<- lm(Q1Q5_adj_return ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5Q1)

sink("summaryQ5Q1_N_POSNEG2.txt")
summary(linear_model_Q5Q1)
sink()

linear_model_Q5Q1_2<- lm((Q5_adj_return -Q1_adj_return) ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5Q1_2)

sink("summaryQ5Q1_cosine2.txt")
summary(linear_model_Q5Q1)
sink()


####### paired t test on means
t.test(combined_dataframe$Q1_adj_return, combined_dataframe$Q5_adj_return, paired=TRUE) 
t.test(combined_dataframe$Q1_return, combined_dataframe$Q5_return, paired=TRUE) 
t.test(combined_dataframe$Q1Q5_adj_return, combined_dataframe$RF, paired=TRUE) 


###### Modeling ends here ###########################













