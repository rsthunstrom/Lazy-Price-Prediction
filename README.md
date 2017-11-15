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

#### Multi-variate linear regression modeling

5. 498_stock_returns_staples_cosine_monthly3-1.R
    * Calculate stock returns for cosine similarity quintiles
  
6. 498_stock_returns_staples_jaccard_monthly2.R
    * Calculate stock returns for jacaard similarity quintiles

7. 498_stock_returns_staples_simple_monthly2-1.R
    * Calculate stock returns for simple similarity quintiles

#### Data Visualization

Visualization of portfolio selection and model can be found in the Lazy-Price-Prediction/DataVisualization folder
