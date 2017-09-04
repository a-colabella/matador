# Matador Version 0.1
# By Andrew Colabella and Julian Costas
import urllib.request as ur
print("Matador (version 0.0.1)")
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
# RSI Variables
rsi_last_buy = None
rsibuys = 0
rsiprofit = 0
rsisells = 0

link_part1 = 'https://www.google.com/finance/getprices?i=3600&p='
link_part2 = "d&f=c&df=cpct&q="

# Ask user for ticker name
ticker = input("Enter the ticker name: ")
# Ask user for days analyzed
days = input("Enter the number of days you wish to analyze: ")
# 7 trading hours per day
period = int(days) * 7

# Import 50 Days
imported_length = 346

# Create full Google finance hyperlink based on users data
full_link = link_part1 + "50" + link_part2 + ticker
# Open Webpage
htmlfile = ur.urlopen(full_link)
htmltext = htmlfile.read()
# Parse Stock Data into a list
data = str(htmltext[120:])
data = data[1:]
data = data.replace('\\n', ' ')
data = data.replace('\'', '')
data = data.split()
data = list(map(float, data))
print(data)

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

#MAIN PROCESS

#SMA
in_portfolio = False
for i in range(1, upper_range):
    for j in range((i + 1), 21):
        for k in range(1, period):
            tick_n = imported_length - period + k
            short_sma = sma(data, tick_n, i)
            long_sma = sma(data, tick_n, j)
            if (short_sma > long_sma) and (in_portfolio == False):
                sma_buys = sma_buys + data[tick_n]
                sma_last_buy = tick_n
                in_portfolio = True

            if (long_sma > short_sma) and (in_portfolio == True):
                sma_sells = sma_sells + data[tick_n]
                in_portfolio = False

        if (in_portfolio == True):
            sma_profit = sma_sells - sma_buys + data[sma_last_buy]

        if (in_portfolio == False):
            sma_profit = sma_sells - sma_buys

        in_portfolio = False
        sma_sells = 0
        sma_buys = 0

        if (sma_profit > sma_max_profit):
            sma_max_profit = sma_profit
            sma_best_short = i
            sma_best_long = j
print("SMA Max Profit: " + str(sma_max_profit) + "   Best Short: " + str(sma_best_short) + "   Best Long: " + str(sma_best_long))

#macD
in_portfolio = False
for k in range(1, period):
    tick_n = imported_length - period + k
    macD = macD_line(data, tick_n)

    if (macD[0] > 0) and (in_portfolio == False):
        macdbuys = macdbuys + data[tick_n]
        macd_last_buy = tick_n
        in_portfolio = True

    if (macD[0] < 0) and (in_portfolio == True):
        macdsells = macdsells + data[tick_n]
        in_portfolio = False

if in_portfolio == True:
    macd_profit = macdsells - macdbuys + data[macd_last_buy]

if in_portfolio == False:
    macd_profit = macdsells - macdbuys

print("macD Profit: " + str(macd_profit))

#PPO
in_portfolio = False
for m in range(1, period):
    tick_n = imported_length - period + m
    ppo = ppo_value(data, tick_n)

    if (ppo[0] > 0) and (in_portfolio == False):
        ppobuys = ppobuys + data[tick_n]
        ppo_last_buy = tick_n
        in_portfolio = True

    if (ppo[0] < 0) and (in_portfolio == True):
        pposells = pposells + data[tick_n]
        in_portfolio = False

if in_portfolio == True:
    ppo_profit = pposells - ppobuys + data[ppo_last_buy]

if in_portfolio == False:
    ppo_profit = pposells - ppobuys

print("PPO Profit: " + str(ppo_profit))

#Aroon
in_portfolio = False
for g in range(lower_param, (upper_param + 1)):
    for h in range(1, period):
        tick_n = imported_length - period + h
        tick_high = highest(data, tick_n, g)
        tick_low = lowest(data, tick_n, g)
        aroonup = aroon_up(tick_n, g, tick_high)
        aroondown = aroon_down(tick_n, g, tick_low)
        if (aroonup > aroondown) and (aroonup[0] > 50) and (in_portfolio == False):
            aroonbuys = aroonbuys + data[tick_n]
            aroon_last_buy = tick_n
            in_portfolio = True

        if (aroondown > aroonup) and (aroondown[0] > 50) and (in_portfolio == True):
            aroonsells = aroonsells + data[tick_n]
            in_portfolio = False
    if in_portfolio:
        aroon_profit = aroonsells - aroonbuys + data[aroon_last_buy]

    if in_portfolio == False:
        aroon_profit = aroonsells - aroonbuys

    in_portfolio = False
    aroonsells = 0
    aroonbuys = 0

    if (aroon_profit > aroon_max_profit):
        aroon_max_profit = aroon_profit
        aroon_best_param = g

print("Aroon Profit: " + str(aroon_max_profit) + "   Best Parameter: " + str(aroon_best_param))

#RSI
in_portfolio = False
for a in range(1, period):
    tick_n = imported_length - period + a
    if tick_n == (imported_length - period + 1):
        av_gains = average_gains(data, tick_n)[0]
        av_losses = average_losses(data, tick_n)[0]
    else:
        av_gains = ((13 * prev_gain) + current_gain(data, tick_n)[0]) / 14
        av_losses = ((13 * prev_loss) + current_loss(data, tick_n)[0]) / 14

    prev_gain = av_gains
    prev_loss = av_losses
    rel_strength = av_gains/av_losses

    RSI = 100 - (100 / (1 + rel_strength))
    if (RSI <= 31) and (in_portfolio == False):
        rsibuys = rsibuys + data[tick_n]
        rsi_last_buy = tick_n
        in_portfolio = True

    if (RSI >= 69) and (in_portfolio == True):
        rsisells = rsisells + data[tick_n]
        in_portfolio = False

if in_portfolio == True:
    rsiprofit = rsisells - rsibuys + data[rsi_last_buy]

if in_portfolio == False:
    rsiprofit = rsisells - rsibuys

print("RSI Profit: " + str(rsiprofit))

input("\nPress any key to exit")