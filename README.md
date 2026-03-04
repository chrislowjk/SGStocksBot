# Telegram Bot: SGStocksBot

A one-stop virtual assistant that offers wide array of financial information relating to stock analysis for Singapore Exchange.



convert this to readme.md format. 



In order to keep myself updated on the financial information of SGX listed companies, I used to install a plethora of investment applications on my mobile device, such as Bloomberg and Yahoo Finance to name a few. 

However, it can get a little messy, often painting an incomplete picture when the information that I was searching for exists in bits and pieces from various sources. 

And that was the decisive moment that I thought of consolidating the data and building a one-stop virtual assistant to process financial information regarding Singapore stocks/bonds. 

With Telegram gaining popularity and prominence as a messaging service application, it would appear to be the ideal platform to experiment a bot that churns out financial information on the go. 

And with that comes the birth of SGStocksBot. 



# Getting access to SGStocksBot
To get started, you would need to have Telegram installed on your mobile device. Upon setting up a Telegram account, you can access to SGStocksBot via the search function,



or the following Telegram invite link: https://t.me/SGStocksBot
You will be directed to the following page in which you may click on "Start" to initiate the bot. 





# /start Command
For those who are unfamiliar with the use of Telegram bots, a bot command begins with a slash "/" followed by the supported commands. 

One of the universal commands is "/start" which initiates the conversation with the bot. At the same time, it brings up the menu of the commands available to the user. Let's go through these commands together. 




# /info Command
The info command gives the basic information of the stock / bond. To use this command, you can key in "/info" along with the name or stock code of the stock / bond that you wish to look up. 

To demonstrate using DBS stock, you can key in either "/info DBS" or "/info D05" if you have knowledge of the ticker symbol that you are searching for. 










Other than stocks, you may also search the database for other security types such as ETFs and bonds. 






# /div Command
The div command provides information regarding the current dividend yield as well as the dividend history of a particular security for the past 5 years. 

The current dividend yield is calculated based on the current price of the security and the amount of dividends issued in the previous year.

To use this command, you can key in "/div" along with the stock code of the security that you wish to look up. As the bot does not impose case sensitivity on the query, you may input the stock symbol in either uppercase or lowercase letters. 

Do note that only the info command allows name searching of securities. So you may wish to check up on the ticker symbol using the info command. 

To demonstrate using DBS stock, you can key in "/div D05" to obtain the dividend information of DBS. 




# /divsum Command
The divsum command calculates the amount of dividend that a shareholder would have collected in a defined time period based on the number of shares that he/she has owned in that particular security.

To use this command, you can key in "/divsum" along with the stock code of the security, the start and end years (inclusive) that you wish to define and the number of shares owned. 

To demonstrate using DBS stock, you can key in "/divsum D05, 2011, 2016, 1000" to derive the total amount of dividend collected with 1000 shares of DBS stock from 2011 to 2016. 

From the example below, the user is able to tell that he has collected a total of $3,460 dividend based on his 1000 shares of DBS from 2011 to 2016. Additionally, he is able to view the dividend breakdown over the years.



Using this command, the user is able to observe the track record of dividend payments for a particular security over the years. 


# /updiv Command
The updiv command allows the user to view the upcoming dividend / corporate actions for SGX listed companies.

To use this command, you can simply key in "/updiv". The bot will respond with 5 upcoming dividend payouts, ordered by recent corporate actions. 




# /divrank Command
The divrank command calculates the dividend yields for each security in specific categories and rank them accordingly.

The dividend yield is calculated based on the previous day's closing price of the security and the amount of dividends issued in the previous year.

To use this command, you can simply key in "/divrank". The bot will respond and ask for your input of choice for the category.



Upon receiving the user's input of choice, the bot will calculate the dividend yields and rank them accordingly. Here are some examples for blue chip stocks and REITs.



I had initially intended to generate the ranking using the price at time of query as input variables but this has hampered the execution of the command considerably. Therefore, I have switched to the use of previous day's closing price of the security in order to optimize the bot's performance.

One thing to take note is that dividend yield of a security is inversely related to its share price. Basing an investment decision solely on high dividends and ignoring other factors can have its implication and risk. 

For instance, First Reit has announced a rights issue in Dec 2020 to meet its debt covenants and avoid an imminent default. This has resulted in the hammering of its stock price.

Hence, investors should not be lured by the attractiveness of high dividend yields. It is imperative to understand, inter alia, the financial metrics of the company and the sustainability of the high dividend payout. 

That is not to say that all high-yield securities signify beleaguered companies in financial duress. The necessary due diligence should be carried out before committing to an investment. 



# /news Command
The news command allows the user to view the recent Singapore financial news and industry trends. 

To use this command, you can simply key in "/news". The bot will respond with the 5 pieces of financial articles, ordered by the publication date. 




# /trend Command
The trend command computes the relevant metrics for trend analysis of a security in the given lookback period. This aspect caters to the technical minds who are keen in studying the trendlines and price movement of stocks.

To use this command, you can key in "/trend" along with the stock code of the security and the number of years as lookback period.


To demonstrate using DBS stock, you can key in "/trend D05, 10" to analyze the trend data for DBS over the past 10 years.




The mean refers to the average daily stock price for the defined period (i.e. 10 years in this case). Visually, you can imagine a horizontal line cutting across the chart at 16.06. 

On top of that, users are able to create their own linear regression charts for trend analysis. 



The stock trend line refers to a linear regression line (or line of best fit) drawn through the daily stock price data. Users are able to use the long-term trend line as a gauge to determine the valuation of the security at the current price (ie. if a stock is trading above or below the regression trendline).

The inclusion of 4 standard deviation lines serves as additional metrics to quantify the degree of deviation from the main regression trendline. For example, the stock price of DBS has reached 1 standard deviation above the trendline in 2018 and fallen below 1 standard deviation from the trendline in 2016 and 2020. 

The price data for these 5 metrics represent the latest price points at the end of the chart. 

Naturally, this command offers an over-simplistic approach in determining the valuation of a particular security. Exercising the appropriate due diligence is definitely recommended. 



# /support Command
Last but not least, if you have found SGStocksBot to be useful and would like to show your appreciation, the support command allows the user to contribute and help support the running of the bot via PayLah payment link.


One last thing to note is that the bot will idle and go to sleep after 30 minutes of inactivity. So do expect the bot to take a few seconds to respond to your command if it has been more than 30 minutes since your last interaction with it. Other than that, the bot should respond almost instantaneously.

If time permits, I may roll out additional bot features/commands in the future. In the meantime, I hope you enjoy the bot and please let me know of any feedback that I can improve on it. 
