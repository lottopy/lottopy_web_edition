# WVLottopy: Matteo DiBiagio
#from django_lottopy.lottopy_site.lottopy.lottopy_web_edition.megamil import Winning_Numbers
from fractions import Fraction as frac
from sheet2dict import Worksheet
import pandas as pd
import requests
from collections import Counter
import csv

url = 'https://wvlottery.com/draw-games/lotto-america/?game-analyze=lotto-america&what-to-search=historysearch&date-range=-1'
header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

# Get web data
r = requests.get(url, headers=header)
dfs = pd.read_html(r.text)
pd.set_option('display.max_rows', None)
# Specifies no max rows, otherwise only shows 10 records
#print(len(dfs))
df = dfs[0]
df2 = df[['Date', 'Numbers', 'SB', 'All Star']]
# Print Table
#print(df2)

# To excel file
df2.to_excel('./lotto_america.xlsx')

#Insert complete path to the excel file and index of the worksheet
df = pd.read_excel("lotto_america.xlsx", sheet_name=0)

# insert the name of the column as a string in brackets
date = list(df['Date']) 
nums = list(df['Numbers'].astype('str')) 
PBs = list(df['SB'].astype('int'))
#appearances = list(df2['Winners WV Only'].astype('int'))

# Index for each row 
index = [i for i in range(0,len(nums)*6)]

# Create an object
ws = Worksheet()

# Convert active sheet (without specifying sheet name)
ws.xlsx_to_dict(path='lotto_america.xlsx')

# Convert sheet of the 'lotto.xslx' spreadsheet file.
ws.xlsx_to_dict(path='lotto_america.xlsx', select_sheet='Sheet1')

# object.header returns first row with the data in a spreadsheet, object.sheet_items returns converted rows as dictionaries in the array 
#print(ws.header)
#print(ws.sheet_items)

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
    most_common_pb = Counter(PBs).most_common(1)
    SB = [v[0] for v in most_common_pb]
    frequency_pb = [v[-1] for v in most_common_pb]

sorted_nums = sorted(likely_nums)
total_freq = sum(frequency + frequency_pb) 
Chance = frac(total_freq, 25989600) # Chance = number call freq / all possible numbers i.e. 11238513
Winning_Numbers = str("-".join(sorted_nums))

#print("Likely numbers are . . . ", sorted_nums, "SB:", likely_pb, "\n", "With percent chance of winning being", chance[0]*100, "%")
d = dict(((k, eval (k)) for k in ('Winning_Numbers', 'SB', 'Chance')))
h = 'Winning_Numbers', 'SB', 'Chance'
f = open('la_ans.csv', 'w', encoding='utf_8')
writer = csv.DictWriter(f, fieldnames=h)
writer.writeheader()
writer.writerow(d)

