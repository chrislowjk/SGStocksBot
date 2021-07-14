import logging
import os
import requests
import json
import pandas as pd
import yfinance as yf
import datetime
import re
import collections
import pytz
import statistics
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup, NavigableString, Tag
from yahoofinancials import YahooFinancials
from pandas_datareader import data as pdr
from dateutil.relativedelta import relativedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from fuzzywuzzy import process, fuzz
from pymongo import MongoClient
from bob_telegram_tools.bot import TelegramBot
from matplotlib.pyplot import figure
from telegram import InlineKeyboardButton,InlineKeyboardMarkup

yf.pdr_override()

HEADERS = {
           "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
           "Origin": "**",
           "Referer": "**"}
		   
TOKEN = '**'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', 5000))

db_url = f'mongodb+srv://***@cluster0.qcqbq.mongodb.net/test?authSource=admin&replicaSet=atlas-10lob9-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true'


def check_stock_quote(code):

    client = MongoClient(db_url)
    security = client['SGX']['security']
    
    if (security.find({'Stock Code': code.upper()}).count()) == 0:
        result = 0
    else:
        result = 1
        
    return result

def stock_name(query): 

    client = MongoClient(db_url)
    security = client['SGX']['security']
    
    if check_stock_quote(query):
        for i in security.find():
            if i['Stock Code'] == query.upper():
                output = {'Security': i['Security'], 'Stock Code': i['Stock Code']}
    else:
        name = []
        for i in security.find():
            name.append(i["Security"])

        match_subset = process.extract(query,name)

        ratio = []
        partial = []
        total = []

        for i in match_subset:
            fuzz_ratio = fuzz.ratio(i[0].lower(),query.lower())
            partial_ratio = fuzz.partial_ratio(i[0].lower(),query.lower())

            ratio.append(fuzz_ratio)
            partial.append(partial_ratio)
            total.append(fuzz_ratio + partial_ratio)

        max_score = max(total)
        shortlist = [i for i,j in enumerate(total) if j == max_score]

        stock_list = []

        if len(shortlist) > 1:
            stock_list.append(match_subset[shortlist[0]])
            stock_list.append(match_subset[shortlist[1]])
        else:
            stock = match_subset[total.index(max(total))][0]

        output_list = []
        code_list = []
        output = {}

        if not stock_list:
            for i in security.find():
                if i['Security'] == stock:
                    output = {'Security': i['Security'], 'Stock Code': i['Stock Code']}
        else:
            for i in security.find():
                for k in stock_list:
                    if i['Security'] == k[0]:
                        output_list.append(i['Security'])
                        code_list.append(i['Stock Code'])                
                output = {'Security': output_list, 'Stock Code':code_list}
            
    return output

def get_stock_info(ticker): 
    
    #Securities
    req = requests.get(
                "**",
                headers=HEADERS)
    
    data = json.loads(req.text)['data']
    df_stock = pd.DataFrame(data['prices'])
    df_stock = df_stock.rename(
            columns={'b': 'Bid',
                     'lt': 'Last',
                     'bv': 'Bid_Volume',
                     'c': 'Change',
                     'sv': 'Ask_volume',
                     'h': 'High',
                     'l': 'Low',
                     'o': 'open',
                     'p': 'Change_percent',
                     's': 'Ask',
                     'vl': 'Volume',
                     'nc': 'Stock_code'}
            )

    #Retail Fixed Income
    req1 = requests.get("**",
                        headers=HEADERS)
    data1 = json.loads(req1.text)['data']
    df_bond = pd.DataFrame(data1['prices'])
    df_bond = df_bond.rename(
            columns={'b': 'Bid',
                     'lt': 'Last',
                     'bv': 'Bid_Volume',
                     'c': 'Change',
                     'sv': 'Ask_volume',
                     'h': 'High',
                     'l': 'Low',
                     'o': 'open',
                     'p': 'Change_percent',
                     's': 'Ask',
                     'vl': 'Volume',
                     'nc': 'Stock_code'}
            )

    df = pd.concat([df_stock,df_bond])
    
    last_price = df['Last'][df['Stock_code'] == ticker].values[0]
    change = df['Change'][df['Stock_code'] == ticker].values[0]
    per_change = df['Change_percent'][df['Stock_code'] == ticker].values[0]
    open_price = df['open'][df['Stock_code'] == ticker].values[0]
    day_low = df['Low'][df['Stock_code'] == ticker].values[0]
    day_high = df['High'][df['Stock_code'] == ticker].values[0]
    
    bid_price = df['Bid'][df['Stock_code'] == ticker].values[0]
    bid_vol = df['Bid_Volume'][df['Stock_code'] == ticker].values[0]
    ask_price = df['Ask'][df['Stock_code'] == ticker].values[0]
    ask_vol = df['Ask_volume'][df['Stock_code'] == ticker].values[0]
    total_vol = df['Volume'][df['Stock_code'] == ticker].values[0]
    
    return last_price, change, per_change, open_price, day_low, day_high, bid_price, bid_vol, ask_price, ask_vol, total_vol

def get_52_weeks(ticker):
    
    end = datetime.datetime.now()
    start = datetime.datetime.now() - relativedelta(years=1)
    
    try:
        low_52 = round(min(pdr.get_data_yahoo(ticker, start, end)["Low"]),3)
        high_52 = round(max(pdr.get_data_yahoo(ticker, start, end)["High"]),3)
    except:
        low_52 = "N/A"
        high_52 = "N/A"
    
    return low_52, high_52

def get_current_div_yield(ticker,last_price): 
    
    url = '**'

    html = requests.get(url, headers = {'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table table-bordered table-striped'})

    tmp = table.find_all('tr')
    first = tmp[0]
    allRows = tmp[1:]
    headers = [header.get_text() for header in first.find_all('th')]
    results = [[data.get_text() for data in row.find_all('td')] for row in allRows]
    
    for i in range(len(results)):
        if len(results[i]) < 5:
            results[i].insert(0,results[i-1][0])
            results[i].insert(1,0)
            results[i].insert(2,0)

    # Remove \t\t
    for i in results:
        i[3] = i[3].rstrip("\t\t")
        i[5] = i[5].rstrip("\t\t")

    df = pd.DataFrame(data=results, columns=headers)
    df_unaltered = pd.DataFrame(data=results, columns=headers)

    currency = []
    for i in range(len(df)):
        if df['Amount'][i] != '-':
            currency.append(re.findall(r'[A-Za-z]+|\d+', df['Amount'][i])[0])

    counter = collections.Counter(currency)
    dominant_currency = counter.most_common(1)[0][0]

    # Remove currency from Amount
    for i in range(len(df)):
        if df['Amount'][i] == '-':
            df['Amount'][i] = 0
        elif dominant_currency not in df_unaltered['Amount'][i]:
            df_unaltered = df_unaltered.drop(i)
            df['Amount'][i] = 0
        else:
            df['Amount'][i] = float(re.findall("\d+\.\d+", df['Amount'][i])[0])
        
    current_yr = datetime.datetime.today().year
    prev_yr = current_yr - 1
    last_5_yr = current_yr - 5

    df_unaltered = df_unaltered.reset_index()
    
    prev_yr_div = round(df['Amount'][df["Year"] == str(prev_yr)].sum(),4)
    current_div_yield = round(prev_yr_div / last_price * 100,2)
    
    return df_unaltered, last_5_yr, prev_yr, current_div_yield  

def calc_div_sum(ticker, start, end, no):

    url = '**'

    html = requests.get(url, headers = {'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table table-bordered table-striped'})

    tmp = table.find_all('tr')
    first = tmp[0]
    allRows = tmp[1:]
    headers = [header.get_text() for header in first.find_all('th')]
    results = [[data.get_text() for data in row.find_all('td')] for row in allRows]

    for i in range(len(results)):
        if len(results[i]) < 5:
            results[i].insert(0,results[i-1][0])
            results[i].insert(1,0)
            results[i].insert(2,0)

    for i in results:
        i[3] = i[3].rstrip("\t\t")
        i[5]= i[5].rstrip("\t\t")

    df = pd.DataFrame(data=results, columns=headers)

    currency = []
    for i in range(len(df)):
        if df['Amount'][i] != '-':
            currency.append(re.findall(r'[A-Za-z]+|\d+', df['Amount'][i])[0])

    counter = collections.Counter(currency)
    dominant_currency = counter.most_common(1)[0][0]

    for i in range(len(df)):
        if df['Amount'][i] == '-':
            df['Amount'][i] = 0
        elif dominant_currency not in df['Amount'][i]:
            df['Amount'][i] = 0
        else:
            df['Amount'][i] = float(re.findall("\d+\.\d+", df['Amount'][i])[0])
            
    start_year = datetime.datetime(start,1,1)
    end_year = datetime.datetime(end,1,1)        
    
    year_list = range(start_year.year, end_year.year+1)
    div_list = []
    
    for year in year_list:
        div_list.append(round(df['Amount'][df["Year"] == str(year)].sum(),4))
        
    total_div = round(sum(div_list),4) * no
    total_div = dominant_currency + " " + "{:.2f}".format(total_div)
    
    return total_div, year_list, div_list, dominant_currency

def get_upcoming_dividend():
    
    url = '**'

    html = requests.get(url, headers = {'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'table table-condensed small'})

    tmp = table.find_all('tr')
    first = tmp[0]
    allRows = tmp[1:11]
    headers = [header.get_text() for header in first.find_all('th')]
    results = [[data.get_text() for data in row.find_all('td')] for row in allRows]

    while("" in headers) : 
        headers.remove("") 

    for line in results: 
        line.pop(0)
        while("" in line) : 
            line.remove("") 

    df = pd.DataFrame(data=results, columns=headers)

    for i in range(len(df)):
        if "Cash Options" in df["Detail"][i]:

            url2 = '**'
            html2 = requests.get(url2, headers = {'User-agent': 'Mozilla/5.0'}).text
            soup2 = BeautifulSoup(html2, 'html.parser')
            table2 = soup2.find_all('table', {'class': 'table table-bordered table-striped'})[-1]
            tmp2 = table2.find_all('tr')
            first2 = tmp2[0]
            allRows2 = tmp2[1:]
            headers2 = [header.get_text() for header in first2.find_all('th')]
            results2 = [[data.get_text() for data in row.find_all('td')] for row in allRows2]

            df2 = pd.DataFrame(data=results2, columns=headers2)
            code = df["Stock / REIT"][i].split(":")[-1].split(")")[0]

            for j in range(len(df2)):
                if code in df2["Company"][j]:
                    df["Detail"][i] = df2["Amount"][j]

    return df

def get_news():
    
    url = '**'

    html = requests.get(url, headers = {'User-agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', {'id': 'articlelist'})

    title_list = []
    link_list = []
    time_list = []
    counter = 0

    for row in table:
        if isinstance(row, NavigableString):
            continue
        if isinstance(row, Tag):
            link = row.get('href')
            title = row.get('title').split(" | ")[0]
            if "businesstimes" in link:
                title_list.append(title)
                link_list.append(link)
                time_list.append(row.find('div', {'class': 'updatedsgtime'}).text)
                counter += 1
                if counter > 4:
                    break
    
    return title_list, link_list, time_list

def linreg(X, Y):

    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in zip(X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    return (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

def excel_date(date):
    temp = datetime.datetime(1899, 12, 30)
    delta = date - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

def get_technical(ticker, lookback):
    end = datetime.datetime.now()
    start = datetime.datetime.now() - relativedelta(years=lookback)

    stock = pdr.get_data_yahoo(ticker + '.SI', start, end)['Adj Close'].dropna()
    stock_mean = stock.mean()

    #daily
    p = stock.index.to_pydatetime()
    u = [excel_date(i) for i in p]
    sd = statistics.stdev(stock.values)
    a,b = linreg(u,stock.values)
    extrapolatedtrendline=[a*index + b for index in u]
    
    trendline = extrapolatedtrendline[-1]
    sd1 = [i + sd for i in extrapolatedtrendline] 
    sdhav = [i + 0.5*sd for i in extrapolatedtrendline] 
    sdneghav = [i - 0.5*sd for i in extrapolatedtrendline] 
    sdneg1 = [i - sd for i in extrapolatedtrendline]

    if (sd1[0] < sd1[-1]):
        trend = "Up"
    else:
        trend = "Down"

    figure(num=None, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(stock.index, stock.values)

    plt.plot(stock.index, sdneg1, label="1 Standard Deviation below Mean", color = 'black')
    plt.plot(stock.index, sdneghav, label="1/2 Standard Deviation below Mean", color='green')
    plt.plot(stock.index, extrapolatedtrendline, "r--", label='Trendline')
    plt.plot(stock.index, sdhav, label="1/2 Standard Deviation above Mean",color='green')
    plt.plot(stock.index, sd1, label="1 Standard Deviation above Mean", color = 'black')

    plt.legend()

    return stock_mean, trendline, sdhav, sd1, sdneghav, sdneg1, trend,plt

def get_div_blue():

   client = MongoClient(db_url)
    bluechips = client['SGX']['dividend_bluechips']

    resp_thb = requests.get('https://v6.exchangerate-api.com/v6/**/pair/SGD/THB')
    THB = resp_thb.json()["conversion_rate"]

    resp_usd = requests.get('https://v6.exchangerate-api.com/v6/**/pair/USD/SGD')
    USD = resp_usd.json()["conversion_rate"]
    
    stock = []
    div = []
    price = []

    for i in bluechips.find({}):
        stock.append(i['Stock Code'])
        div.append(i['2020 Dividend'])
        price.append(i['Price'])

    divy=[]

    for i, j, k in zip(stock, div, price):
        if i == "Y92":
            divy.append(round((j/THB)/k*100,2))
        elif i == "C07":
            divy.append(round((j*USD)/k*100,2))
        else:
            divy.append(round(j/k*100,2))
            
    divy_sort_index = sorted(range(len(divy)), key=lambda i: divy[i], reverse=True)[:8]

    divy_sort= []
    identifier = []

    for i in divy_sort_index:
        divy_sort.append(divy[i]) 
        identifier.append(stock[i])
        
    name_sorted = []
    stock_sorted = []

    for i in identifier:
        for j in bluechips.find({"Stock Code": i}):
            name_sorted.append(j['Name'])
            stock_sorted.append(j['Stock Code'])
        
    return name_sorted, stock_sorted, divy_sort

def get_div_reits():

	client = MongoClient(db_url)
    reits = client['SGX']['dividend_reit']
        
    stock = []
    div = []
    price = []

    for i in reits.find({}):
        stock.append(i['Stock Code'])
        div.append(i['2020 Dividend'])
        price.append(i['Price'])

    divy=[]

    for i, j, k in zip(stock, div, price):
        divy.append(round(j/k*100,2))
            
    divy_sort_index = sorted(range(len(divy)), key=lambda i: divy[i], reverse=True)[:8]

    divy_sort= []
    identifier = []

    for i in divy_sort_index:
        divy_sort.append(divy[i]) 
        identifier.append(stock[i])
        
    name_sorted = []
    stock_sorted = []

    for i in identifier:
        for j in reits.find({"Stock Code": i}):
            name_sorted.append(j['Name'])
            stock_sorted.append(j['Stock Code'])
            
    return name_sorted, stock_sorted, divy_sort

def get_div_bt():

    client = MongoClient(db_url)
    bts = client['SGX']['dividend_business_trusts']

    resp_usd = requests.get('https://v6.exchangerate-api.com/v6/**/pair/USD/SGD')
    USD = resp_usd.json()["conversion_rate"]

    resp_hkd = requests.get('https://v6.exchangerate-api.com/v6/**/pair/HKD/SGD')
    HKD = resp_hkd.json()["conversion_rate"]
  
    stock = []
    div = []
    price = []

    for i in bts.find({}):
        stock.append(i['Stock Code'])
        div.append(i['2020 Dividend'])
        price.append(i['Price'])

    divy=[]

    for i, j, k in zip(stock, div, price):
        if i == "D8DU":
            divy.append(round((j*USD)/k*100,2))
        elif i == "P7VU":
            divy.append(round((j*HKD)/k*100,2))            
        elif i == "NS8U":
            divy.append(round((j/(USD/HKD))/k*100,2))            
        else:
            divy.append(round(j/k*100,2))
            
    divy_sort_index = sorted(range(len(divy)), key=lambda i: divy[i], reverse=True)[:8]

    divy_sort= []
    identifier = []

    for i in divy_sort_index:
        divy_sort.append(divy[i]) 
        identifier.append(stock[i])
        
    name_sorted = []
    stock_sorted = []

    for i in identifier:
        for j in bts.find({"Stock Code": i}):
            name_sorted.append(j['Name'])
            stock_sorted.append(j['Stock Code'])
            
    return name_sorted, stock_sorted, divy_sort

def get_div_bond():

    client = MongoClient(db_url)
    bonds = client['SGX']['dividend_bond']

    stock = []
    div = []
    price = []

    for i in bonds.find({}):
        stock.append(i['Stock Code'])
        div.append(i['2020 Dividend'])
        price.append(i['Price'])
        
    divy=[]

    for i, j, k in zip(stock, div, price):
        if k == 0:
            continue
        divy.append(round(j/k*100,2))
            
    divy_sort_index = sorted(range(len(divy)), key=lambda i: divy[i], reverse=True)[:8]

    divy_sort= []
    identifier = []

    for i in divy_sort_index:
        divy_sort.append(divy[i]) 
        identifier.append(stock[i])
        
    name_sorted = []
    stock_sorted = []

    for i in identifier:
        for j in bonds.find({"Stock Code": i}):
            name_sorted.append(j['Name'])
            stock_sorted.append(j['Stock Code'])
            
    return name_sorted, stock_sorted, divy_sort

def get_div_etf():

    client = MongoClient(db_url)
    etfs = client['SGX']['dividend_etfs']

    resp_usd = requests.get('https://v6.exchangerate-api.com/v6/**/pair/USD/SGD')
    USD = resp_usd.json()["conversion_rate"]

    stock = []
    div = []
    price = []

    for i in etfs.find({}):
        stock.append(i['Stock Code'])
        div.append(i['2020 Dividend'])
        price.append(i['Price'])

    divy=[]

    for i, j, k in zip(stock, div, price):
        if i == "COI":
            divy.append(round((j/USD)/k*100,2))   
        elif i == "QL3":
            divy.append(round((j*USD)/k*100,2))               
        else:
            divy.append(round(j/k*100,2))
            
    divy_sort_index = sorted(range(len(divy)), key=lambda i: divy[i], reverse=True)[:8]

    divy_sort= []
    identifier = []

    for i in divy_sort_index:
        divy_sort.append(divy[i]) 
        identifier.append(stock[i])
        
    name_sorted = []
    stock_sorted = []

    for i in identifier:
        for j in etfs.find({"Stock Code": i}):
            name_sorted.append(j['Name'])
            stock_sorted.append(j['Stock Code'])
            
    return name_sorted, stock_sorted, divy_sort













def start(update, context):

    firstname = update.message.chat.first_name  

    update.message.reply_text(
        f'Hello {firstname},\n\n'
        'I am SGStocksBot, your one-stop virtual assistant to help you with any SG stock queries!\n\n' 
        'These are the available commands:\n'        
        '/info [ Name / Stock Quote] - Gives the basic information of the stock / bond.\n\n'
        '/div [ Stock Quote ] - To view the current dividend yield and the dividend history for the past 5 years.\n\n'
        '/divsum [ Stock Quote, Start Year, End Year, Number of shares ] - To calculate the amount of dividends collected for a time period (start and end year inclusive) given the number of shares owned in that particular security.\n\n'
        '/updiv - To view the upcoming dividend / corporate actions for SGX Listed Companies.\n\n'
        '/divrank - To view the top 8 Singapore securities ranked according to the highest dividend yields.\n\n'
        '/news - To view the recent Singapore financial news.\n\n'
        '/trend [ Stock Quote, Number of year(s) as Lookback Period ] - To view the trend analysis of stock in a given lookback period.\n\n'        
        '/support - Thank you for loving SGStocksBot. If you would like to contribute and help support the running of this Bot, you may wish to do so via PayLah.\n\n'
        'You may also share with other users using the following link:\nhttps://t.me/SGStocksBot\n\n'
         'Thank you so much for checking out the SGStocksBot!')

def info(update, context):

    msg = update.message.text
    input = msg.replace('/info ', '')

    output = stock_name(input)
    if isinstance(output["Security"], list):
        name1 = output["Security"][0]
        name2 = output["Security"][1]
        ticker1 = output["Stock Code"][0]
        ticker2 = output["Stock Code"][1]

        ticker_mod = ticker1 + ".SI"

        last_price, change, per_change, open_price, day_low, day_high, bid_price, bid_vol, ask_price, ask_vol, total_vol = get_stock_info(ticker1)
        low_52, high_52 = get_52_weeks(ticker_mod)

        text = "{} ({})".format(name1, ticker1)
        if change < 0:
            text += "\n" + "Last Price: {}  ▼ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        elif change > 0: 
            text += "\n" + "Last Price: {}  ▲ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        else:
            text += "\n" + "Last Price: {}   ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        text += "\n" + "Open Price: {}".format(str(open_price))

        text += "\n\n" + "Day's Range: {} - {}".format(str(day_low), str(day_high))   
        if low_52 == "N/A":
            pass
        else:
            text += "\n" + "52-Week Range: {} - {}".format(str(low_52), str(high_52))

        text += "\n\n" + "Bid: {} ({}k)".format(bid_price, str(bid_vol))
        text += "\n" + "Ask: {} ({}k)".format(ask_price, str(ask_vol))
        text += "\n" + "Total Volume: {}k".format(str(total_vol))     

        ticker_mod = ticker2 + ".SI"

        last_price, change, per_change, open_price, day_low, day_high, bid_price, bid_vol, ask_price, ask_vol, total_vol = get_stock_info(ticker2)
        low_52, high_52 = get_52_weeks(ticker_mod)

        text += "\n\n" + "{} ({})".format(name2, ticker2)
        if change < 0:
            text += "\n" + "Last Price: {}  ▼ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        elif change > 0: 
            text += "\n" + "Last Price: {}  ▲ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        else:
            text += "\n" + "Last Price: {}   ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        text += "\n" + "Open Price: {}".format(str(open_price))

        text += "\n\n" + "Day's Range: {} - {}".format(str(day_low), str(day_high))   
        if low_52 == "N/A":
            pass
        else:
            text += "\n" + "52-Week Range: {} - {}".format(str(low_52), str(high_52))

        text += "\n\n" + "Bid: {} ({}k)".format(bid_price, str(bid_vol))
        text += "\n" + "Ask: {} ({}k)".format(ask_price, str(ask_vol))
        text += "\n" + "Total Volume: {}k".format(str(total_vol))   

    else:
        name = output["Security"]
        ticker = output["Stock Code"]

        ticker_mod = ticker + ".SI"

        last_price, change, per_change, open_price, day_low, day_high, bid_price, bid_vol, ask_price, ask_vol, total_vol = get_stock_info(ticker)
        low_52, high_52 = get_52_weeks(ticker_mod)

        text = "{} ({})".format(name, ticker)
        if change < 0:
            text += "\n" + "Last Price: {}  ▼ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        elif change > 0: 
            text += "\n" + "Last Price: {}  ▲ ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        else:
            text += "\n" + "Last Price: {}   ( {} | {}% )".format(str(last_price), str(change), str(round(per_change,2)))
        text += "\n" + "Open Price: {}".format(str(open_price))

        text += "\n\n" + "Day's Range: {} - {}".format(str(day_low), str(day_high))   
        if low_52 == "N/A":
            pass
        else:
            text += "\n" + "52-Week Range: {} - {}".format(str(low_52), str(high_52))

        text += "\n\n" + "Bid: {} ({}k)".format(bid_price, str(bid_vol))
        text += "\n" + "Ask: {} ({}k)".format(ask_price, str(ask_vol))
        text += "\n" + "Total Volume: {}k".format(str(total_vol))          

    update.message.reply_text(text)

def div(update, context):

    msg = update.message.text
    input = msg.replace('/div ', '')

    try: 
        output = stock_name(input)
        name = output["Security"]
        ticker = output["Stock Code"]
        
        last_price, change, per_change, open_price, day_low, day_high, bid_price, bid_vol, ask_price, ask_vol, total_vol = get_stock_info(ticker)
        df, last_5_yr, prev_yr, current_div_yield = get_current_div_yield(ticker, last_price)

        text = "Current Dividend Yield Based on {} Dividends: \n".format(prev_yr)
        text += "{}%".format(current_div_yield) 

        text += "\n\n" + "Dividend History for {}".format(name)
        
        for i in range(len(df)):
            if df['Year'][i] == str(last_5_yr):
                break
            elif df['Amount'][i] == '-':
                text += "\n" + "Ex-Date: {}".format(datetime.datetime.strptime(df["Ex Date"][i], '%Y-%m-%d').strftime("%b %d, %Y"))
                text += "\n" + df['Particulars'][i] + "\n"
            else:        
                if df["Ex Date"][i] != "-":         
                    text += "\n" + "Ex-Date: {}".format(datetime.datetime.strptime(df["Ex Date"][i], '%Y-%m-%d').strftime("%b %d, %Y"))
                if df["Pay Date"][i]!= "-":
                    text += "\n" + "Pay-Date: {}".format(datetime.datetime.strptime(df["Pay Date"][i], '%Y-%m-%d').strftime("%b %d, %Y"))
                text += "\n" + re.sub('(\d+(\.\d+)?)', r' \1 ', df['Amount'][i]).strip() + "\n"           

        update.message.reply_text(text)

    except:
        text = "There appears to be an error. Please try again. \n\nKindly input in the following format: \n/div [Stock Ticker] \n(e.g. /div D05)\n\nYou may consider using the /info command to find the ticker of the stock/bond."
        update.message.reply_text(text)

def divsum(update, context):

    msg = update.message.text
    input = msg.replace('/divsum ', '')
    
    try: 
        ticker_input, start, end, no = input.split(",")
        output = stock_name(ticker_input)
        name = output["Security"]
        ticker = output["Stock Code"]
        total_div, year_list, div_list, currency = calc_div_sum(ticker, int(start), int(end), int(no))

        text = "Total Dividends collected for {} ({}) from {} to {}: \n".format(name, ticker, start, end)
        text += "{}".format(total_div) 

        text += "\n\n" + "Dividend Breakdown for {} shares of {}: \n".format(no, name)

        for year, div in zip(year_list,div_list):
            text += "{}: {} {:.2f}\n".format(year,currency, div * int(no)) 

        update.message.reply_text(text)
    except:
        text = "There appears to be an error. Please try again. \n\nKindly input in the following format: \n/divsum [Stock Ticker], [Start Year], [End Year], [Number of Shares]\n(e.g. /divsum D05, 2015, 2020, 1000)\n\nYou may consider using the /info command to find the ticker of the stock/bond."
        update.message.reply_text(text)

def updiv(update, context):

    msg = update.message.text
    df = get_upcoming_dividend()

    text = "Upcoming Dividends: \n"

    for i in range(len(df)):
        if i > 4:
            break
    
        text += "\n" + "{} ({})".format(df['Stock / REIT'][i].split(" (SGX:")[0].title(), df['Stock / REIT'][i].split(" (SGX:")[1][:-1])
        text += "\n" + "Type: {}".format(df['Type'][i].capitalize()) 
        text += "\n" + "Details: {}".format(df['Detail'][i]) 
        text += "\n" + "Ex-Date: {}".format(datetime.datetime.strptime(df["Ex Date"][i], '%Y-%m-%d').strftime("%b %d, %Y"))        
        if df["Payment Date"][i]:
            text += "\n" + "Payment Date: {}".format(datetime.datetime.strptime(df["Payment Date"][i], '%Y-%m-%d').strftime("%b %d, %Y"))    
        text += "\n"

    update.message.reply_text(text)

def news(update, context):

    msg = update.message.text

    title_list, link_list, time_list = get_news()

    text = "Recent News: \n\n"

    for title, link, time in zip(title_list, link_list, time_list):
            text += "{}\n{}\n{}\n\n".format(title, time, link)

    update.message.reply_text(text)

def trend(update, context):

    msg = update.message.text
    input = msg.replace('/trend ', '')
    
    try: 
        ticker_input, lookback = input.split(",")
        stock_mean, trendline, sdhav, sd1, sdneghav, sdneg1, trend, plt = get_technical(ticker_input, int(lookback))
        
        output = stock_name(ticker_input)
        name = output["Security"]
        ticker = output["Stock Code"]

        text = "Trend Analysis for {} ({}) for the last {} year(s): \n\n".format(name, ticker, lookback)
        text += "Mean: {:.2f}\n".format(float(stock_mean))
        text += "Stock Trendline: {:.2f}\n\n".format(float(trendline))
        text += "1 Standard Deviation below Mean: {:.2f}\n".format(float(sdneg1[-1]))    
        text += "1/2 Standard Deviation below Mean: {:.2f}\n".format(float(sdneghav[-1])) 
        text += "1/2 Standard Deviation above Mean: {:.2f}\n".format(float(sdhav[-1]))  
        text += "1 Standard Deviation above Mean: {:.2f}\n\n".format(float(sd1[-1]))
        if trend == "Up":   
            text += "Overall Trend: {} ▲ \n".format(trend)  
        if trend == "Down":
            text += "Overall Trend: {} ▼ \n".format(trend)            

        update.message.reply_text(text)

        user_id = int(update.message.chat_id)
        bot = TelegramBot(TOKEN, user_id)
        bot.send_plot(plt)
    except:
        text = "There appears to be an error. Please try again. \n\nKindly input in the following format: \n/trend [Stock Ticker], [Number of years as Lookback Period] \n(e.g. /trend D05, 3)"
        update.message.reply_text(text)

def support(update, context):

    msg = update.message.text

    text = "Hi there!\n\nPlease click on the link below to support SGStocksBot via Paylah.\nhttps://www.dbs.com.sg/personal/mobile/paylink/index.html?tranRef=**"

    update.message.reply_text(text)

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def menu(update,context):
    categories = ['Blue Chip Stocks', 'REITs', 'Business Trusts', 'Bonds', 'ETFs']
    button_list = []

    for i in categories:
        button_list.append(InlineKeyboardButton(i, callback_data = i))

    reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
    update.message.reply_text(text='Choose from the following',reply_markup=reply_markup)

def bluechips(update, context):
    query = update.callback_query
    bot = context.bot
    
    name, ticker, dividend_yield = get_div_blue()
    text = "Blue chip stocks with the highest dividend yields based on 2020 dividends:\n\n"

    counter = 1
    for i, j, k in zip(name, ticker, dividend_yield):
        text += "{}. {} ({}) \n    {}%\n\n".format(counter,i, j, str(k))
        counter+=1
    
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text)

def reits(update, context):
    query = update.callback_query
    bot = context.bot
    
    name, ticker, dividend_yield = get_div_reits()
    text = "REITs with the highest dividend yields based on 2020 dividends:\n\n"

    counter = 1
    for i, j, k in zip(name, ticker, dividend_yield):
        text += "{}. {} ({}) \n    {}%\n\n".format(counter,i, j, str(k))
        counter+=1
    
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text)

def bts(update, context):
    query = update.callback_query
    bot = context.bot
    
    name, ticker, dividend_yield = get_div_bt()
    text = "Business trusts with the highest dividend yields based on 2020 dividends:\n\n"

    counter = 1
    for i, j, k in zip(name, ticker, dividend_yield):
        text += "{}. {} ({}) \n    {}%\n\n".format(counter,i, j, str(k))
        counter+=1
    
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text)

def bonds(update, context):
    query = update.callback_query
    bot = context.bot
    
    name, ticker, dividend_yield = get_div_bond()
    text = "Bonds with the highest yields based on 2020 dividends:\n\n"

    counter = 1
    for i, j, k in zip(name, ticker, dividend_yield):
        text += "{}. {} ({}) \n    {}%\n\n".format(counter,i, j, str(k))
        counter+=1
    
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text)

def etfs(update, context):
    query = update.callback_query
    bot = context.bot
    
    name, ticker, dividend_yield = get_div_etf()
    text = "ETFs with the highest dividend yields based on 2020 dividends:\n\n"

    counter = 1
    for i, j, k in zip(name, ticker, dividend_yield):
        text += "{}. {} ({}) \n    {}%\n\n".format(counter,i, j, str(k))
        counter+=1
    
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=text)


def noncommand(update, context):
    update.message.reply_text(        
        'It appears to be an invalid command. Please try again!\n\n' 
        'These are the available commands:\n'        
        '/info [ Name / Stock Quote] - Gives the basic information of the stock / bond.\n\n'
        '/div [ Stock Quote ] - To view the current dividend yield and the dividend history for the past 5 years.\n\n'
        '/divsum [ Stock Quote, Start Year, End Year, Number of shares ] - To calculate the amount of dividends collected for a time period (start and end year inclusive) given the number of shares owned in that particular security.\n\n'
        '/updiv - To view the upcoming dividend / corporate actions for SGX Listed Companies.\n\n'
        '/divrank - To view the top 8 Singapore securities ranked according to the highest dividend yields.\n\n'
        '/news - To view the recent Singapore financial news.\n\n'
        '/trend [ Stock Quote, Number of year(s) as Lookback Period ] - To view the trend analysis of stock in a given lookback period.\n\n'        
        '/support - Thank you for loving SGStocksBot. If you would like to contribute and help support the running of this Bot, you may wish to do so via PayLah.\n\n'
        'Thank you so much for checking out the SGStocksBot!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    updater = Updater(
        TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Available Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("div", div))
    dp.add_handler(CommandHandler("divsum", divsum))
    dp.add_handler(CommandHandler("updiv", updiv))
    dp.add_handler(CommandHandler("divrank", menu))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("trend", trend))
    dp.add_handler(CommandHandler("support", support))

    dp.add_handler(CallbackQueryHandler(bluechips, pattern='Blue Chip Stocks'))
    dp.add_handler(CallbackQueryHandler(reits, pattern='REITs'))
    dp.add_handler(CallbackQueryHandler(bts, pattern='Business Trusts'))
    dp.add_handler(CallbackQueryHandler(bonds, pattern='Bonds'))
    dp.add_handler(CallbackQueryHandler(etfs, pattern='ETFs'))


    # Handle noncommand messages
    dp.add_handler(MessageHandler(Filters.text, noncommand))

    # Log all errors
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://sgstocksbot.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()