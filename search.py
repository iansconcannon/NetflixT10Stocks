import tweepy
import config
import yfinance
from datetime import datetime, timedelta
import pytz

'''client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'netflix'
counts = client.get_recent_tweets_count(query=query, start_time='2023-04-14T00:00:00.000Z', end_time='2023-04-14T00:15:00.000Z')
for count in counts.data:
    print(count)'''

#netflix = yfinance.Ticker('NFLX')
#df = netflix.history(period = '7d', actions=False, rounding=True, interval = '15m')
#print(df.loc['2023-04-11 09:45:00-04:00', 'Open'] - df.loc['2023-04-11 09:30:00-04:00', 'Open']) #how to index
#print(df.loc['2023-04-11 10:30:00-04:00', 'Open'] - df.loc['2023-04-11 10:15:00-04:00', 'Open'])
# start_time, end_time in YYYY-MM-DDTHH:mm:ssZ so like 2000-01-23T20:00:00Z and the time is in UTC
# start at 9:30 each morning, end in 15 minute intervals

# for yahoo finance, get difference in NFLX ticker symbol for the corresponding time for the past 15 minutes (end - start) keep the signs (no absolute value)
# DATABASE USES CLOSING TIME FOR TWITTER AND OPENING TIME FOR STOCKS AS THE PRIMARY KEY

'''markettime = pytz.timezone('US/Eastern')
print(datetime.now(markettime))
date = datetime.today() - timedelta(days=30)
newdate = date - timedelta(days=2)
print(date)
print(newdate)
print(datetime.today())'''

def get_datetimes():
    days = {}
    markettime = pytz.timezone('US/Eastern')
    date = (datetime.now(markettime) - timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
    while len(days) < 4:
        while date.weekday() > 4:
            date = date - timedelta(days=1)
        datetimes = []
        for i in range(0,27):
            datetimes.append(str(date + timedelta(minutes=(15 * i))))
        days[str(date.date())] = datetimes
        date = date - timedelta(days=1)
    return days

def get_netflix_stock(datetimes):
    netflix = yfinance.Ticker('NFLX')
    stocks = netflix.history(period = '7d', actions = False, rounding = True, interval = '15m')
    print(stocks)
    price_changes = {}
    for date in datetimes:
        for i in range(1,26):
            start_time = (datetimes[date])[i]
            price_difference = stocks.loc[start_time, 'Close'] - stocks.loc[start_time, 'Open']
            price_changes[start_time] = price_difference
    return price_changes

'''days = get_datetimes()
dic = get_netflix_stock(days)
print(dic)'''

def convert_times(time):
    # 2023-04-18 10:00:00-04:00
    updated = time[:10]
    updated += 'T'
    hour = str(int(time[11:13]) + 4)
    if len(hour) == 1:
        updated += '0'
        updated += hour
    else:
        updated += hour
    updated += time[13:19]
    updated += 'Z'
    return updated

def get_tweet_counts(queries, datetimes):
    tweet_counts = {}
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
    for date in datetimes:
        for i in range(0,25):
            start_time_est = (datetimes[date])[i]
            end_time_est = (datetimes[date])[i + 1]
            start_time = convert_times(start_time_est)
            end_time = convert_times(end_time_est)
            for query in queries:
                counts = client.get_recent_tweets_count(query=query, start_time=start_time, end_time=end_time)
                if end_time in tweet_counts:
                    tweet_counts[end_time_est] += counts
                else:
                    tweet_counts[end_time_est] = counts
    return tweet_counts

dates = get_datetimes()
queries = ['Netflix']

#dummy = get_tweet_counts(queries, dates)
#print(dummy)
test = convert_times('2023-04-17 11:00:00-04:00')
print(test)
