import tweepy
import config
import yfinance
from datetime import datetime, timedelta
import pytz
import json
import sqlite3
import os
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import ssl
import re


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
    price_changes = {}
    for date in datetimes:
        for i in range(1,26):
            start_time = (datetimes[date])[i]
            price_difference = round(stocks.loc[start_time, 'Close'] - stocks.loc[start_time, 'Open'], 2)
            price_changes[start_time] = price_difference
    return price_changes

def convert_times(time):
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

def get_tweet_counts(query, datetimes, date):
    # DOES ONLY ONE DATE TO AVOID RATE LIMITING
    tweet_counts = {}
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
    for i in range(0,25):
        start_time_est = (datetimes[date])[i]
        end_time_est = (datetimes[date])[i + 1]
        start_time = convert_times(start_time_est)
        end_time = convert_times(end_time_est)
        counts = client.get_recent_tweets_count(query=query, start_time=start_time, end_time=end_time)
        tweet_counts[end_time_est] = (counts.data)[0]['tweet_count']
    return tweet_counts

def get_netflix_top_10(date):
    url = 'https://top10.netflix.com/tv?week=' + date
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    titles = []
    table = soup.find_all('tbody')
    shows = (table[0]).find_all('tr')
    for show in shows:
        attributes = show.find_all('td')
        titles.append(attributes[1].text)
    return titles

def twitter_tag(titles):
    d = {}
    regex = 'Season (\d+)'
    for title in titles:
        lst = []
        i = title.rfind(":")
        new_title = title[:i]
        new_title = new_title.replace(" ", "")
        new_title = new_title.replace(":", "")
        lst.append("#"+new_title+"Netflix")
        match = re.search(regex, title)
        if match:
            sNumber = match.group(1)
            num = int(sNumber)
            if num > 1:
                lst.append("#"+new_title+"S"+sNumber)
                lst.append("#"+new_title+"Season"+sNumber)
        d[title] = lst
    return d

def make_twitter_query(tags):
    query = tags[next(iter(tags))][0]
    count = len(query)

    for title in tags: #adds all #[Name]Netflix tags
        s = " OR " + tags[title][0]
        if (count + len(s) < 512):
            count += len(s)
            query += s
        else:
            return query

    for title in tags: #adds all #[Name]S[#]
        if len(tags[title]) > 1:
            s = " OR " + tags[title][1]
            if (count + len(s) < 512):
                count += len(s)
                query += s
            else:
                return query
    
    for title in tags: #adds all #[Name]Season[#]
        if len(tags[title]) > 2:
            s = " OR " + tags[title][2]
            if (count + len(s) < 512):
                count += len(s)
                query += s
            else:
                return query
    return query

def test_twitter_query(query):
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)
    counts = client.get_recent_tweets_count(query=query, start_time="2023-04-19T09:45:00Z", end_time="2023-04-19T10:15:00Z")
    tweet_counts = (counts.data)[0]['tweet_count']
    return tweet_counts



#dates = get_datetimes()
#queries = ['Netflix OR NetflixT10 OR YouS4 OR WednesdayS1']

#dummy = get_tweet_counts(queries, dates)
#print(dummy)

# netflix_stock = {'2023-04-19 09:45:00-04:00': 0.75, '2023-04-19 10:00:00-04:00': 3.73, '2023-04-19 10:15:00-04:00': -1.43, '2023-04-19 10:30:00-04:00': 1.02, '2023-04-19 10:45:00-04:00': -0.5, '2023-04-19 11:00:00-04:00': 0.18, '2023-04-19 11:15:00-04:00': -2.38, '2023-04-19 11:30:00-04:00': 0.59, '2023-04-19 11:45:00-04:00': 1.49, '2023-04-19 12:00:00-04:00': 0.13, '2023-04-19 12:15:00-04:00': -1.83, '2023-04-19 12:30:00-04:00': -0.16, '2023-04-19 12:45:00-04:00': -0.73, '2023-04-19 13:00:00-04:00': 1.07, '2023-04-19 13:15:00-04:00': -0.73, '2023-04-19 13:30:00-04:00': -1.25, '2023-04-19 13:45:00-04:00': 0.48, '2023-04-19 14:00:00-04:00': -0.05, '2023-04-19 14:15:00-04:00': -0.01, '2023-04-19 14:30:00-04:00': 0.87, '2023-04-19 14:45:00-04:00': 0.12, '2023-04-19 15:00:00-04:00': 0.46, '2023-04-19 15:15:00-04:00': 0.34, '2023-04-19 15:30:00-04:00': 1.63, '2023-04-19 15:45:00-04:00': 0.1, '2023-04-18 09:45:00-04:00': 0.52, '2023-04-18 10:00:00-04:00': -1.55, '2023-04-18 10:15:00-04:00': -0.63, '2023-04-18 10:30:00-04:00': 0.84, '2023-04-18 10:45:00-04:00': -1.0, '2023-04-18 11:00:00-04:00': -0.26, '2023-04-18 11:15:00-04:00': 0.39, '2023-04-18 11:30:00-04:00': -0.15, '2023-04-18 11:45:00-04:00': 0.18, '2023-04-18 12:00:00-04:00': 0.87, '2023-04-18 12:15:00-04:00': 0.69, '2023-04-18 12:30:00-04:00': 0.94, '2023-04-18 12:45:00-04:00': 0.27, '2023-04-18 13:00:00-04:00': 0.61, '2023-04-18 13:15:00-04:00': -1.74, '2023-04-18 13:30:00-04:00': -0.36, '2023-04-18 13:45:00-04:00': 0.63, '2023-04-18 14:00:00-04:00': 1.05, '2023-04-18 14:15:00-04:00': 0.12, '2023-04-18 14:30:00-04:00': -0.44, '2023-04-18 14:45:00-04:00': 0.3, '2023-04-18 15:00:00-04:00': 0.77, '2023-04-18 15:15:00-04:00': -1.51, '2023-04-18 15:30:00-04:00': 0.59, '2023-04-18 15:45:00-04:00': -0.01, '2023-04-17 09:45:00-04:00': 1.3, '2023-04-17 10:00:00-04:00': -0.54, '2023-04-17 10:15:00-04:00': -2.1, '2023-04-17 10:30:00-04:00': -1.34, '2023-04-17 10:45:00-04:00': -0.8, '2023-04-17 11:00:00-04:00': -1.42, '2023-04-17 11:15:00-04:00': -0.6, '2023-04-17 11:30:00-04:00': -1.59, '2023-04-17 11:45:00-04:00': 1.18, '2023-04-17 12:00:00-04:00': -0.67, '2023-04-17 12:15:00-04:00': -0.23, '2023-04-17 12:30:00-04:00': 0.26, '2023-04-17 12:45:00-04:00': 1.53, '2023-04-17 13:00:00-04:00': 1.23, '2023-04-17 13:15:00-04:00': -1.25, '2023-04-17 13:30:00-04:00': 0.61, '2023-04-17 13:45:00-04:00': -0.89, '2023-04-17 14:00:00-04:00': 0.18, '2023-04-17 14:15:00-04:00': -0.26, '2023-04-17 14:30:00-04:00': 0.76, '2023-04-17 14:45:00-04:00': 0.52, '2023-04-17 15:00:00-04:00': -1.2, '2023-04-17 15:15:00-04:00': 1.43, '2023-04-17 15:30:00-04:00': 0.7, '2023-04-17 15:45:00-04:00': 0.75, '2023-04-14 09:45:00-04:00': 1.55, '2023-04-14 10:00:00-04:00': -1.14, '2023-04-14 10:15:00-04:00': -2.12, '2023-04-14 10:30:00-04:00': 0.02, '2023-04-14 10:45:00-04:00': -0.59, '2023-04-14 11:00:00-04:00': 0.25, '2023-04-14 11:15:00-04:00': -1.64, '2023-04-14 11:30:00-04:00': 0.55, '2023-04-14 11:45:00-04:00': 0.58, '2023-04-14 12:00:00-04:00': -0.7, '2023-04-14 12:15:00-04:00': 0.81, '2023-04-14 12:30:00-04:00': -1.56, '2023-04-14 12:45:00-04:00': 0.38, '2023-04-14 13:00:00-04:00': 0.47, '2023-04-14 13:15:00-04:00': -0.68, '2023-04-14 13:30:00-04:00': -0.39, '2023-04-14 13:45:00-04:00': 0.53, '2023-04-14 14:00:00-04:00': -0.09, '2023-04-14 14:15:00-04:00': 0.19, '2023-04-14 14:30:00-04:00': -0.07, '2023-04-14 14:45:00-04:00': 0.53, '2023-04-14 15:00:00-04:00': -1.72, '2023-04-14 15:15:00-04:00': 0.4, '2023-04-14 15:30:00-04:00': 1.45, '2023-04-14 15:45:00-04:00': -0.29}
# tweet_counts = {'2023-04-19 09:45:00-04:00': 4101, '2023-04-19 10:00:00-04:00': 3568, '2023-04-19 10:15:00-04:00': 4494, '2023-04-19 10:30:00-04:00': 3965, '2023-04-19 10:45:00-04:00': 3770, '2023-04-19 11:00:00-04:00': 3550, '2023-04-19 11:15:00-04:00': 4365, '2023-04-19 11:30:00-04:00': 3728, '2023-04-19 11:45:00-04:00': 3791, '2023-04-19 12:00:00-04:00': 3309, '2023-04-19 12:15:00-04:00': 3531, '2023-04-19 12:30:00-04:00': 3466, '2023-04-19 12:45:00-04:00': 3315, '2023-04-19 13:00:00-04:00': 3102, '2023-04-19 13:15:00-04:00': 3189, '2023-04-19 13:30:00-04:00': 2856, '2023-04-19 13:45:00-04:00': 2720, '2023-04-19 14:00:00-04:00': 2677, '2023-04-19 14:15:00-04:00': 2729, '2023-04-19 14:30:00-04:00': 2799, '2023-04-19 14:45:00-04:00': 2614, '2023-04-19 15:00:00-04:00': 2536, '2023-04-19 15:15:00-04:00': 2608, '2023-04-19 15:30:00-04:00': 2584, '2023-04-19 15:45:00-04:00': 2674, '2023-04-18 09:45:00-04:00': 4068, '2023-04-18 10:00:00-04:00': 3978, '2023-04-18 10:15:00-04:00': 5450, '2023-04-18 10:30:00-04:00': 5195, '2023-04-18 10:45:00-04:00': 4486, '2023-04-18 11:00:00-04:00': 3844, '2023-04-18 11:15:00-04:00': 4305, '2023-04-18 11:30:00-04:00': 3756, '2023-04-18 11:45:00-04:00': 4098, '2023-04-18 12:00:00-04:00': 3712, '2023-04-18 12:15:00-04:00': 3806, '2023-04-18 12:30:00-04:00': 3437, '2023-04-18 12:45:00-04:00': 3546, '2023-04-18 13:00:00-04:00': 3216, '2023-04-18 13:15:00-04:00': 3132, '2023-04-18 13:30:00-04:00': 2789, '2023-04-18 13:45:00-04:00': 2775, '2023-04-18 14:00:00-04:00': 2573, '2023-04-18 14:15:00-04:00': 2941, '2023-04-18 14:30:00-04:00': 2764, '2023-04-18 14:45:00-04:00': 2627, '2023-04-18 15:00:00-04:00': 2634, '2023-04-18 15:15:00-04:00': 2714, '2023-04-18 15:30:00-04:00': 2705, '2023-04-18 15:45:00-04:00': 2725, '2023-04-17 09:45:00-04:00': 4140, '2023-04-17 10:00:00-04:00': 3408, '2023-04-17 10:15:00-04:00': 4051, '2023-04-17 10:30:00-04:00': 3992, '2023-04-17 10:45:00-04:00': 3730, '2023-04-17 11:00:00-04:00': 3561, '2023-04-17 11:15:00-04:00': 3973, '2023-04-17 11:30:00-04:00': 3787, '2023-04-17 11:45:00-04:00': 3240, '2023-04-17 12:00:00-04:00': 3208, '2023-04-17 12:15:00-04:00': 3331, '2023-04-17 12:30:00-04:00': 3230, '2023-04-17 12:45:00-04:00': 3448, '2023-04-17 13:00:00-04:00': 3395, '2023-04-17 13:15:00-04:00': 3001, '2023-04-17 13:30:00-04:00': 3011, '2023-04-17 13:45:00-04:00': 3076, '2023-04-17 14:00:00-04:00': 2703, '2023-04-17 14:15:00-04:00': 2824, '2023-04-17 14:30:00-04:00': 2680, '2023-04-17 14:45:00-04:00': 2521, '2023-04-17 15:00:00-04:00': 2505, '2023-04-17 15:15:00-04:00': 3733, '2023-04-17 15:30:00-04:00': 2851, '2023-04-17 15:45:00-04:00': 2608, '2023-04-14 09:45:00-04:00': 4127, '2023-04-14 10:00:00-04:00': 4520, '2023-04-14 10:15:00-04:00': 4203, '2023-04-14 10:30:00-04:00': 3589, '2023-04-14 10:45:00-04:00': 3540, '2023-04-14 11:00:00-04:00': 3415, '2023-04-14 11:15:00-04:00': 4317, '2023-04-14 11:30:00-04:00': 3646, '2023-04-14 11:45:00-04:00': 3375, '2023-04-14 12:00:00-04:00': 3369, '2023-04-14 12:15:00-04:00': 3402, '2023-04-14 12:30:00-04:00': 3370, '2023-04-14 12:45:00-04:00': 3328, '2023-04-14 13:00:00-04:00': 3261, '2023-04-14 13:15:00-04:00': 3455, '2023-04-14 13:30:00-04:00': 2505, '2023-04-14 13:45:00-04:00': 2800, '2023-04-14 14:00:00-04:00': 2826, '2023-04-14 14:15:00-04:00': 2935, '2023-04-14 14:30:00-04:00': 2727, '2023-04-14 14:45:00-04:00': 2646, '2023-04-14 15:00:00-04:00': 2575, '2023-04-14 15:15:00-04:00': 3136, '2023-04-14 15:30:00-04:00': 2489, '2023-04-14 15:45:00-04:00': 2333}

def create_and_add_to_database(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database_name)
    cur = conn.cursor()
    
    cur.execute('CREATE TABLE IF NOT EXISTS NetflixTweetsAndStocks (datetime TEXT PRIMARY KEY, stockchange FLOAT, tweets INT)')

    datetimes = get_datetimes()

    unused = False
    for date in datetimes:
        cur.execute(f'SELECT COUNT(*) FROM NetflixTweetsAndStocks WHERE "{str(datetimes[date][1])}" = datetime')
        for row in cur:
            if row[0] == 0:
                today = date
                unused = True
        if unused == True:
            break

    if unused == False:
        return
    # get QUERIES HERE

    current = datetimes[today][1:-1]
    stocks = get_netflix_stock(datetimes)
    query = 'Netflix OR NetflixT10'
    tweet = get_tweet_counts(query, datetimes, today)
    for time in current:
        cur.execute('INSERT INTO NetflixTweetsAndStocks (datetime, stockchange, tweets) VALUES (?,?,?)', (str(time), stocks[time], tweet[time]))
    conn.commit()

# create_and_add_to_database('test.db')
lst = get_netflix_top_10("2023-04-16")
# print(lst)
d = twitter_tag(lst)
# print(d)
query = make_twitter_query(d)
print(query)
print(len(query))
tweet_counts = test_twitter_query(query)
print(tweet_counts)





    
    




