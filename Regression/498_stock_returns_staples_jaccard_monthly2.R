# Stuart Muter
# Predict 498
# Capstone Assignment
# Stock & portfolio return calculation 

#10/20/17
##
##



# If necessary, install packages
install.packages("psych")
install.packages("ggplot2")
install.packages("ElemStatLearn")
install.packages("multilevel")
install.packages("lsr")
install.packages("xlsx")
install.packages("XML")
install.packages("data.table") 
install.packages("plyr")
install.packages("bsts")
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
install.packages("party")
install.packages("randomForest")
install.packages("dyn")
install.packages("Ecdat")
install.packages("fGarch")
install.packages("copula")
install.packages("quantmod")
install.packages("VineCopula")
install.packages("tseries")
install.packages("rgl")
install.packages("rugarch")
install.packages("Matrix")
install.packages("quadprog")
install.packages("quantmod")
install.packages("tidyquant")
install.packages("rowr")
install.packages("mondate")

# Load packages
library(psych)
library(ggplot2)
library(multilevel)
library(lsr)
library(xlsx)
library(XML)
library(data.table) 
library(plyr)
library(bsts)
library(reshape2)
library(zoo)
library(pscl) 
library(rpart)
library(fma)
library(forecast)
library(car)
library(MASS)
library(TTR)
library(lubridate)
library(DataCombine)
library(party)
library(Matrix)
library(Ecdat)
library(rowr)
library(mondate)




###### Read in the data ################################################

### list of stock tickers to read in for staples universe  #########################################
symbols <- c("GIS", "KR", "MKC", "SJM", "EL", "HRL", "HSY", "K", "KHC", 
             "KMB", "MDLZ", "MNST", "PEP", "PG", "PM", "SYY", "TAP", "TSN", "WBA", "WMT")



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
  dat2 <- dat[, c('timestamp', symbols[i])]
  if (i <2){
    stock_data<- dat2
  } else{
    stock_data <- cbind.fill(stock_data, dat2[2], fill = NA)
  }
}

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

# compute difference of log stock prices (log differences), need to get FF RF for
# excess return calculation
#stocks_diff = as.data.frame(100*apply(log(stocks_subset), 2, diff) - FF_data_3$RF) # Excess returns
stocks_log_prices <- as.data.frame(apply(stock_data2[,2:ncol(stock_data2)], 2, log))
symbols_log <- lapply(symbols, function(x) paste0(x,"_logprice"))

#add names to stocks_log_prices
names(stocks_log_prices) <- symbols_log
# Check
head(stocks_log_prices)

# Apply the difference function to compute log differences
stocks_log_diff <- as.data.frame(apply(stocks_log_prices, 2, diff))

# add names to stocks_log_diff
symbols_log_diff <- lapply(symbols, function(x) paste0(x,"_log_diff"))
names(stocks_log_diff) <- symbols_log_diff

# Check
head(stocks_log_diff)
tail(stocks_log_diff)

# Add back the timestamp/date
stocks_log_diff_2 <- cbind(stock_data2$timestamp[-1], stocks_log_diff)
names(stocks_log_diff_2) <- c('timestamp',symbols_log_diff)

# check
head(stocks_log_diff_2)
print(stocks_log_diff_2)
print(tail(stocks_log_diff_2))
#print(stocks_log_diff_2[140:145,])



### Now create functions to return a cumulative return.
## First create function to compute return of a SINGLE stock
## arguments = stock ticker and date (month ending date)
## returns the stock return for that month (so filing occured in the month before)

#### 1 month return function  #######
## arguments = stock ticker and date (month ending date)
## returns the stock return for that month (so filing occured in the month before)
one_month_return <- function(stock_ticker, return_date) { 
  file_row<- which(stocks_log_diff_2 == return_date)
  begin_row <- file_row 
  end_one_month_row <- file_row 
  column_name_end <- c('_log_diff')
  col_name <-  paste0(stock_ticker, column_name_end)
  id_col<- which(names(stocks_log_diff_2) == col_name)
  sum_one<- sum(stocks_log_diff_2[begin_row:begin_row, id_col])
  exp_one <- expm1(sum_one) 
  return(exp_one)
}


### check function
one_month_return('KR', '2014-06-30')


##### Write portfolio return function   ########
### equal weighted portfolio return from stock returns
#### one month portfolio return function #####
### given ticker list and month the portfolio is active,  returns equal weighted portfolio return for that month
### This function calls the stock return function for all stocks in a list and computes and equal weighted
### return (average return) for the portfolio. 
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

#### test/check this function #######

test_tickers = c("PEP","TSN", "KR")
test_date <- c('2013-07-31')

port_return<- one_month_port_return(test_tickers, test_date)
print(port_return)


### Using this. This is the output from Reed/Michelle scraping and quintile sorting. 
#### import monthly Quintile rankings data  module #######

quintiles_data <- read.csv("Stuart2transposedJacard.csv", header = TRUE)

## Look at the data
print(quintiles_data)
tail(quintiles_data)
str(quintiles_data)


### change date into yearmon and convert to the last day of the month
quintiles_data$Date <- as.Date(quintiles_data$Date, format = "%B %d %Y")
quintiles_data$Date <- LastDayInMonth(quintiles_data$Date)

####### Index the date forward by a month. The portfolio was created on the last day of the month
#### so need to get returns for the FOLLOWING MONTH 

quintiles_data$port_calc_date<-  as.Date(as.mondate(quintiles_data$Date) + 1)

###3 right now Fama frenchdata only goes to september 2017, so trim portfolio
quintiles_data<- quintiles_data[1:80,]

### get beginnining and ending month of the similarity data, which we will need
## later to match up fama french date when we combine the two datasets
begin_month <- as.yearmon(quintiles_data$port_calc_date[1])
end_month <- as.yearmon(quintiles_data$port_calc_date[nrow(quintiles_data)])

#print(LastDayInMonth(as.Date(sim_data$Date[1])))

#### Loop through the data dataframe to prep data as character
quintiles_data$Q1_clean <- lapply(quintiles_data$Q1, as.character)
quintiles_data$Q5_clean <- lapply(quintiles_data$Q5, as.character)


####### portfolio generator code #######################################

#### Needs to be indexed forward by one month (i + 1), which we did in 
## quintiles_data with port_calc date variable (variable that used to calc
### the return for that month)


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


###### check ###########
print(quintiles_data)
str(quintiles_data)

#### we have some multiple rows for the same month and have to trim the data to match fama french (one
#### unique row per month)

### will pick the last row for multiple month
### need to delete in quintiles data: row 8, 20, 33, 45, 58, 70
row_delete<- c(8, 20, 33, 45, 58, 70)
quintiles_data <- quintiles_data[-row_delete, ]
print(quintiles_data)

### reset the index(rownames) for the trimmed quintiles_data ###########
rownames(quintiles_data) <- seq(length=nrow(quintiles_data))
print(quintiles_data)


##################################################

##### link quintiles_data portfolios (list of stocks) to the output of the portfolio generator 
#### to get the returns for the created portfolios


###### create a dataframe with the returns data for each month in sim_data #####
##### create a dataframe with Q1 and Q5 returns ##########
##### run the loop here ####### 
# initialize two empty matrices to take the data
port_return <- matrix(, nrow = nrow(quintiles_data), ncol = 2)
#Q5_port_return <- matrix(, nrow = nrow(sim_data), ncol = 1)

for (i in 1:nrow(quintiles_data)){
  port_calc_date<- as.character(quintiles_data$port_calc_date[i])
  print(port_calc_date)
  string_Q1<- c(unlist(quintiles_data$Q1_port_clean[i]))
#  string_Q1<- c(quintiles_data$Q1_clean[i])
#  print(string_Q1[[1]])
#  new_string_Q1<- strsplit(string_Q1[[1]], " ")[[1]]
#  print(new_string_Q1)
  string_Q5<- c(unlist(quintiles_data$Q5_port_clean[i]))
#  string_Q5<- c(quintiles_data$Q5_clean[i])
#  print(string_Q5)
#  new_string_Q5<- strsplit(string_Q5[[1]], " ")[[1]]
#  print(new_string_Q5)
### call port return function ######
  port_return[i,1] <- as.numeric(one_month_port_return(c(string_Q1), port_calc_date))
  port_return[i,2] <- as.numeric(one_month_port_return(c(string_Q5), port_calc_date))
#  port_return[i,1] <- as.numeric(one_month_port_return(as.character(new_string_Q1), port_calc_date))
#  port_return[i,2] <- as.numeric(one_month_port_return(as.character(new_string_Q5), port_calc_date))
#  portfolio_filler(port_return_data)
}

#### checking
print(port_return)

#### convert matrix into a dataframe & look at it
port_return_DF <- data.frame(port_return)
colnames(port_return_DF) <- c("Q1_return", "Q5_return")
print(port_return_DF)
mean(port_return_DF$Q1_return)
mean(port_return_DF$Q5_return)

###### read in fremch fama data to run the factor analysis on the computed portfolio return #############################################

#french_fama <- read.csv("F_F_Research_Data_Factors.CSV", header = TRUE)
french_fama <- read.table("F_F_Research_Data_Factors.txt", header = TRUE)

head(french_fama)
tail(french_fama)
str(french_fama)

## format in French Fama data is 192601 for Jan 1926

#### convert integer date (YYYYmm) to yearmon class (month year)
french_fama$Date <- as.yearmon(as.character(french_fama$Date), "%Y%m")

### figure out he begin and end row for french fama data to match quintiles_data dataframe monthly rows
id_month_row_start<- which(french_fama$Date == begin_month)
id_month_row_end<- which(french_fama$Date == end_month)

#### subset french_fama data to start from begin date in quintiles_data and end date in quintiles_data
returns_dataframe<- french_fama[id_month_row_start:id_month_row_end,]

head(returns_dataframe)
tail(returns_dataframe)

print(returns_dataframe)

### reset the index(rownames) for the returns_dataframe subset ###########
rownames(returns_dataframe) <- seq(length=nrow(returns_dataframe))

### Now combine the Q1 and Q5 portfolio returns with the fremnch-fama dataframe, so we can regress
#### add portfolio returns (port_return_DF) to french-fama dataframe (returns_dataframe)

combined_dataframe <- cbind(returns_dataframe, port_return_DF)

##### create Q1_adj_return and Q5_adj_return columns in combined_dataframe
## Adjusted return = port return -RF (risk free rate)

combined_dataframe$Q1_adj_return <- 100*combined_dataframe$Q1_return -combined_dataframe$RF
combined_dataframe$Q5_adj_return <- 100*combined_dataframe$Q5_return -combined_dataframe$RF
combined_dataframe$Q5Q1_adj_return <- combined_dataframe$Q5_adj_return - combined_dataframe$Q1_adj_return
combined_dataframe$Q5Q1_adj_return_2 <- (combined_dataframe$Q5_return - combined_dataframe$Q1_return) - combined_dataframe$RF
#### Check ####
print(combined_dataframe)

#### compute means of the adjusted returns

mean(combined_dataframe$Q1_adj_return)
mean(combined_dataframe$Q5_adj_return)

#### write completed DF into a CSV file
write.csv(combined_dataframe, file = "combined_DF_jacard3.csv")

##### recovering data
combined_dataframe<- read.csv(file = "combined_DF_jacard2.csv")
str(combined_dataframe)

##### Now create linear regression model for Q1 portfolio 

linear_model_Q1<- lm(Q1_adj_return ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q1)

sink("summaryQ1jaccard3.txt")
summary(linear_model_Q1)
sink()

plot(combined_dataframe$Date, combined_dataframe$Q1_adj_return)


##### Now create linear regression model for Q5

linear_model_Q5<- lm(Q5_adj_return ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5)

sink("summaryQ5jaccard3.txt")
summary(linear_model_Q5)
sink()

plot(combined_dataframe$Date, combined_dataframe$Q5_adj_return)

linear_model_Q5Q1<- lm(Q5Q1_adj_return_2 ~ Mkt.RF + SMB + HML, data = combined_dataframe)

summary(linear_model_Q5Q1)

sink("summaryQ5Q1jaccard3.txt")
summary(linear_model_Q5Q1)
sink()

####### paired t test on means
t.test(combined_dataframe$Q1_adj_return, combined_dataframe$Q5_adj_return, paired=TRUE) 
t.test(combined_dataframe$Q1_return, combined_dataframe$Q5_return, paired=TRUE) 
t.test(combined_dataframe$Q1Q5_adj_return, combined_dataframe$RF, paired=TRUE) 

###### Modeling ends here ###########################

####### END ##############################################


