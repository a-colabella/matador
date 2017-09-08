# Matador Version 0.5
# By Andrew Colabella and Julian Costas
from tkinter import *
from tkinter import ttk
import urllib.request as ur
import operator
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
font = {'family' : 'arial',
        'weight' : 'normal',
        'size'   : 9}

matplotlib.rc('font', **font)
#Main window
root = Tk()
root.title('Matador (0.5)') #Version
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h)) #Fullscreen
root.state('zoomed')
#Frame
topFrame = Frame(root)
topFrame.pack(side=TOP, fill=X)
middleFrame = Frame(root)
middleFrame.pack()
bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)
#Ticker/Analyze
ticker_label = Label(topFrame, text="Ticker: ")
ticker_label.pack(side="left")
ticker_entry = Entry(topFrame)
ticker_entry.pack(side="left")
days_label = Label(topFrame, text="Days: ")
days_label.pack(side="left")
days_scale = Spinbox(topFrame, from_=1, to = 20)
days_scale.pack(side="left")
#Checkboxes
view_aroon = Checkbutton(topFrame, text="Aroon")
view_macd = Checkbutton(topFrame, text="MACD")
view_ppo = Checkbutton(topFrame, text="PPO")
view_sma = Checkbutton(topFrame, text="SMA")
view_sma.pack(side="right")
view_ppo.pack(side="right")
view_macd.pack(side="right")
view_aroon.pack(side="right")
#GRAPH FIGURE
plt.ion()
f = Figure(figsize=(8,3.5), dpi=100,tight_layout=TRUE)
a = f.add_subplot(1,1,1)
a.set_xlabel('Tick (Minute)')
a.set_ylabel('Price ($)')
canvas = FigureCanvasTkAgg(f,master=middleFrame)
toolbar = NavigationToolbar2TkAgg(canvas, middleFrame)
canvas.show()
canvas.get_tk_widget().pack()
f_volume = Figure(figsize=(8,1), dpi=100,tight_layout=TRUE)
a_volume = f_volume.add_subplot(1,1,1)
a_volume.set_ylabel('Volume')
canvas_volume = FigureCanvasTkAgg(f_volume,master=middleFrame)
canvas_volume.show()
canvas_volume.get_tk_widget().pack()
#Notebook of Indicators
nb = ttk.Notebook(bottomFrame, height = 100, width = (w-20), padding = 10)
stockdata_page = ttk.Frame(nb)
indicator_page = ttk.Frame(nb)
aroon_page = ttk.Frame(nb)
macd_page = ttk.Frame(nb)
ppo_page = ttk.Frame(nb)
sma_page = ttk.Frame(nb)
nb.add(stockdata_page, text='Stock Data')
nb.add(indicator_page, text='Profits')
nb.add(aroon_page, text='Aroon')
nb.add(macd_page, text='MACD')
nb.add(ppo_page, text='PPO')
nb.add(sma_page, text='SMA')
nb.grid(row=8)
#Textboxes
stockdata_text = Text(stockdata_page, width=600, height=200)
stockdata_text.pack()
indicator_text = Text(indicator_page, width=600,height=200)
indicator_text.pack()
aroon_text = Text(aroon_page, width=600,height=200)
aroon_text.pack()
macd_text = Text(macd_page, width=600,height=200)
macd_text.pack()
ppo_text = Text(ppo_page, width=600,height=200)
ppo_text.pack()
sma_text = Text(sma_page, width=600,height=200)
sma_text.pack()
main_link = 'https://www.google.com/finance/getprices?i=60&p=50d&f=c&df=cpct&q='
volume_link = 'https://www.google.com/finance/getprices?i=60&p=50d&f=v&df=cpct&q='

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
    imported_length = get_data.imported_length

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
    full_volume_link = volume_link + ticker_entry.get()
    period = int(days_scale.get())*1440
    # Open Webpage
    htmlfile = ur.urlopen(full_link)
    htmltext = htmlfile.read()
    #Open Volume Webpage
    volumefile = ur.urlopen(full_volume_link)
    volumetext = volumefile.read()
    # Parse Stock Data into a list
    if "NASDAQ" in str(htmltext):
        data = str(htmltext[118:])
        volume_data = str(volumetext[120:])
    elif "CURRENCY" in str(htmltext):
        data = str(htmltext[115:])
        volume_data = str(volumetext[117:])
    elif "NYSEARCA" in str(htmltext):
        data = str(htmltext[119:])
        volume_data = str(volumetext[121:])
    elif "NYSE" in str(htmltext):
        data = str(htmltext[116:])
        volume_data = str(volumetext[118:])

    data = data[1:]
    data = data.replace('\\n', ' ')
    data = data.replace('\'', '')
    data = data.split()
    data = list(map(float, data))
    volume_data = volume_data[1:]
    volume_data = volume_data.replace('\\n', ' ')
    volume_data = volume_data.replace('\'', '')
    volume_data = volume_data.split()
    volume_data = list(map(float, volume_data))
    stockdata_text.delete("1.0",END)
    indicator_text.delete("1.0",END)
    aroon_text.delete("1.0",END)
    macd_text.delete("1.0",END)
    ppo_text.delete("1.0",END)
    sma_text.delete("1.0",END)
    #Print Stock Data
    for i in range(0,len(data)):
        stockdata_text.insert(END, str(data[i]) + "\n")
    get_data.imported_length = len(data)
    #Axes for Graph
    x_axis = list(range(0,period))
    y_axis = []
    v_axis = []
    for ys in range (0, period):
        y_value = get_data.imported_length - period + ys
        y_axis.append(data[y_value])
    for vs in range (0, period):
        v_value = get_data.imported_length - period + vs
        v_axis.append(volume_data[v_value])

    #Draw new graph
    a.clear()
    a.set_xlabel('Tick (Minute)')
    a.set_ylabel('Price ($)')
    #markers_on = [120, 270, 800, 900]
    #a.plot(x_axis,y_axis, '-D', markevery=markers_on)
    a.plot(x_axis, y_axis)
    a.set_title(ticker_entry.get())
    a_volume.clear()
    a_volume.set_ylabel('Volume')
    a_volume.plot(x_axis,v_axis)
    plt.show()
    canvas.show()
    canvas_volume.show()
    toolbar.update()
    canvas._tkcanvas.pack()

    # SMA
    in_portfolio = False
    for i in range(1, upper_range):
        for j in range((i + 1), 21):
            sma_text.insert(END, "Short: " + str(i) + " Long: " + str(j) + "\n")
            for k in range(1, period):
                tick_n = get_data.imported_length - period + k
                short_sma = sma(data, tick_n, i)
                long_sma = sma(data, tick_n, j)
                hist_sma = sma(data, tick_n, j+12)
                stop_sma = sma(data, tick_n, j+10)
                if (short_sma > long_sma) and (long_sma > hist_sma) and (data[tick_n] > stop_sma[0]) and (in_portfolio == False):
                    sma_buys = sma_buys + data[tick_n]
                    sma_last_buy = tick_n
                    sma_text.insert(END, "Buys at: " + str(data[tick_n]) + "\n")
                    in_portfolio = True

                if (stop_sma[0] > data[tick_n]) and (in_portfolio == True):
                    sma_sells = sma_sells + data[tick_n]
                    sma_text.insert(END, "Sells at: " + str(data[tick_n]) + "\n")
                    in_portfolio = False

            if (in_portfolio == True):
                sma_profit = sma_sells - sma_buys + data[sma_last_buy]
                sma_text.insert(END, "Profit: " + str(sma_profit) + "\n\n")

            if (in_portfolio == False):
                sma_profit = sma_sells - sma_buys
                sma_text.insert(END, "Profit: " + str(sma_profit) + "\n\n")

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
        tick_n = get_data.imported_length - period + k
        macD = macD_line(data, tick_n)
        if (macD[0] > 0) and (in_portfolio == False):
            macdbuys = macdbuys + data[tick_n]
            macd_last_buy = tick_n
            macd_text.insert(END, "Buys at: " + str(data[tick_n]) + "\n")
            in_portfolio = True
        elif (macD[0] < 0) and (in_portfolio == True):
            macdsells = macdsells + data[tick_n]
            macd_text.insert(END, "Sells at: " + str(data[tick_n]) + "\n")
            in_portfolio = False

    if in_portfolio == True:
        macd_profit = macdsells - macdbuys + data[macd_last_buy]
        macd_text.insert(END, "Profit: " + str(macd_profit) + "\n")
    if in_portfolio == False:
        macd_profit = macdsells - macdbuys
        macd_text.insert(END, "Profit: " + str(macd_profit) + "\n")

    # PPO
    in_portfolio = False
    for m in range(1, period):
        tick_n = get_data.imported_length - period + m
        ppo = ppo_value(data, tick_n)

        if (ppo[0] > 0) and (in_portfolio == False):
            ppobuys = ppobuys + data[tick_n]
            ppo_last_buy = tick_n
            ppo_text.insert(END, "Buys at: " + str(data[tick_n]) + "\n")
            in_portfolio = True

        if (ppo[0] < 0) and (in_portfolio == True):
            pposells = pposells + data[tick_n]
            ppo_text.insert(END, "Sells at: " + str(data[tick_n]) + "\n")
            in_portfolio = False

    if in_portfolio == True:
        ppo_profit = pposells - ppobuys + data[ppo_last_buy]
        ppo_text.insert(END, "Profit: " + str(ppo_profit) + "\n")

    if in_portfolio == False:
        ppo_profit = pposells - ppobuys
        ppo_text.insert(END, "Profit: " + str(ppo_profit) + "\n")

    # Aroon
    in_portfolio = False
    for g in range(lower_param, (upper_param + 1)):
        aroon_text.insert(END, "Parameter: " + str(g) + "\n")
        for h in range(1, period):
            tick_n = get_data.imported_length - period + h
            tick_high = highest(data, tick_n, g)
            tick_low = lowest(data, tick_n, g)
            aroonup = aroon_up(tick_n, g, tick_high)
            aroondown = aroon_down(tick_n, g, tick_low)
            if (aroonup[0] > 50) and (aroondown[0] < 50) and (in_portfolio == False):
                aroonbuys = aroonbuys + data[tick_n]
                aroon_last_buy = tick_n
                aroon_text.insert(END, "Buys at: " + str(data[tick_n]) + "\n")
                in_portfolio = True
            elif (aroondown[0] > 50) and (aroonup[0] < 50) and (in_portfolio == True):
                aroonsells = aroonsells + data[tick_n]
                aroon_text.insert(END, "Sells at: " + str(data[tick_n]) + "\n")
                in_portfolio = False
        if in_portfolio:
            aroon_profit = aroonsells - aroonbuys + data[aroon_last_buy]
            aroon_text.insert(END, "Profit: " + str(aroon_profit) + "\n\n")

        if in_portfolio == False:
            aroon_profit = aroonsells - aroonbuys
            aroon_text.insert(END, "Profit: " + str(aroon_profit) + "\n\n")

        in_portfolio = False
        aroonsells = 0
        aroonbuys = 0

        if (aroon_profit > aroon_max_profit):
            aroon_max_profit = aroon_profit
            aroon_best_param = g
    aroon_text.insert(END, "\n\nMax Profit: " + str(aroon_max_profit) + " Best Parameter: " + str(aroon_best_param))
    sma_key = 'SMA Profit (Short: ' + str(sma_best_short) + ')(Long: ' + str(sma_best_long) + '): '
    aroon_key = 'Aroon Profit (Parameter: ' + str(aroon_best_param) + '): '
    indicators = {sma_key : sma_profit, 'macD Profit: ': macd_profit, 'PPO Profit: ': ppo_profit,
                  aroon_key: aroon_max_profit}
    sorted_x = sorted(indicators.items(), key=operator.itemgetter(1), reverse=True)
    for item in sorted_x:
        indicator_text.insert(END, str(item[0]) + str(item[1]) + "\n")

#Click button to run
analyze_button = Button(topFrame, text="Analyze", command=get_data)
analyze_button.pack(side="left")

#Show indicator graphs

#Keep on screen
root.mainloop()
