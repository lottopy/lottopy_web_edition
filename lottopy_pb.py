# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
from math import comb
import pandas as pd
import requests
from collections import Counter
import csv

def get_data():
    # Old records from the excel sheets, wvlottery.com took these down but they go back to the early 90s on some games
    df_old = pd.read_excel('./excel_lotto_records/lotto.xlsx')
    salvaged = df_old[['Date', 'Numbers', 'PB']]

    url = 'https://gateway.loyalty.wvlottery.com/services/jackpot/api/v1/jackpot-results?gameId=12&jackpotStatus=PAYABLE&size=500&sort=externalId,drawDate,desc&page='
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    # Get web data, the new site pulls past draws from json 500 at a time
    web = {'Date': [], 'Numbers': [], 'PB': []}
    page = 0
    while True:
        r = requests.get(url + str(page), headers=header)
        data = r.json()
        for x in data['content']:
            web['Date'].append(x['drawingDate'])
            web['Numbers'].append('–'.join(str(n['data']) for n in x['resultData'] if n['type'] == 'REGULAR'))
            web['PB'].append([n['data'] for n in x['resultData'] if n['type'] == 'SPECIAL'][0])
        if data['last']:
            break
        page += 1
    dfs = [pd.DataFrame(web)]
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers', 'PB']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    PBs = list(df2['PB'].astype('int'))
    return date, nums, PBs

date, nums, PBs = get_data()

# Formatting 
# Site numbers come split by – and the excel records by - so it splits on both
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ').replace('-',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")
# Only count numbers that can still be called, the ball ranges have changed over the years
# so the old records have some numbers that dont exist in the game anymore
sep = [x for x in sep if x.isdigit() and 1 <= int(x) <= 69]
PBs = [x for x in PBs if 1 <= x <= 26]

for n in range(0, 69):
    most_common = Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 26):
    most_common_pb = Counter(PBs).most_common(1)
    PB = [v[0] for v in most_common_pb]
    frequency_pb = [v[-1] for v in most_common_pb]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
# Chance = 1 / every possible ticket, 69 choose 5 white balls times 26 powerballs = 292201338
# every ticket has the same odds, the forecast just goes with the numbers that get called the most
Chance = frac(1, comb(69, 5) * 26)
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} PB: {PB}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'PB', 'Chance')))
h = 'Forecast', 'PB', 'Chance'
f = open('pb_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)