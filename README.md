# SGStocksBot - Singapore Stock Market Telegram Bot

![SGStocksBot](https://github.com/user-attachments/assets/baac9cf1-f8bc-4702-9c92-8f435806f02a)

A comprehensive Telegram bot that provides real-time Singapore stock market information, dividend analysis, technical indicators, and financial news. The bot serves as a one-stop virtual assistant for investors interested in the Singapore Exchange (SGX).

# Features
## Stock Information
- Real-time stock quotes with price changes and percentages
- Day range (high/low), 52-week range
- Bid/ask prices with volumes
- Total trading volume
- Fuzzy name search for stocks and bonds

![info2](https://github.com/user-attachments/assets/ad960529-fc4c-4ef8-9a9f-b9cb1e8afa83)

## Dividend Analysis
- Current dividend yield based on previous year's dividends
- 5-year dividend history with ex-dates and pay dates
- Dividend calculator for specific time periods
- Upcoming dividend/corporate actions calendar
- Top dividend-yielding securities by category (Blue Chips, REITs, Business Trusts, Bonds, ETFs)

![div](https://github.com/user-attachments/assets/9b2ac16b-72b6-4a7e-bc08-17d7cf61b0a7)
![divrank2](https://github.com/user-attachments/assets/57c5c93c-3fdd-4bc7-9bf1-1e6fc1295e6f)

## Technical Analysis
- Trend analysis with customizable lookback periods
- Linear regression trendlines
- Standard deviation bands (1/2 and 1 standard deviation)
- Visual price charts with technical indicators
- Overall trend direction (Up/Down)

![trend1](https://github.com/user-attachments/assets/17fafc43-50e3-44e3-804d-bdb954e7b6c1)

## News & Updates
- Latest Singapore financial news from major sources
- Real-time market updates

![news](https://github.com/user-attachments/assets/e4470deb-19f1-4e3a-8ed8-961140e7c429)

# Commands
| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and command list | `/start` |
| `/info [name/code]` | Get basic stock/bond information | `/info DBS` or `/info D05` |
| `/div [code]` | View dividend yield and 5-year history | `/div D05` |
| `/divsum [code, start, end, shares]` | Calculate dividend collection for a period | `/divsum D05, 2015, 2020, 1000` |
| `/updiv` | View upcoming dividends/corporate actions | `/updiv` |
| `/divrank` | Top 8 highest dividend yields by category | `/divrank` |
| `/news` | Recent Singapore financial news | `/news` |
| `/trend [code, years]` | Technical trend analysis with chart | `/trend D05, 3` |
| `/support` | Support the project via PayLah | `/support` |


# Technology Stack
- Python 3.7+
- python-telegram-bot - Telegram bot framework
- MongoDB Atlas - Cloud database for stock metadata
- Pandas - Data manipulation and analysis
- yFinance - Yahoo Finance data retrieval
- BeautifulSoup4 - Web scraping for dividend data
- Matplotlib - Chart generation for technical analysis
- FuzzyWuzzy - Fuzzy string matching for stock name searches
- Requests - API calls to SGX and exchange rates

# Data Sources
- SGX (Singapore Exchange) - Real-time pricing data
- Yahoo Finance - Historical price data for 52-week ranges
- dividends.sg - Dividend history and upcoming dividends
- ExchangeRate-API - Currency conversion for foreign listings

# Key Functions
`stock_name(query)`

Performs fuzzy matching to find the correct stock code based on user input. Returns exact match if found, or provides multiple suggestions for close matches.

`get_stock_info(ticker)`

Retrieves real-time pricing data from SGX for both securities and retail fixed income instruments.

`get_current_div_yield(ticker, last_price)`

Scrapes dividend history and calculates current yield based on previous year's dividends.

`get_technical(ticker, lookback)`

Performs linear regression analysis on historical price data and generates trend charts with standard deviation bands.

# Error Handling
- The bot includes comprehensive error handling for:
- Invalid stock codes
- API failures
- Data source unavailability
- User input formatting errors

# Disclaimer
This bot is for informational purposes only and does not constitute financial advice. Always do your own research before making investment decisions.

# Support
If you find this bot useful, consider supporting its development via PayLah (use /support command in the bot).

# Contact
Bot Link: https://t.me/SGStocksBot

GitHub: https://github.com/chrislowjk/SGStocksBot

Blog: https://theboywhoprocrastinates.blogspot.com/2021/04/introducing-virtual-assistant-for-sg.html
