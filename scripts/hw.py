import os
import glob
import pandas as pd
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--out_dir", help="name of folder for outputs", default='output/hw_apr2021')

# Ex:
# python hw.py
# Simplified this one by removing cats_file, data_gte.

args = parser.parse_args()
print(args)

devices = [
    'chromewindows',]

search_engines =[
    'google',
    'bing',
]

cats = [
    'hw_nice'
]

locs = [
    'None'
]

configs = []

print(f'Writing to {args.out_dir}')

for device in devices:
    for loc in locs:
        for cat in cats:
            files = glob.glob(f'search_queries/prepped/{cat}/*.txt')
            for file in files:
                keyword_filename = os.path.basename(file).replace('.txt', '')
                configs.append({
                    'device': device,
                    'cat': cat,
                    'loc': loc,
                    'file': keyword_filename,
                })

for config in configs:
    cmds = []
    for search_engine in search_engines:
        device = config['device']
        cat = config['cat']
        loc = config['loc']
        file = config['file']        
        cmd = f"node collect.js --device={device} --platform={search_engine} --queryCat='{cat}' --queryFile={file} --geoName={loc} --outDir={args.out_dir}"
        cmds.append(cmd)
    concat = ' & '.join(cmds) + ' & wait'
    print(concat)
    os.system(concat)


# node collect.js --device=chromewindows --platform=bing --queryCat='hw_nice' --queryFile=Algorithm_Design_Manual_Chapter_3 --geoName=None --outDir=output/test