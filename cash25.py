# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
from math import comb
import pandas as pd
import requests
from collections import Counter
import csv

def get_data():
    # Old records from the excel sheets, wvlottery.com took these down but they go back to the early 90s on some games
    df_old = pd.read_excel('./excel_lotto_records/cash25.xlsx')
    salvaged = df_old[['Date', 'Numbers']]

    url = 'https://gateway.loyalty.wvlottery.com/services/jackpot/api/v1/jackpot-results?gameId=10&jackpotStatus=PAYABLE&size=500&sort=externalId,drawDate,desc&page='
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    # Get web data, the new site pulls past draws from json 500 at a time
    web = {'Date': [], 'Numbers': []}
    page = 0
    while True:
        r = requests.get(url + str(page), headers=header)
        data = r.json()
        for x in data['content']:
            web['Date'].append(x['drawingDate'])
            web['Numbers'].append('–'.join(str(n['data']) for n in x['resultData'] if n['type'] == 'REGULAR'))
        if data['last']:
            break
        page += 1
    dfs = [pd.DataFrame(web)]
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    df = pd.concat([dfs[0], salvaged], ignore_index=True)
    df2 = df[['Date', 'Numbers']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    return date, nums

date, nums = get_data()

# Formatting 
# Site numbers come split by – and the excel records by - so it splits on both
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ').replace('-',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")
# Only count numbers that can still be called, the ball ranges have changed over the years
# so the old records have some numbers that dont exist in the game anymore
sep = [x for x in sep if x.isdigit() and 1 <= int(x) <= 25]

for n in range(0, 25):
    most_common= Counter(sep).most_common(6)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
# Chance = 1 / every possible ticket, 25 choose 6 = 177100
# every ticket has the same odds, the forecast just goes with the numbers that get called the most
Chance = frac(1, comb(25, 6))
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . . {Forecast} \n" 
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast','Chance')))
h = 'Forecast', 'Chance'
f = open('c25_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)