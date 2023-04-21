import sqlite3
import os
import pandas
import matplotlib.pyplot as plot

database_name = 'test.db'
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+database_name)
cur = conn.cursor()


def make_stock_chart(cur): 
    # make candlestick chart
    # 4 days 1 - 4:
    # for each day date chart, JOIN stock chart on timeID = timeID, time dateID = date dateID WHERE date day = NUMBER:
    # THEN make chart (1 of 4) and put it in a certain part


    data = {}
    for day in range(1,5):
        cur.execute(f'''SELECT NetflixStocks.open, NetflixStocks.close, NetflixStocks.high, NetflixStocks.low, Times.datetime
        FROM NetflixStocks JOIN Times ON Times.timeID = NetflixStocks.timeID JOIN Date on Times.dateID = Date.dateID WHERE Date.dateID = {day}''')
        _open = []
        close = []
        high = []
        low = []
        times = []
        date = ''
        for row in cur:
            date = row[4][:10]
            _open.append(row[0])
            close.append(row[1])
            high.append(row[2])
            low.append(row[3])
            times.append(row[4][11:19])
        data[date] = {'open': _open, 'close': close, 'high': high, 'low': low}, times
    dates = []
    for day in data:
        dates.append(day)
    fig = plot.figure()
    for i in range(1, 5):
        ax = fig.add_subplot(2, 2, i)
        col1 = 'green'
        col2 = 'red'
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




    


def make_volatility_chart(cur, f):
    # make chart that records volatility of the tweets vs ABSOLUTE DIFFERENCE OF THE STOCKS OPEN AND CLOSE
    # use AVG function to get AVG tweets and compare amount of tweets to avg (absolute value)
    # make separate figure to split by days
    data = {}

    f.write('VOLATILITY CHART CALCULATIONS:\n')
    f.write('\n')

    for day in range(1, 5):
        cur.execute(f'''SELECT SUM(NetflixTweets.tweets) FROM NetflixTweets JOIN Times ON NetflixTweets.timeID = Times.timeID 
                        JOIN Date ON Times.dateID = Date.dateID WHERE Date.dateID = {day}''')
        sum = int(cur.fetchone()[0])
        f.write(f'Sum of tweets on {day} most recent day: {sum}\n')

        # for opening (i-1 * 25 ) + 1
        cur.execute(f'''SELECT NetflixStocks.open, Times.datetime FROM NetflixStocks JOIN Times ON
                        NetflixStocks.timeID = Times.timeID WHERE NetflixStocks.timeID = {((day-1) * 25) + 1}''')
        t = cur.fetchone()
        day_open = t[0]
        date = t[1][:10]
        # for closing i * 25
        cur.execute(f'''SELECT NetflixStocks.close FROM NetflixStocks WHERE NetflixStocks.timeID = {day * 25}''')
        day_close = cur.fetchone()[0]

        data[date] = [day_open, day_close, sum]
    dates = []
    for date in data:
        dates.append(date)
    


    # First list is stock change, second list in twitter volatility, third list in times
    dates = []
    abs_change = []
    sum = []
    for day in data:
        dates.append(day)
        abs_change.append(500 * abs(round(data[day][0] - data[day][1], 2)))
        sum.append(data[day][2])

    fig = plot.figure()
    x = range(1, 5)
    ax = fig.add_subplot(111)
    ax.plot(x, abs_change, label = 'Abs. Value of Stock Change')
    ax.plot(x, sum, label = 'Tweet Count Volatility')
    ax.legend(fontsize=6)
    ax.set_xticks(range(4), dates, fontsize=5, rotation = 90)
    
    fig.tight_layout(pad=3.25)
    fig.supxlabel('Date')
    fig.supylabel('Scaled Stock Price Change (Absolute Val) \n and Total Number of Tweets')
    fig.suptitle('Correlation Line Graph for Tweet \n Counts and Stock Price Changes', fontsize=14, y=0.99)
    plot.savefig('Volatility.png')

    return


def make_pos_neg_volatility_chart(cur, f):
    # same as above except no absolute value
    data = {}
    f.write('\n')
    f.write('CORRELATION CHART CALCULATIONS:\n')
    f.write('\n')
    for day in range(1, 5):
        cur.execute(f'''SELECT AVG(NetflixTweets.tweets) FROM NetflixTweets JOIN Times ON NetflixTweets.timeID = Times.timeID 
                        Join Date ON Times.dateID = Date.dateID WHERE Date.dateID = {day}''')
        avg = int(cur.fetchone()[0])
        f.write(f'Average amount of tweets for {day} most recent day: {avg}\n')
        # needs stock open - stock close
        stock_diff = []
        # needs num tweets - avg
        tweet_vol = []
        # needs times
        times = []

        date = ''

        cur.execute(f'''SELECT NetflixStocks.open, NetflixStocks.close, NetflixTweets.tweets, Times.datetime
                    FROM NetflixStocks JOIN NetflixTweets ON NetflixStocks.timeID = NetflixTweets.timeID
                    JOIN Times ON NetflixStocks.timeID = Times.timeID JOIN Date on Times.dateID = Date.dateID WHERE Date.dateID = {day}''')

        for row in cur:
            date = row[3][:10]
            stock_diff.append(round(row[0] - row[1], 2) * 10)
            tweet_vol.append(round(row[2] - avg, 2))
            times.append(row[3][11:19])
        data[date] = [stock_diff, tweet_vol, times]

    # First list is stock change, second list in twitter volatility, third list in times
    dates = []
    for day in data:
        dates.append(day)

    fig = plot.figure()
    x = range(1, 26)
    for i in range(1, 5):
        ax = fig.add_subplot(2, 2, i)
        ax.plot(x, data[dates[i - 1]][0], label = 'Stock Change')
        ax.plot(x, data[dates[i - 1]][1], label = 'Tweet Count Volatility')
        ax.legend(fontsize=6)
        times = data[dates[i - 1]][2]
        ax.set_xticks(range(25), times, fontsize=5, rotation = 90)
    
    fig.tight_layout(pad=3.25)
    fig.supxlabel('Time (EST)')
    fig.supylabel('Scaled Stock Price Change and Difference \n Between Tweet Count and Tweet Average')
    fig.suptitle('Correlation Line Graph for Tweet \n Counts and Stock Price Changes', fontsize=14, y=0.99)
    plot.savefig('CorrelationGraph.png')



def create_charts(cur):
    f = open('calculations.txt', 'w')
    make_stock_chart(cur)
    make_volatility_chart(cur, f)
    make_pos_neg_volatility_chart(cur, f)
    f.close()

create_charts(cur)