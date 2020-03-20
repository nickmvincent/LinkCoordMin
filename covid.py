import os
import glob
import pandas as pd

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
cat_df = pd.read_csv('query_selection_code/all_cats.csv')
cat_df = cat_df[cat_df.date >= '2020-03-19']
cat_df = cat_df[~cat_df.cat.str.contains('dailyTrends')]
cats = cat_df['cat']
print(cats)

locs = [
    'None'
]

configs = []

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

outdir = 'output/covidout_mar19'
for config in configs:
    cmds = []
    for search_engine in search_engines:
        device = config['device']
        cat = config['cat']
        loc = config['loc']
        file = config['file']        
        cmd = f"node collect.js --device={device} --platform={search_engine} --queryCat='{cat}' --queryFile={file} --geoName={loc} --outDir={outdir}"
        cmds.append(cmd)
    concat = ' & '.join(cmds) + ' & wait'
    print(concat)
    os.system(concat)
