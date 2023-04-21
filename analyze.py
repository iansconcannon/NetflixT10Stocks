import sqlite3
import os


database_name = 'test.db'
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+database_name)
cur = conn.cursor()


def make_stock_chart(conn, cur): 
    data = []
    cur.execute('SELECT NetflixTweets.datetime, NetflixTweets.tweets, NetflixStocks.open, NetflixStocks.close, NetflixStocks.high, NetflixStocks.low FROM NetflixTweets JOIN NetflixStocks ON NetflixTweets.datetime = NetflixStocks.datetime')
    for row in cur:
        data.append(row)
    conn.commit()

