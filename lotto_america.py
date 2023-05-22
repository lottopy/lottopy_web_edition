# WVLottopy: Matteo DiBiagio
#from django_lottopy.lottopy_site.lottopy.lottopy_web_edition.megamil import Forecast
from fractions import Fraction as frac
import pandas as pd
import requests
from collections import Counter
import csv

def get_data():
    df_old = pd.read_excel('./excel_lotto_records/lotto_america.xlsx')
    salvaged = df_old[['Date', 'Numbers', 'SB']]

    url = 'https://wvlottery.com/draw-games/lotto-america/?game-analyze=lotto-america&what-to-search=historysearch&date-range=-1'
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
    }

    # Get web data
    dfs = list(pd.read_html(requests.get(url, headers=header).text))
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers', 'SB', 'All Star']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    SBs = list(df2['SB'].astype('int'))
    return date, nums, SBs

date, nums, SBs = get_data()

# Formatting 
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")

for n in range(0, 52):
    most_common= Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 10):
    most_common_sb = Counter(SBs).most_common(1)
    SB = [v[0] for v in most_common_sb]
    frequency_sb = [v[-1] for v in most_common_sb]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
total_freq = sum(frequency + frequency_sb) 
Chance = frac(total_freq, 25989600) # Chance = number call freq / all possible numbers i.e. 25,989,600
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} SB: {SB}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'SB', 'Chance')))
h = 'Forecast', 'SB', 'Chance'
f = open('la_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)

