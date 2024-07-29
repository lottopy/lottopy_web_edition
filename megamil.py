# WVLottopy megamil: Matteo DiBiagio
from fractions import Fraction as frac
import pandas as pd
import requests
from collections import Counter
from io import StringIO
import csv


def get_data():
    df_old = pd.read_excel('./excel_lotto_records/lotto_megamil.xlsx')
    salvaged = df_old[['Date', 'Numbers', 'MB']]

    url = 'https://wvlottery.com/draw-games/mega-millions/?game-analyze=mega-millions&what-to-search=historysearch&date-range=-1'
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    r = requests.get(url, headers=header)
    # Get web data
    dfs = list(pd.read_html(StringIO(r.text)))
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers', 'MB', 'MP']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    MBs = list(df2['MB'].astype('int'))
    return date, nums, MBs

date, nums, MBs = get_data()

# Formatting 
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")

for n in range(0, 70):
    most_common= Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 25):
    most_common_mb = Counter(MBs).most_common(1)
    MB = [v[0] for v in most_common_mb]
    frequency_mb = [v[-1] for v in most_common_mb]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
total_freq = sum(frequency + frequency_mb) 
Chance = frac(total_freq, 302575350) # Chance = number call freq / all possible numbers i.e. 11238513
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} MB: {MB}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'MB', 'Chance')))
h = 'Forecast', 'MB', 'Chance'
f = open('mm_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)
