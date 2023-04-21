import sqlite3
import os


database_name = 'test.db'
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+database_name)
cur = conn.cursor()


def make_stock_chart(conn, cur): 
    # make candlestick chart
    # 4 days 1 - 4:
    # for each day date chart, JOIN stock chart on timeID = timeID, time dateID = date dateID WHERE date day = NUMBER:
    # THEN make chart (1 of 4) and put it in a certain part.
    return
    


def make_volatility_chart(conn, cur):
    # make chart that records volatility of the tweets vs ABSOLUTE DIFFERENCE OF THE STOCKS OPEN AND CLOSE
    # use AVG function to get AVG tweets and compare amount of tweets to avg (absolute value)
    # make separate figure to split by days
    return

def make_pos_neg_volatility_chart(conn, cur):
    # same as above excpet no absolute value
    return

