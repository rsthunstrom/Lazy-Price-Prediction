# Lazy Price Prediction
## Portfolio selection through natural language processing

PREDICT 498 - Team Members
* Bill
* Josh 
* Masae
* Stuart
* Reed


## Pipeline - Order for code

#### Web Scraping
1. SP500CoList17.py
   * Grab all tickers from S&P 500 and initial SEC URL
2. project15a.py
   * Click through SEC site and grab the URL of the 10-Qs and 10-Ks that house the text
3. FullRunAssemblyAfterInitScrape.py
   * Loop through all tickers, scrape risk factor section from URLs, and assemble a dataframe for each month

#### Simililarity Metrics
4. masterFileAssembly.py
   * Assemble a master file with all tickers, months, and risk factors.
   * Calculate similarity metrics each month, bucket tickers into quintiles, and append to master file for modeling

#### Multi linear regression modeling

* Update - Waiting for R code*
