# WVLottopy: Matteo DiBiagio
from sheet2dict import Worksheet
import pandas as pd
import requests
from collections import Counter

url = 'https://wvlottery.com/draw-games/powerball/?game-analyze=powerball&what-to-search=historysearch&date-range=-1'
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
df2 = df[['Date', 'Numbers', 'PB', 'PPX', 'Winners WV Only', 'Payout WV Only']]
# Print Table
#print(df2)

# To excel file
df2.to_excel('../lottopy/lotto.xlsx')

#Insert complete path to the excel file and index of the worksheet
df = pd.read_excel("lotto.xlsx", sheet_name=0)

# insert the name of the column as a string in brackets
date = list(df['Date']) 
nums = list(df['Numbers'].astype('str')) 
PB = list(df['PB'].astype('int'))
appearances = list(df2['Winners WV Only'].astype('int'))

# Index for each row 
index = [i for i in range(0,len(nums)*6)]

# Create an object
ws = Worksheet()

# Convert active sheet (without specifying sheet name)
ws.xlsx_to_dict(path='lotto.xlsx')

# Convert sheet of the 'lotto.xslx' spreadsheet file.
ws.xlsx_to_dict(path='lotto.xlsx', select_sheet='Sheet1')

# object.header returns first row with the data in a spreadsheet, object.sheet_items returns converted rows as dictionaries in the array 
#print(ws.header)
#print(ws.sheet_items)

# Formatting 
hyphenfree = []
for x in nums:
    hyphenfree.append(x.replace('-',', ')) 
splitlist = ", ".join(hyphenfree)
sep = splitlist.split(", ")

for n in range(0, 69):
    most_common= Counter(sep).most_common(5)
    likely_nums = [v[0] for v in most_common]
    frequency = [v[-1] for v in most_common]
    
for n in range(0, 26):
    most_common_pb = Counter(PB).most_common(1)
    likely_pb = [v[0] for v in most_common_pb]
    frequency_pb = [v[-1] for v in most_common_pb]

sorted_nums = sorted(likely_nums)
total_freq = sum(frequency + frequency_pb) 
chance  = [(total_freq / 292201338) * 100] # Chance = number call freq / all possible numbers i.e. 11238513

print("Likely numbers are . . . ", sorted_nums, "PB:", likely_pb, "\n", "With percent chance of winning being", chance[0]*100, "%")
