# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
import pandas as pd
import records
import requests
from collections import Counter
import csv

def get_data():
    url = 'https://gateway.loyalty.wvlottery.com/services/jackpot/api/v1/jackpot-results?gameId=24&jackpotStatus=PAYABLE&size=500&sort=externalId,drawDate,desc&page='
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    # Get web data, cash pop is drawn every 15 min so ~3000 draws is about a month
    web = {'Date': [], 'Numbers': []}
    ids, times = [], []
    page = 0
    while page < 6:
        r = requests.get(url + str(page), headers=header)
        data = r.json()
        for x in data['content']:
            web['Date'].append(records.draw_day(x))
            web['Numbers'].append('–'.join(str(n['data']) for n in x['resultData'] if n['type'] == 'REGULAR'))
            ids.append(x['externalId'])
            times.append(x['drawDate'])
        if data['last']:
            break
        page += 1
    df2 = pd.DataFrame(web)
    # site only keeps a year of cash pop, keep our own record
    records.merge_save('./excel_lotto_records/cash_pop.xlsx', df2, ids=ids, times=times)
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    return date, nums

date, nums = get_data()

# Formatting 
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")
# only 1 - 15
sep = [x for x in sep if x.isdigit() and 1 <= int(x) <= 15]

for n in range(0, 15):
    most_common= Counter(sep).most_common(3)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]

Forecast = likely_nums[0]
Backups = str(" - ".join(likely_nums[1:]))
Chance = frac(1, 15) # one number out of 15

#print(f"Likely number is . . .  {Forecast} Backups: {Backups}\n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast', 'Backups', 'Chance')))
h = 'Forecast', 'Backups', 'Chance'
f = open('cp_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)