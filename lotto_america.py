# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
from math import comb
import pandas as pd
import requests
from collections import Counter
import csv

def get_data():
    # Old records from the excel sheets, wvlottery.com took these down but they go back to the early 90s on some games
    df_old = pd.read_excel('./excel_lotto_records/lotto_america.xlsx')
    salvaged = df_old[['Date', 'Numbers', 'SB']]

    url = 'https://gateway.loyalty.wvlottery.com/services/jackpot/api/v1/jackpot-results?gameId=16&jackpotStatus=PAYABLE&size=500&sort=externalId,drawDate,desc&page='
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    # Get web data, the new site pulls past draws from json 500 at a time
    web = {'Date': [], 'Numbers': [], 'SB': []}
    page = 0
    while True:
        r = requests.get(url + str(page), headers=header)
        data = r.json()
        for x in data['content']:
            web['Date'].append(x['drawingDate'])
            web['Numbers'].append('–'.join(str(n['data']) for n in x['resultData'] if n['type'] == 'REGULAR'))
            web['SB'].append([n['data'] for n in x['resultData'] if n['type'] == 'SPECIAL'][0])
        if data['last']:
            break
        page += 1
    dfs = [pd.DataFrame(web)]
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers', 'SB']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    SBs = list(df2['SB'].astype('int'))
    return date, nums, SBs

date, nums, SBs = get_data()

# Formatting 
# Site numbers come split by – and the excel records by - so it splits on both
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ').replace('-',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")
# Only count numbers that can still be called, the ball ranges have changed over the years
# so the old records have some numbers that dont exist in the game anymore
sep = [x for x in sep if x.isdigit() and 1 <= int(x) <= 52]
SBs = [x for x in SBs if 1 <= x <= 10]

for n in range(0, 52):
    most_common= Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 10):
    most_common_sb = Counter(SBs).most_common(1)
    SB = [v[0] for v in most_common_sb]
    frequency_sb = [v[-1] for v in most_common_sb]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
# Chance = 1 / every possible ticket, 52 choose 5 white balls times 10 star balls = 25989600
# every ticket has the same odds, the forecast just goes with the numbers that get called the most
Chance = frac(1, comb(52, 5) * 10)
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} SB: {SB}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'SB', 'Chance')))
h = 'Forecast', 'SB', 'Chance'
f = open('la_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)

