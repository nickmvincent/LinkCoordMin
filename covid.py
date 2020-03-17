import os
import glob

devices = [
    'chromewindows',
    'iphonex'
]

search_engines =[
    'google',
    'bing'
]

cats = [
    'coronavirus_Tue Mar 17 2020 01-03-34 GMT-0500 (Central Daylight Time)',
    #'COVID-19_Tue Mar 17 2020 01-03-34 GMT-0500 (Central Daylight Time)',
    'dailyTrendsTue Mar 17 2020 01-03-34 GMT-0500 (Central Daylight Time)',
    #'recurse_coronavirus',
]

locs = [
    'uw',
    'hancock',
    'None'
]

configs = []

for device in devices:
    for cat in cats:
        for 
        for loc in locs:
            configs.append({
                'device': device,
                'cat': cat,
                'loc': loc,
            })

for config in configs:
    cmds = []
    for search_engine in search_engines:
        device = config['device']
        cat = config['cat']
        # todo other indices
        cmd = f"node collect.js {device} {search_engine} '{cat}' 0 {loc}"
        cmds.append(cmd)
    concat = '& '.join(cmds)
    print(concat)
    os.system(concat)
