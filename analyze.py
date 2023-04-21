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
    fig = plot.figure()
    for i in range(1, 5):
        ax = fig.add_subplot(2, 2, i)
        col1 = 'red'
        col2 = 'green'
        width = .3
        width2 = .03
        stocks_one = pandas.DataFrame(data[dates[i - 1]][0])
        up_one = stocks_one[stocks_one.close >= stocks_one.open]
        down_one = stocks_one[stocks_one.close < stocks_one.open]
        ax.bar(up_one.index, up_one.close-up_one.open, width, bottom=up_one.open, color=col1)
        ax.bar(up_one.index, up_one.high-up_one.close, width2, bottom=up_one.close, color=col1)
        ax.bar(up_one.index, up_one.low-up_one.open, width2, bottom=up_one.open, color=col1)
        ax.bar(down_one.index, down_one.close-down_one.open, width, bottom=down_one.open, color=col2)
        ax.bar(down_one.index, down_one.high-down_one.open, width2, bottom=down_one.open, color=col2)
        ax.bar(down_one.index, down_one.low-down_one.close, width2, bottom=down_one.close, color=col2)
        times = data[dates[i - 1]][1]
        ax.set_xticks(range(25), times, fontsize=5, rotation = 90)
        ax.yaxis.grid()
        ax.title.set_text(f'Netflix Stock on {dates[i - 1]}')
    fig.tight_layout(pad=2)
    fig.supxlabel('Time (EST)')
    fig.supylabel('Stock Price (USD)')
    fig.suptitle('Netflix Stock Candle Chart for the Last 4 Open Market Days', fontsize=14, y=0.99)
    plot.savefig('NetflixStockChart.png')




    


def make_volatility_chart(conn, cur):
    # make chart that records volatility of the tweets vs ABSOLUTE DIFFERENCE OF THE STOCKS OPEN AND CLOSE
    # use AVG function to get AVG tweets and compare amount of tweets to avg (absolute value)
    # make separate figure to split by days
    return

def make_pos_neg_volatility_chart(conn, cur):
    # same as above except no absolute value
    cur.execute(f'''SELECT AVG(tweets) FROM NetflixTweets''')
    data = {}

    for day in range(1, 5):
        cur.execute(f'''SELECT AVG(tweets) FROM NetflixTweets Join Date ON Date.dateID = {day}''')
        avg = int(cur.fetchone()[0])
        print(avg)
        # needs stock open - stock close
        stock_diff = []
        # needs num tweets - avg
        tweet_vol = []
        # needs times
        times = []

        date = ''

        cur.execute(f'''SELECT NetflixStocks.open, NetflixStocks.close, NetflixTweets.tweets,
        Times.datetime From NetflixStocks, Times JOIN NetflixTweets ON NetflixStocks.timeID = NetflixTweets.timeID
        JOIN Date ON Date.dateID = {day}''')

        for row in cur:
            date = row[3][:10]
            stock_diff.append(row[0] - row[1])
            tweet_vol.append(row[2] - avg)
            times.append(row[3][11:19])
        data[date] = stock_diff, tweet_vol, times

        print(data)

    return

def create_charts(conn, cur):
    make_stock_chart(conn, cur)
    make_volatility_chart(conn, cur)
    make_pos_neg_volatility_chart(conn, cur)



# make_stock_chart(conn, cur)
make_pos_neg_volatility_chart(conn, cur)