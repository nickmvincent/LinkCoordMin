import os
import glob
import pandas as pd
import argparse
parser = argparse.ArgumentParser()
# TODO: create args for: devices, platforms, locs
parser.add_argument("--date_gte", help="what date to grab queries from, as a YYYY-MM-DD string", default='2020-03-20')
parser.add_argument("--cats_file", help="File with category data", default='query_selection_code/all_cats.csv')
parser.add_argument("--out_dir", help="name of folder for outputs", default='output/covidout_mar20')

# Ex:
# python covid.py --date_gte=2020-03-22 --out_dir=output/covidoutmar22



args = parser.parse_args()
print(args)

devices = [
    'chromewindows',
    'iphonex'
]

search_engines =[
    'google',
    'bing',
    #'yahoo',
    #'duckduckgo',
]

# could be DB call here, or a mnaully set cats = [...]
cat_df = pd.read_csv(args.cats_file)
cat_df = cat_df[cat_df.date >= args.date_gte]
#cat_df = cat_df[~cat_df.cat.str.contains('dailyTrends')]
cats = list(cat_df['cat'])
print(cats)
cats += ['covid_stems', 'reddit']

locs = [
    'None'
]

configs = []

print(f'Reading cats from {args.cats_file} created after {args.date_gte}')
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
