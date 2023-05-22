# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
import pandas as pd
import requests
from collections import Counter
import csv

def get_data():
    df_old = pd.read_excel('./excel_lotto_records/lotto.xlsx')
    salvaged = df_old[['Date', 'Numbers', 'PB', 'PPX', 'Winners WV Only', 'Payout WV Only']]

    url = 'https://wvlottery.com/draw-games/powerball/?game-analyze=powerball&what-to-search=historysearch&date-range=-1'
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    # Get web data
    dfs = list(pd.read_html(requests.get(url, headers=header).text))
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers', 'PB', 'PPX', 'Winners WV Only', 'Payout WV Only']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    PBs = list(df2['PB'].astype('int'))
    return date, nums, PBs

date, nums, PBs = get_data()

# Formatting 
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")

for n in range(0, 69):
    most_common = Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 26):
    most_common_pb = Counter(PBs).most_common(1)
    PB = [v[0] for v in most_common_pb]
    frequency_pb = [v[-1] for v in most_common_pb]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
total_freq = sum(frequency + frequency_pb) 
Chance = frac(total_freq, 292201338) # Chance = number call freq / all possible numbers i.e. 292201338
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} PB: {PB}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'PB', 'Chance')))
h = 'Forecast', 'PB', 'Chance'
f = open('pb_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)