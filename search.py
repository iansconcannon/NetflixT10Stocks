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
            # (open, close, high, low)
            prices = (stocks.loc[start_time, 'Open'], stocks.loc[start_time, 'Close'], stocks.loc[start_time, 'High'], stocks.loc[start_time, 'Low'])
            price_changes[start_time] = prices
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

s = 'Netflix (You OR Outer Banks OR) OR tags...'

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

def create_and_add_to_database(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database_name)
    cur = conn.cursor()
    
    cur.execute('CREATE TABLE IF NOT EXISTS NetflixTweets (datetime TEXT PRIMARY KEY, tweets INT)')
    cur.execute('CREATE TABLE IF NOT EXISTS NetflixStocks (datetime TEXT PRIMARY KEY, open FLOAT, close FLOAT, high FLOAT, low FLOAT)')

    datetimes = get_datetimes()

    unused = False
    first = True
    for date in datetimes:
        if first == True:
            recent = date
            first = False
        cur.execute(f'SELECT COUNT(*) FROM NetflixTweets WHERE "{str(datetimes[date][1])}" = datetime')
        for row in cur:
            if row[0] == 0:
                today = date
                unused = True
        if unused == True:
            break

    if unused == False:
        return
    
    titles = get_netflix_top_10(str(recent))
    tags = twitter_tag(titles)
    query = make_twitter_query(tags)
    query = "Netflix (You OR Outer Banks OR Wednesday)"
    current = datetimes[today][1:-1]
    stocks = get_netflix_stock(datetimes)
    tweet = get_tweet_counts(query, datetimes, today)
    for time in current:
        cur.execute('INSERT INTO NetflixTweets (datetime, tweets) VALUES (?,?)', (str(time), tweet[time]))
        cur.execute('INSERT INTO NetflixStocks (datetime, open, close, high, low) VALUES (?,?,?,?,?)', (str(time), stocks[time][0], stocks[time][1], stocks[time][2], stocks[time][3]))
    conn.commit()

create_and_add_to_database('test.db')


    
    
