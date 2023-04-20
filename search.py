import tweepy
import config
import yfinance
from datetime import datetime, timedelta
import pytz

'''client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

query = 'covid -is:retweet'
counts = client.get_recent_tweets_count(query=query, granularity='day')'''

#netflix = yfinance.Ticker('NFLX')
#df = netflix.history(period = '7d', actions=False, rounding=True, interval = '15m')
#print(df.loc['2023-04-11 09:45:00-04:00', 'Open'] - df.loc['2023-04-11 09:30:00-04:00', 'Open']) #how to index
#print(df.loc['2023-04-11 10:30:00-04:00', 'Open'] - df.loc['2023-04-11 10:15:00-04:00', 'Open'])
# start_time, end_time in YYYY-MM-DDTHH:mm:ssZ so like 2000-01-23T20:00:00Z and the time is in UTC
# start at 9:30 each morning, end in 15 minute intervals

# for yahoo finance, get difference in NFLX ticker symbol for the corresponding time for the past 15 minutes (end - start) keep the signs (no absolute value)
# 

markettime = pytz.timezone('US/Eastern')
print(datetime.now(markettime))
date = datetime.today() - timedelta(days=30)
newdate = date - timedelta(days=2)
print(date)
print(newdate)
print(datetime.today())