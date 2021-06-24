import time
from selenium import webdriver
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import os

portfolio_record = []
ts_record = []
max_port = 0
min_port = 100000
counter = 0

f = open('C:\\Users\\rahul\\Desktop\\Data\\portfolio.txt', 'r')
for record in f.readlines():
    portfolio_record.append(float(record[:8]))
    ts_record.append(record[-9:-1])
f.close()
max_port = max(portfolio_record)
if min(portfolio_record) > 0:
    min_port = min(portfolio_record)

if len(portfolio_record) > 35:
    del (portfolio_record[0:-35])
    del (ts_record[0:-35])

style.use('ggplot')
fig = plt.figure()
fig.set_size_inches(18.5, 10.5)
ax1 = fig.add_subplot(111)

# path for the web driver -- using microsoft Edge
browser_path = "C:\\Users\\rahul\\Desktop\\LearningML\\msedgedriver.exe"
# initialize the driver
driver = webdriver.Edge(browser_path)
coin = 'WRX'
url = f"https://wazirx.com/exchange/{coin}-INR"
driver.get(url)
time.sleep(1)

wrx_amount = 79.558112311
bnb_amount = 0.7711
enj_amount = 149.3
matic_amount = 112.0
doge_amount = 166.0


def get_data():
    global max_port
    global min_port
    f = open('C:\\Users\\rahul\\Desktop\\Data\\portfolio.txt', 'a')
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
    ts = dt.now()
    ts = ts.strftime('%H:%M:%S')
    ts_record.append(ts)
    price_dic = dict(zip(tickers, ps))
    bnb_value = price_dic['BNB/INR']
    matic_value = price_dic['MATIC/INR']
    doge_value = price_dic['DOGE/INR']
    wrx_value = price_dic['WRX/INR']
    enj_value = price_dic['ENJ/INR']
    total_amount = 0.0
    total_amount = (bnb_value * bnb_amount) + (wrx_value * wrx_amount) + (enj_value * enj_amount) + (
            matic_value * matic_amount) + (doge_value * doge_amount)
    if total_amount < 48000 or total_amount > 60000:
        pass
    portfolio_record.append(total_amount)
    total_loss = 70190 - portfolio_record[-1]

    if total_amount > max_port:
        max_port = total_amount
    if total_amount < min_port:
        min_port = total_amount
    f.write(str(total_amount)[:8] + ' ')
    f.write(str(total_loss)[:8] + ' ')
    f.write(str(max_port)[:8] + ' ')
    f.write(str(min_port)[:8] + ' ')
    f.write(ts + '\n')
    f.close()


def draw_data(i):
    global counter
    global max_port
    global min_port
    counter += 1
    get_data()
    # delete records older than 35 data points
    if len(portfolio_record) > 35:
        del (portfolio_record[0])
        del (ts_record[0])
        plt.cla()

    low_limit = min_port - min_port * 0.01
    high_limit = max_port + max_port * 0.01
    plt.ylim(low_limit, high_limit)
    plt.xlabel('time')
    plt.ylabel('portfolio')
    plt.xticks(rotation=55)
    title = 'Max : {:.2f}   Min : {:.2f}   Current :{:.2f}   Loss :{:.2f}'.format(max_port, min_port,
                                                                                  portfolio_record[-1],
                                                                                  70190 - portfolio_record[-1])
    plt.title(title)
    ax1.plot(ts_record, portfolio_record, color='r', marker='x', linewidth=.7)
    if counter == 6:
        counter = 0
        if os.path.exists('C:\\Users\\rahul\\Desktop\\Data\\cur_port.png'):
            os.remove('C:\\Users\\rahul\\Desktop\\Data\\cur_port.png')
        fig.savefig('C:\\Users\\rahul\\Desktop\\Data\\cur_port.png')
        

ani = animation.FuncAnimation(fig, draw_data, interval=5000)
plt.show()
