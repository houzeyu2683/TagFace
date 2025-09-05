import os
import pandas
import glob

# loop = [
#     './download/【數位主播午報】ok/#fragment/', 
#     './download/【數位主播晚報】ok/#fragment/', 
#     './download/【新聞抓重點】 新聞特報ok/#fragment', 
#     './download/【楊惠宇分析師-五福臨門】-doing/#fragment'
# ]
# for folder in loop:
#     for path in glob.glob(os.path.join(folder, '*.csv')):
#         sheet = pandas.read_csv(path)
#         sheet.columns = ['head', 'tail']
#         sheet.to_csv(path, index=False)
#         continue
#     continue


loop = [
    './download/【數位主播午報】ok/#face/', 
    './download/【數位主播晚報】ok/#face/', 
    './download/【新聞抓重點】 新聞特報ok/#face', 
    './download/【楊惠宇分析師-五福臨門】-doing/#face'
]
for folder in loop:
    for path in glob.glob(os.path.join(folder, '*.csv')):
        sheet = pandas.read_csv(path)
        sheet.columns = ['interval', 'region', 'delta']
        sheet.to_csv(path, index=False)
        continue
    continue