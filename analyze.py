import sqlite3
import os
import pandas
import matplotlib.pyplot as plot

database_name = 'test.db'
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+database_name)
cur = conn.cursor()


def make_stock_chart(conn, cur): 
    # make candlestick chart
    # 4 days 1 - 4:
    # for each day date chart, JOIN stock chart on timeID = timeID, time dateID = date dateID WHERE date day = NUMBER:
    # THEN make chart (1 of 4) and put it in a certain part.
    
    data = {}
    for day in range(1,5):
        cur.execute(f'''SELECT NetflixStocks.open, NetflixStocks.close, NetflixStocks.high, NetflixStocks.low, Times.datetime
        FROM NetflixStocks JOIN Times ON Times.timeID = NetflixStocks.timeID JOIN Date on Times.dateID = Date.dateID WHERE Date.dateID = {day}''')
        open = []
        close = []
        high = []
        low = []
        times = []
        date = ''
        for row in cur:
            date = row[4][:10]
            open.append(row[0])
            close.append(row[1])
            high.append(row[2])
            low.append(row[3])
            times.append(row[4][11:19])
        data[date] = {'open': open, 'close': close, 'high': high, 'low': low}, times
    dates = []
    print(data)
    for day in data:
        dates.append(day)
    



    


def make_volatility_chart(conn, cur):
    # make chart that records volatility of the tweets vs ABSOLUTE DIFFERENCE OF THE STOCKS OPEN AND CLOSE
    # use AVG function to get AVG tweets and compare amount of tweets to avg (absolute value)
    # make separate figure to split by days
    return

def make_pos_neg_volatility_chart(conn, cur):
    # same as above excpet no absolute value
    return

def create_charts(conn, cur):
    make_stock_chart(conn, cur)
    make_volatility_chart(conn, cur)
    make_pos_neg_volatility_chart(conn, cur)



make_stock_chart(conn, cur)