# WVLottopy: Matteo DiBiagio
from fractions import Fraction as frac
import pandas as pd
import records
import requests
from collections import Counter
import csv

def get_data():
    # previous records which have since been removed from wvlottery.com's database
    df_old = pd.read_excel('./excel_lotto_records/daily4.xlsx')
    salvaged = df_old[['Date', 'Numbers']]

    url = 'https://gateway.loyalty.wvlottery.com/services/jackpot/api/v1/jackpot-results?gameId=14&jackpotStatus=PAYABLE&size=500&sort=externalId,drawDate,desc&page='
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    }
    # Get web data, 500 draws a page
    web = {'Date': [], 'Numbers': []}
    page = 0
    while True:
        r = requests.get(url + str(page), headers=header)
        data = r.json()
        for x in data['content']:
            web['Date'].append(records.draw_day(x))
            web['Numbers'].append('–'.join(str(n['data']) for n in x['resultData'] if n['type'] == 'REGULAR'))
        if data['last']:
            break
        page += 1
    dfs = [pd.DataFrame(web)]
    pd.set_option('display.max_rows', None)
    # Specifies no max rows, otherwise only shows 10 records
    # adds new draws to the excel so the records keep growing
    df = records.merge_save('./excel_lotto_records/daily4.xlsx', dfs[0], fallback=salvaged)
    df2 = df[['Date', 'Numbers']]
    date = list(df2['Date']) 
    nums = list(df2['Numbers'].astype('str')) 
    return date, nums

date, nums = get_data()

# Formatting 
# site uses – and the excel uses -
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('–',', ').replace('-',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")
# gets rid of blanks from the excel
sep = [x for x in sep if x.isdigit() and int(x) <= 9]

for n in range(0, 9):
    most_common= Counter(sep).most_common(4)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]

sorted_nums = sorted(likely_nums, key=lambda x: (len(x), x))
Chance = frac(24, 10000) # box play, 24 ways out of 10000 (straight is 1/10000)
Forecast = str(" - ".join(sorted_nums))

#print(f"Likely numbers are . . .  {Forecast} \n"
#f"With percent chance of winning being {Chance}")

d = dict(((k, eval (k)) for k in ('Forecast','Chance')))
h = 'Forecast', 'Chance'
f = open('d4_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)