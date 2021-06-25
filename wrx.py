import time
from selenium import webdriver
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import os

# Coins amount
wrx_amount = 79.558112311
bnb_amount = 0.7711
enj_amount = 178.04
matic_amount = 112.0
doge_amount = 332.0

# global variables
portfolio_record = []
ts_record = []
max_port = 0
min_port = 100000
counter = 0
invested = 75490
x_lim = 1000

# path for the local file
local_file_path = 'C:\\Users\\rahul\\Desktop\\Data\\portfolio.txt'

if os.path.exists(local_file_path):
    # read records from the file
    f = open(local_file_path, 'r')
    for record in f.readlines():
        if 60000 > float(record[:8]) > 45000:
            portfolio_record.append(float(record[:8]))
            ts_record.append(record[-9:-1])
    f.close()

    # calculate maximum port amount
    max_port = max(portfolio_record)
    if min(portfolio_record) > 0:
        min_port = min(portfolio_record)

    # calculate maximum port amount
    if len(portfolio_record) > x_lim:
        del (portfolio_record[0:-x_lim])
        del (ts_record[0:-x_lim])

# setting figure
style.use('dark_background')
fig = plt.figure()
fig.set_size_inches(18.5, 10.5)
ax1 = fig.add_subplot(111)

# different lines
cur_graph_min_line = ax1.axhline()
cur_graph_max_line = ax1.axhline()
max_line = ax1.axhline()
cur_line = ax1.axhline()

# path for the web driver -- using microsoft Edge
browser_path = "C:\\Users\\rahul\\Desktop\\LearningML\\msedgedriver.exe"
driver = webdriver.Edge(browser_path)
coin = 'WRX'
url = f"https://wazirx.com/exchange/{coin}-INR"
driver.get(url)
time.sleep(1)


def get_data():
    global max_port
    global min_port
    global counter
    global cur_graph_min_line
    global cur_graph_max_line
    global cur_line
    global max_line

    # get data from the webserver
    prices = [x.text[1:] for x in driver.find_elements_by_class_name('price-text')]
    tickers = [x.text for x in driver.find_elements_by_class_name('market-name-text')]
    ps = []
    for x in prices:
        ele = ''
        for y in x:
            if y == ',':
                pass
            else:
                ele += y
        ps.append(float(ele))

    # get current date
    ts = dt.now()
    ts = ts.strftime('%H:%M:%S')
    # create a dictionary to make my life less harder
    price_dic = dict(zip(tickers, ps))

    # get current price of each asset
    bnb_value = price_dic['BNB/INR']
    matic_value = price_dic['MATIC/INR']
    doge_value = price_dic['DOGE/INR']
    wrx_value = price_dic['WRX/INR']
    enj_value = price_dic['ENJ/INR']

    # calculate total amount
    total_amount = (bnb_value * bnb_amount) + (wrx_value * wrx_amount) + (enj_value * enj_amount) + (
            matic_value * matic_amount) + (doge_value * doge_amount)

    # if there was some error in data due to which there is outlier
    if total_amount - portfolio_record[-1] > 500 < total_amount - portfolio_record[-1]:
        return
    ts_record.append(ts)
    portfolio_record.append(total_amount)
    total_loss = invested - portfolio_record[-1]

    # update maximum, minimum portfolio if current record is larger or smaller
    if total_amount > max_port:
        max_port = total_amount
    if total_amount < min_port:
        min_port = total_amount

    # write files to the local file
    f = open(local_file_path, 'a')
    f.write(str(total_amount)[:8] + ' ')
    f.write(str(total_loss)[:8] + ' ')
    f.write(str(max_port)[:8] + ' ')
    f.write(str(min_port)[:8] + ' ')
    f.write(ts + '\n')
    f.close()

    counter += 1
    # saving figure offline
    if counter == 6:
        counter = 0
        fig.savefig('C:\\Users\\rahul\\Desktop\\Data\\cur_port.png')

    # remove all lines so they can be updated in next iteration
    cur_line.remove()
    max_line.remove()
    cur_graph_max_line.remove()
    cur_graph_min_line.remove()


def get_yticks():
    y_tck = []
    cur_max_p = max(portfolio_record)
    cur_p = portfolio_record[-1]
    min_p = min(portfolio_record)
    max_min_diff = (max_port - min_p) / 6
    y_tck.append(min_p)
    y_tck.append(min_p - max_min_diff)
    for x in range(1, 6):
        if abs(cur_max_p - (min_p + max_min_diff * x)) < max_min_diff:
            y_tck.append(cur_max_p)
        if abs(cur_p - (min_p + max_min_diff * x)) < max_min_diff and 100 < cur_p - min_p and cur_max_p - cur_p > 100:
            y_tck.append(cur_p)
        if abs(cur_p - (min_p + max_min_diff * x)) > 150 and abs(cur_max_p - (min_p + max_min_diff * x)) > 150:
            y_tck.append(min_p + max_min_diff * x)

    y_tck.append(max_port)
    y_tck.append(max_port + max_min_diff)
    return y_tck


def draw_data(i):
    global x_lim
    global cur_graph_min_line
    global cur_graph_max_line
    global cur_line
    global max_line
    global counter
    global max_port
    global min_port

    # get new data from web server
    get_data()
    # delete records older than 35 data points
    if len(portfolio_record) >= x_lim:
        del (portfolio_record[0])
        del (ts_record[0])
        plt.cla()

    low_limit = min(portfolio_record) - min(portfolio_record) * 0.01
    high_limit = max_port + max_port * 0.01
    plt.ylim(low_limit, high_limit)
    plt.xlabel('time')
    plt.ylabel('portfolio')
    plt.yticks(get_yticks())
    x_tick = np.linspace(1, x_lim-1, 10)
    plt.xticks(x_tick, rotation=55)

    # current portfolio
    current_port = portfolio_record[-1]

    # max and min portfolio from the previous 1000 records
    cur_graph_max_port = max(portfolio_record)
    cur_graph_min_port = min(portfolio_record)

    # calculate percentage market should grow to cover loss
    percentage_to_cover_loss = ((invested - current_port) / invested) * 100

    # minimum portfolio line (from the current graph)
    cur_graph_min_line = plt.axhline(y=cur_graph_min_port, color='#FF3377', alpha=1, label='Cur-Graph Min',
                                     linewidth=0.7)
    # if we have maximum portfolio in the current graph length
    if cur_graph_max_port != max_port:
        cur_graph_max_line = plt.axhline(y=cur_graph_max_port, color='#0092CC', alpha=0.7, label='Cur-Graph Max',
                                         linewidth=1)
    else:
        cur_graph_max_line = plt.axhline()
    # show invested line only when we reach near it
    if invested - max_port < 1000:
        spent_line = plt.axhline(y=invested, color='g', alpha=0.7, label='Invested', linestyle='-', linewidth=1.5)
    # maximum portfolio of all time
    max_line = plt.axhline(y=max_port, color='lightgreen', alpha=0.7, label='Max', linestyle='--', linewidth=0.8)

    # draw current portfolio line only when maximum portfolio is 100 bigger than current portfolio to avoid overlapping
    if max_port - current_port > 100 < current_port - cur_graph_min_port and cur_graph_max_port - current_port > 100:
        cur_line = plt.axhline(y=current_port, color='#FF3333', label='Current', linestyle='-', alpha=0.4,
                               linewidth=0.6)
    else:
        cur_line = plt.axhline()

    # set the title
    title = 'Market Down:{:.2f}%  Loss :{:.2f}  Max-Cur :{:.2f}'.format(percentage_to_cover_loss,
                                                                        invested - current_port,
                                                                        max_port - current_port)
    plt.title(title)
    ax1.plot(ts_record, portfolio_record, color='b', linewidth=1)
    ax1.legend()


ani = animation.FuncAnimation(fig, draw_data, interval=4000)
plt.show()
