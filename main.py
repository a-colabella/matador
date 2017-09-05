# Matador Version 0.3
# By Andrew Colabella and Julian Costas
from tkinter import *
from tkinter import ttk
import urllib.request as ur

#Main window
root = Tk()
root.title('Matador (0.3)')
root.geometry('500x400')
#Frame
topFrame = Frame(root)
topFrame.pack()
bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)
#Ticker/Analyze
ticker_label = Label(topFrame, text="Ticker: ")
ticker_label.grid(row=0, column=0, sticky=E)
ticker_entry = Entry(topFrame)
ticker_entry.grid(row=0, column=1)
days_label = Label(topFrame, text="Days: ")
days_label.grid(row=1, column=0, sticky=E)
days_scale = Spinbox(topFrame, from_=1, to = 20)
days_scale.grid(row=1,column=1)

#Notebook of Indicators
nb = ttk.Notebook(bottomFrame, height = 280, width = 450, padding = 10)
stockdata_page = ttk.Frame(nb)
aroon_page = ttk.Frame(nb)
macd_page = ttk.Frame(nb)
ppo_page = ttk.Frame(nb)
sma_page = ttk.Frame(nb)
nb.add(stockdata_page, text='Stock Data')
nb.add(aroon_page, text='Aroon')
nb.add(macd_page, text='macD')
nb.add(ppo_page, text='PPO')
nb.add(sma_page, text='SMA')
nb.pack()
#Textboxes
stockdata_text = Text(stockdata_page, width=400, height=300)
stockdata_text.pack()
aroon_text = Text(aroon_page, width=400,height=300)
aroon_text.pack()
macd_text = Text(macd_page, width=400,height=300)
macd_text.pack()
ppo_text = Text(ppo_page, width=400,height=300)
ppo_text.pack()
sma_text = Text(sma_page, width=400,height=300)
sma_text.pack()

imported_length = 50
main_link = 'https://www.google.com/finance/getprices?i=3600&p=50d&f=c&df=cpct&q='

# Simple moving average
def sma(prices, tick, time_frame):
    start_point = tick - time_frame
    total = sum(prices[start_point:tick])
    result = total / time_frame
    return [result]

# Exponential moving average
def ema(prices, tick, frame):
    result = 0
    previous = 0

    if frame == 12:
        multiplier = 0.1538
    elif frame == 26:
        multiplier = 0.0741
    elif frame == 9:
        multiplier = 0.2

    for z in range(0, frame):
        if ((tick + z) >= imported_length):
            result = (previous*(1 - multiplier))
        elif z == 0:
            result = prices[tick]
        else:
            result = (multiplier*prices[tick + z]) + (previous*(1 - multiplier))

        previous = result
    return [result]

# macD = ema12 - ema26
def macD_line(prices, tick):
    twelve = ema(prices, tick, 12)
    twenty_six = ema(prices, tick, 26)
    macd_result = twelve[0] - twenty_six[0]
    return [macd_result]

# ppo
def ppo_value(prices, tick):
    nine = ema(prices, tick, 9)
    twenty_six = ema(prices, tick, 26)
    ppo_result = (nine[0] - twenty_six[0]) / twenty_six[0]
    return [ppo_result]

# aroon up
def aroon_up(tick, frame, high_num):
    distance = tick - high_num[0]
    aroon_up_value = 100*((frame - distance)/frame)
    return [aroon_up_value]

# aroon down
def aroon_down(tick, frame, low_num):
    distance = tick - low_num[0]
    aroon_down_value = 100*((frame - distance)/frame)
    return [aroon_down_value]

# aroon highest
def highest(prices, tick, frame):
    high = 0
    high_tick = tick - frame
    for p in range(frame, 0, -1):
        if prices[tick - p] > high:
            high = prices[tick - p]
            high_tick = tick - p

    return [high_tick]

# aroon lowest
def lowest(prices, tick, frame):
    low = prices[tick - frame]
    low_tick = tick - frame
    for q in range(frame, 0, -1):
        if prices[tick - q] < low:
            low = prices[tick - q]
            low_tick = tick - q

    return [low_tick]

#average gains
def average_gains(prices, tick):
    gains = 0
    for w in range (13, 0, -1):
        if prices[tick - w] < prices[tick - (w - 1)]:
            gains = gains + prices[tick - (w - 1)] - prices[tick - w]

    av_gain = gains/14

    return [av_gain]

#average losses
def average_losses(prices, tick):
    loss = 0
    for f in range (13, 0, -1):
        if prices[tick - f] > prices[tick - (f - 1)]:
            loss = loss + prices[tick - f] - prices[tick - (f - 1)]

    av_loss = loss/14
    return [av_loss]

#current gain
def current_gain(prices, tick):
    cur_gain = 0
    if prices[tick] > prices[tick - 1]:
        cur_gain = prices[tick] - prices[tick - 1]

    return [cur_gain]

#current loss
def current_loss(prices, tick):
   cur_loss = 0
   if prices[tick] < prices[tick - 1]:
       cur_loss = prices[tick - 1] - prices[tick]

   return [cur_loss]

def get_data():
    upper_range = 20  # for SMA
    upper_param = 25  # for Aroon
    lower_param = 14  # for Aroon
    in_portfolio = None
    # SMA Variables
    sma_buys = 0
    sma_sells = 0
    sma_last_buy = None
    sma_profit = 0
    sma_max_profit = 0
    sma_best_long = None
    sma_best_short = None
    # macD Variables
    macd_last_buy = None
    macd_profit = 0
    macdbuys = 0
    macdsells = 0
    # PPO Variables
    ppobuys = 0
    pposells = 0
    ppo_last_buy = None
    ppo_profit = 0
    # Aroon Variables
    aroonbuys = 0
    aroonsells = 0
    aroon_last_buy = None
    aroon_best_param = None
    aroon_profit = 0
    aroon_max_profit = 0
    full_link = main_link + ticker_entry.get()
    period = int(days_scale.get())*7
    # Open Webpage
    htmlfile = ur.urlopen(full_link)
    htmltext = htmlfile.read()
    # Parse Stock Data into a list
    if "NASDAQ" in str(htmltext):
        data = str(htmltext[120:])
    elif "CURRENCY" in str(htmltext):
        data = str(htmltext[117:])
    elif "NYSE" in str(htmltext):
        data = str(htmltext[118:])

    data = data[1:]
    data = data.replace('\\n', ' ')
    data = data.replace('\'', '')
    data = data.split()
    data = list(map(float, data))
    stockdata_text.delete("1.0",END)
    aroon_text.delete("1.0",END)
    macd_text.delete("1.0",END)
    ppo_text.delete("1.0",END)
    sma_text.delete("1.0",END)

    for i in range(0,346):
        stockdata_text.insert(END, str(data[i]) + "\n")

    # SMA
    in_portfolio = False
    for i in range(1, upper_range):
        for j in range((i + 1), 21):
            sma_text.insert(END, "\n\nShort: " + str(i) + " Long: " + str(j))
            for k in range(1, period):
                tick_n = imported_length - period + k
                short_sma = sma(data, tick_n, i)
                long_sma = sma(data, tick_n, j)
                if (short_sma > long_sma) and (in_portfolio == False):
                    sma_buys = sma_buys + data[tick_n]
                    sma_last_buy = tick_n
                    sma_text.insert(END, "\nBuys at: " + str(data[tick_n]))
                    in_portfolio = True

                if (long_sma > short_sma) and (in_portfolio == True):
                    sma_sells = sma_sells + data[tick_n]
                    sma_text.insert(END, "\nSells at: " + str(data[tick_n]))
                    in_portfolio = False

            if (in_portfolio == True):
                sma_profit = sma_sells - sma_buys + data[sma_last_buy]
                sma_text.insert(END, "\nProfit: " + str(sma_profit))

            if (in_portfolio == False):
                sma_profit = sma_sells - sma_buys
                sma_text.insert(END, "\nProfit: " + str(sma_profit))

            in_portfolio = False
            sma_sells = 0
            sma_buys = 0

            if (sma_profit > sma_max_profit):
                sma_max_profit = sma_profit
                sma_best_short = i
                sma_best_long = j

    sma_text.insert(END, "\n\nSMA Max Profit: " + str(sma_max_profit) + "   Best Short: " + str(sma_best_short) + "   Best Long: " + str(sma_best_long))

    # macD
    in_portfolio = False
    for k in range(1, period):
        tick_n = imported_length - period + k
        macD = macD_line(data, tick_n)
        if (macD[0] > 0) and (in_portfolio == False):
            macdbuys = macdbuys + data[tick_n]
            macd_last_buy = tick_n
            macd_text.insert(END, "\nBuys at: " + str(data[tick_n]))
            in_portfolio = True
        elif (macD[0] < 0) and (in_portfolio == True):
            macdsells = macdsells + data[tick_n]
            macd_text.insert(END, "\nSells at: " + str(data[tick_n]))
            in_portfolio = False

    if in_portfolio == True:
        macd_profit = macdsells - macdbuys + data[macd_last_buy]
        macd_text.insert(END, "\nProfit: " + str(macd_profit))
    if in_portfolio == False:
        macd_profit = macdsells - macdbuys
        macd_text.insert(END, "\nProfit: " + str(macd_profit))

    # PPO
    in_portfolio = False
    for m in range(1, period):
        tick_n = imported_length - period + m
        ppo = ppo_value(data, tick_n)

        if (ppo[0] > 0) and (in_portfolio == False):
            ppobuys = ppobuys + data[tick_n]
            ppo_last_buy = tick_n
            ppo_text.insert(END, "\nBuys at: " + str(data[tick_n]))
            in_portfolio = True

        if (ppo[0] < 0) and (in_portfolio == True):
            pposells = pposells + data[tick_n]
            ppo_text.insert(END, "\nSells at: " + str(data[tick_n]))
            in_portfolio = False

    if in_portfolio == True:
        ppo_profit = pposells - ppobuys + data[ppo_last_buy]
        ppo_text.insert(END, "\nProfit: " + str(ppo_profit))

    if in_portfolio == False:
        ppo_profit = pposells - ppobuys
        ppo_text.insert(END, "\nProfit: " + str(ppo_profit))

    # Aroon
    in_portfolio = False
    for g in range(lower_param, (upper_param + 1)):
        aroon_text.insert(END, "\nParameter: " + str(g))
        for h in range(1, period):
            tick_n = imported_length - period + h
            tick_high = highest(data, tick_n, g)
            tick_low = lowest(data, tick_n, g)
            aroonup = aroon_up(tick_n, g, tick_high)
            aroondown = aroon_down(tick_n, g, tick_low)
            if (aroonup[0] > 50) and (aroondown[0] < 50) and (in_portfolio == False):
                aroonbuys = aroonbuys + data[tick_n]
                aroon_last_buy = tick_n
                aroon_text.insert(END, "\nBuys at: " + str(data[tick_n]))
                in_portfolio = True
            elif (aroondown[0] > 50) and (aroonup[0] < 50) and (in_portfolio == True):
                aroonsells = aroonsells + data[tick_n]
                aroon_text.insert(END, "\nSells at: " + str(data[tick_n]))
                in_portfolio = False
        if in_portfolio:
            aroon_profit = aroonsells - aroonbuys + data[aroon_last_buy]
            aroon_text.insert(END, "\nProfit: " + str(aroon_profit))

        if in_portfolio == False:
            aroon_profit = aroonsells - aroonbuys
            aroon_text.insert(END, "\nProfit: " + str(aroon_profit))

        in_portfolio = False
        aroonsells = 0
        aroonbuys = 0

        if (aroon_profit > aroon_max_profit):
            aroon_max_profit = aroon_profit
            aroon_best_param = g
    aroon_text.insert(END, "\n\nMax Profit: " + str(aroon_max_profit) + " Best Parameter: " + str(aroon_best_param))


#Click button to run
analyze_button = Button(topFrame, text="Analyze", command=get_data)
analyze_button.grid(row=2,column=1)

#Keep on screen
root.mainloop()
