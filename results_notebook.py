
#%% [markdown]
# # Quick links
# ## If you want to skip to a particular result in this notebook, search for the following terms
# * "What search engines were considered?" / "What devices were considered?" / "What query categories were considered?"
# * "What queries were made?"
# * "What Wikipedia links appeared in SERPs?"
# * "How many times does each Wikipedia link appear for each device and search engine?"
# * "How often did Wikipedia links appear in SERPs?"
# * "How often did Wikipedia links appear in certain locations of SERPs?" (e.g. above-the-fold, in the right-hand column, etc.
# 
# For the code that calculate incidence rates, see analyze_links.py



#%% [markdown]
# # Current data format
# Currently, the node.js scraping code (see collect.js)
# saves 3 result files per SERP scraped:
# * a .json file with 
# device object used by puppeteer ("device"), date collection started ("dateStr"),
# date of collection ("dataAtSave"), user-specified query category (queryCat),
# file queries came from ("queryFile"), device name ("deviceName"),
# url accessed ("link"), the search engine or website ("platform"),
# the query made ("target"), and finally, a huge array of link elements ("linkElements")
# * a .png file that is a full screenshot of the SERP
# * a .mhtml snapshot of the website that can be opened in a web browser (this is experimental, apparently)
# 
# Files are named by datetime of script start to avoid accidental overwrite.
# 
# This script (analysis.py) includes code which stitches together a visual representation of
# links and their coordinates (obtained using getBoundingClientRect) alongside screenshots
# so search can perform visual validation -- compare the link representation (easy to do quant analyses)
# with the png representation and make sure they match up!

#%% [markdown]
# # Looking at the data
# ## For a very quick glance, look at all the files in `quick_examples`
# ## Alternatively, can look through the entire `server_output` folder


#%%
# defaults
import json
import glob
from pprint import pprint
from collections import defaultdict
from urllib.parse import unquote
import os

# scipy
import pandas as pd
import numpy as np

# plotting / images
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from PIL import Image

# helpers for this project
from helpers import (
    infinite_defaultdict, recurse_print_infinitedict, extract,
    is_mobile,
)
from constants import CONSTANTS

DO_COORDS = False
SAVE_PLOTS = False

#%% [markdown]
# The heavy lifting of analysis is in "analyze_links.py"
# `analyze_links_df` function takes a dataframe of links
# and calculates the width, height, and normalized coordinates of each link element.
# It extracts the domain from each link (using urlparse(link).netloc, see helpers.py).
# Finally, it calculates a variety of incidence rates: how often are various
# domains appearing in the full page, above-the-fold, in the right column, etc.
# Above-the-fold, right-hand, etc. are calculated using the constants defined above
# such as common viewport heights for desktop and mobile devices.

#%%
from analyze_links import analyze_links_df

#%%
# Which experiments should we load?
device_names = [
    'Chrome on Windows',
    'iPhone X',
]


search_engines = [
    'google',
    'bing',
    #'duckduckgo',
    # 'yahoo' not yet tested, but probably works decently well.
]
query_sets = [
    #'top',
    #'med',
    #'trend',
    #'covid19',
]
query_sets = 'all'

outdir = 'covidout' # where are the files

    

#%% [markdown]
# Below: load all the files from specified directory
# and put then load them into the "full_df" dataframe

#%%
rows = []
for file in glob.glob(f'{outdir}/**/*.json', recursive=True):
    with open(file, 'r', encoding='utf8') as f:
        d = json.load(f)
    d['fileName'] = file
    rows.append(d)
full_df = pd.DataFrame(rows)
full_df.head(3)

#%% 
# ## "What search engines were considered?" / "What devices were considered?" / "What query categories were considered?"
print('Search engines and how many SERPs per search engine:')
print(full_df.platform.value_counts(), '\n')
print('Device names and how many SERPs per device:')
print(full_df.deviceName.value_counts(), '\n')
print('Query categories and how many SERPs per category:')
print(full_df.queryCat.value_counts(), '\n')
if query_sets == 'all':
    query_sets = list(full_df.queryCat.unique())

#%%
print(query_sets)

#%%
# Which SERPs are missing for each search engines?
pd.crosstab(full_df.platform, full_df.target)


#%%
configs = []
for device_name in device_names:
    for search_engine in search_engines:
        for query_cat in query_sets:
            configs.append({
                'device_name': device_name,
                'search_engine': search_engine,
                'query_cat': query_cat,
            })


#%%
# ## "What queries were made?"
print('Queries made and how many SERPs per query:')
print(full_df.target.value_counts().sort_index())

#%%
# we will have one dataframe full of links for each combination of device_name / search_engine / query_cat
# in each df, each row corresponds to a single <a> link element
dfs = infinite_defaultdict()
# this three-key dict will be use the following sequence of keys: device_name, search_engine, query_cat
errs = []
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']
    sub = full_df[
        (full_df.deviceName == device_name) &
        (full_df.platform == search_engine) & 
        (full_df.queryCat == query_cat) 
    ]
    links_rows = []
    print(device_name, search_engine, query_cat)
    for i, row in sub.iterrows():
        linkElements = row.linkElements
        #print(row)
        try:
            for x in linkElements:
                x['target'] = row.target
                x['device_name'] = device_name
                x['search_engine'] = search_engine
                x['query_cat'] = query_cat
                x['file_name'] = row.fileName
                x['date_str'] = row.dateStr
            links_rows += linkElements
        except TypeError: # (linkElements is NaN, and therefore a float)
            print('error')
            errs.append(row)
        
    links_df = pd.DataFrame(links_rows)

    dfs[device_name][search_engine][query_cat] = analyze_links_df(
        pd.DataFrame(links_df), is_mobile(device_name)
    )

#%%
errs

#%%
# for config in configs:
#     device_name = config['device_name']
#     search_engine = config['search_engine']
#     query_cat = config['query_cat']
#     tmp = dfs[device_name][search_engine][query_cat]
#     print(device_name, search_engine, query_cat)
#     print(tmp[tmp.error])


#%% [markdown]
# ## Let's see which links are most common

#%%
concat_all_domains = []
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']
    concat_all_domains.append(
        dfs[device_name][search_engine][query_cat][['domain']]
    )
print('Top 20 domains in all SERPs collected:')
concatted_domains = pd.concat(concat_all_domains)['domain']
print(concatted_domains.value_counts()[:20])


#%% [markdown]
# ## What Wikipedia links appeared in SERPs?
#%%
print('What are the Wikipedia links showing up on desktop?')
concat_wp_links = []
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']
    tmp = dfs[device_name][search_engine][query_cat]
    tmp = tmp[tmp.wikipedia_appears]
    tmp['norm_href'] = tmp.href.apply(
        lambda x: unquote(x.replace('http://', '').replace('https://', '').replace('.m.', '.'))
    )
    concat_wp_links.append(
        tmp
    )
concatted_wp_links = pd.concat(concat_wp_links)
concatted_wp_links['norm_href'].value_counts()



#%%
# How many times does each Wikipedia link appear for each device and search engine?
print('How many times does each Wikipedia link appear for each device and search engine?')
pd.crosstab(concatted_wp_links.norm_href, [concatted_wp_links.device_name, concatted_wp_links.search_engine])

# %%
print('How many times does each Wikipedia link appear for each device and search engine?')
tmp_tab = pd.crosstab(concatted_wp_links.norm_href, [concatted_wp_links.search_engine, concatted_wp_links.target])
for i, row in tmp_tab.iterrows():
    print(row[row > 0])
    print()


#%%
# to stitch together image files:
# source: https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python

#%% [markdown]
# the below code creates visualization of our scraped links
# critically, this means we can compare our links (used for quant analysis) 
# with actual screenshots of SERPs or actual SERPs.
# To facilitate even easier visual validation, the below code takes a sample of SERPS
# and stitches the coordinate visualization and SERP screenshot together.
# This is pretty slow, so there's a DO_COORDS flag to turn it off.

#%%
# create the coordinate visualization
if DO_COORDS:
    for config in configs:
        device_name = config['device_name']
        search_engine = config['search_engine']
        query_cat = config['query_cat']

        df = dfs[device_name][search_engine][query_cat]
        if type(df) == defaultdict:
            continue
        right_max = df['right'].max()
        bot_max = df['bottom'].max()
        ratio = bot_max / right_max
        k = f'{device_name}_{search_engine}_{query_cat}'
        print(k)

        available_targets = list(full_df[
            (full_df.deviceName == device_name) & (full_df.platform == search_engine) & (full_df.queryCat == query_cat)
        ].target)

        np.random.seed(0)
        chosen_ones = np.random.choice(available_targets, 5, replace=False)
        with open(f'reports/samples/{k}.txt', 'w', encoding='utf8') as f:
            f.write('\n'.join(chosen_ones))
        for target in available_targets + [None]:
            if target:
                subdf = df[df['target'] == target]
            else:
                subdf = df
            file_name = subdf.file_name.iloc[0]
            if target:
                assert len(set(subdf.file_name)) == 1
            fig, ax = plt.subplots(1, 1, figsize=(CONSTANTS['figure_width'], CONSTANTS['figure_width'] * ratio))
            plt.gca().invert_yaxis()
            add_last = []
            for i_row, row in subdf.iterrows():
                if row.width == 0 or row.height == 0:
                    continue
                x = row['left']
                y = row['bottom']
                width = row['width']
                height = row['height']
                domain = row['domain']

                if row['wikipedia_appears']:
                    # add it to the plot last so it is on top
                    add_last.append([domain, (x,y,), width, height])
                    
                else:
                    if row['platform_ugc']:
                        color = 'b'
                    # color internal search engine links as lightgray
                    if 'google' in domain or 'bing' in domain or 'duckduckgo' in domain:
                        color = 'lightgray'
                    else:
                        color = 'grey'
                    plt.annotate(domain, (x, y), color=color)
                    # Add the patch to the Axes
                    rect = matplotlib.patches.Rectangle((x,y),width,height,linewidth=1,edgecolor=color,facecolor='none')
                    ax.add_patch(rect)
            for domain, coords, width, height in add_last:
                plt.annotate(domain, coords, color='g')
                rect = matplotlib.patches.Rectangle(coords,width,height,linewidth=2,edgecolor=color,facecolor='none')
                ax.add_patch(rect)

            # kp line = lefthand width border.
            kp_line = CONSTANTS['lefthand_width']
            if is_mobile(device_name):
                scroll_line = CONSTANTS['mobile_lines']['noscroll_mg']
            else:
                scroll_line = CONSTANTS['desktop_lines']['noscroll_mg']
            plt.axvline(kp_line, color='r', linestyle='-')

            # show the right edge of the viewport
            plt.axvline(CONSTANTS['viewport_width'], color='k', linestyle='-')
            # show the page-fold
            plt.axhline(scroll_line, color='k', linestyle='-')

            overlay_file_name = f'{file_name}_overlay.png'
            if SAVE_PLOTS:
                plt.savefig(overlay_file_name)
            #plt.savefig(f'reports/overlays/{k}_{target}_{file_name}.png')

            plt.close()
            if target in chosen_ones:
                screenshot_path = file_name.replace('.json', '.png')
                # the overlay will be smaller
                #TODO
                try:
                    screenshot_img = Image.open(screenshot_path)
                    big_w, big_h = screenshot_img.size
                    overlay_img = Image.open(overlay_file_name)
                    small_w, small_h = overlay_img.size
                except FileNotFoundError: 
                    continue

                h_percent = (big_h/float(small_h))
                new_w = int((float(small_w) * float(h_percent)))
                resized_overlay = overlay_img.resize((new_w,big_h), Image.ANTIALIAS)

                total_width = new_w + big_w

                new_im = Image.new('RGB', (total_width, big_h))

                x_offset = 0
                for im in (screenshot_img, resized_overlay):
                    new_im.paste(im, (x_offset,0))
                    x_offset += im.size[0]
                new_im.save(f'reports/samples/concat_{k}_{target}.png')


#%%
# toss results in here for easy dataframe creation
row_dicts = [] # each row is one config: device_name / search_engine / query_cat (/geography?)
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']

    print(device_name, search_engine, query_cat)
    df = dfs[device_name][search_engine][query_cat]
    if type(df) == defaultdict:
        continue

    groupby = ['target', 'date_str']
    inc_rate = df.groupby(groupby).wikipedia_appears.agg(any).mean()
    inc = df.groupby(groupby).wikipedia_appears.agg(any).sum()
    total = df.groupby(groupby).wikipedia_appears.agg(any).count()

    rh_inc_rate = df.groupby(groupby).wikipedia_appears_rh.agg(any).mean()
    lh_inc_rate = df.groupby(groupby).wikipedia_appears_lh.agg(any).mean()

    if is_mobile(device_name):
        d = CONSTANTS['mobile_lines']
    else:
        d = CONSTANTS['desktop_lines']
    matches = set(df[df.wikipedia_appears == True]['target'])

    row_dict = {
        'query_cat': query_cat,
        'search_engine': search_engine,
        'device_name': device_name,
        'inc_rate': inc_rate,
        'inc': inc,
        'total': total,
        'rh_inc_rate': rh_inc_rate,
        'lh_inc_rate': lh_inc_rate,
        'matches': matches
    }
    for name in d.keys():
        row_dict[f'{name}_inc_rate'] = df.groupby(groupby)[f'wikipedia_appears_{name}'].agg(any).mean()
        row_dict[f'lh_{name}_inc_rate'] = df.groupby(groupby)[f'wikipedia_appears_lh_{name}'].agg(any).mean()
    for domain in [
        'twitter', 'youtube',
        'facebook',
    ]:
        row_dict[f'{domain}_inc_rate'] = df.groupby(groupby)[f'{domain}_appears'].agg(any).mean() 


    row_dicts.append(row_dict)
#%%
results_df = pd.DataFrame(row_dicts)
results_df.head(3)


#%% [markdown]
# ## How often did Wikipedia links appear in SERPs? (tabular)

#%%
results_df[
    ['device_name', 'search_engine', 'query_cat', 'inc_rate', 'inc', 'total']
]

#%%
print(results_df[results_df.search_engine == 'google'].matches.values)

#%%



# %%
FP = 'Full-page incidence'
RH = 'Right-hand incidence'
LH = 'Left-hand incidence'
AF_MG = 'Above-the-fold incidence'
AF_pretty = 'Above-the-fold incidence (lower bound - upper bound)'

LH_AF_pretty = 'Left-hand above-the-fold incidence (lower bound - upper bound)'
LH_AF_LB = 'Left-hand above-the-fold incidence (lower bound)' 
LH_AF_MG = 'Left-hand above-the-fold incidence'
LH_AF_UB = 'Left-hand above-the-fold incidence (upper bound)' 

AF_LB = 'Above-the-fold incidence (lower bound)'
AF_UB = 'Above-the-fold incidence (upper bound)'

cols = [
    'device_name', 'search_engine', 'query_cat', 'inc_rate', 'rh_inc_rate',
    'lh_inc_rate',
]
for name in CONSTANTS['mobile_lines'].keys():
    cols += [f'{name}_inc_rate', f'lh_{name}_inc_rate']
print(cols)

renamed = results_df[cols]
renamed.rename(columns={
    'device_name': 'Device', 'search_engine': 'Search Engine',
    'query_cat': 'Query Category', 'inc_rate': FP,
    'rh_inc_rate': RH,
    'lh_inc_rate': LH,
    'lh_noscroll_lb_inc_rate': LH_AF_LB,
    'lh_noscroll_mg_inc_rate': LH_AF_MG,
    'lh_noscroll_ub_inc_rate': LH_AF_UB,
    'noscroll_lb_inc_rate': AF_LB,
    'noscroll_mg_inc_rate': AF_MG,
    'noscroll_ub_inc_rate': AF_UB,
    'youtube_inc_rate': 'Youtube incidence rate',
    'twitter_inc_rate': 'Twitter incidence rate',
}, inplace=True)

def pretty_bounds(row):
    mg = row[AF_MG]
    lb = row[AF_LB]
    ub = row[AF_UB]
    return f'{mg:.2f} ({lb:.2f} - {ub:.2f})'

def pretty_bounds_lh(row):
    mg = row[LH_AF_MG]
    lb = row[LH_AF_LB]
    ub = row[LH_AF_UB]
    return f'{mg:.2f} ({lb:.2f} - {ub:.2f})'

renamed[AF_pretty] = renamed.apply(pretty_bounds, axis=1)
renamed[LH_AF_pretty] = renamed.apply(pretty_bounds_lh, axis=1)

renamed.replace(to_replace={
    'top': 'common',
    'med': 'medical',
    'trend': 'trending',
    'covid19': 'COVID-19'
}, inplace=True)
renamed

renamed[[
    'Device', 'Search Engine', 'Query Category',
    FP, RH, LH, AF_pretty, LH_AF_pretty
]].to_csv('reports/main.csv', float_format="%.2f", index=False)

#%%
renamed.head(3)

#%%
baseline_df = results_df[['device_name', 'search_engine', 'query_cat', 'twitter_inc_rate', 'youtube_inc_rate', 'facebook_inc_rate']]
baseline_df.rename(columns={
    'device_name': 'Device', 'search_engine': 'Search Engine',
    'query_cat': 'Query Category'
}, inplace=True)
baseline_df.to_csv('reports/other_domains.csv', float_format="%.2f", index=False)

#%%
melted = renamed.melt(id_vars=['Device', 'Search Engine', 'Query Category'])
#%%
melted.head(3)

#%% [markdown]
# ## How often did Wikipedia links appear in SERPs? (visual)
#%%
melted.rename(columns={
    'variable': 'y-axis',
    'value': 'Incidence rate',
}, inplace=True)
sns.set()
g = sns.catplot(
    x="Query Category", y='Incidence rate',
    hue="Search Engine", col="Device", row='y-axis',
    palette=['g', 'b', 'y'],
    #order=['COVID-19'],
    #row_order=[FP, AF, RH],
    data=melted[melted['y-axis'] == FP], kind="bar",
    height=3, aspect=1.5, ci=None,
    sharex=False,
)
if SAVE_PLOTS:
    plt.savefig('reports/FP_catplot.png', dpi=300)


#%% [markdown]
# ## How often did Wikipedia links appear in certain locations of SERPs?
#%%
# lh vs rh
g = sns.catplot(
    x="Query Category", y='Incidence rate',
    hue="Search Engine", col='y-axis', row='Device',
    col_order=[LH, RH],
    palette=['g', 'b', 'y'],
    #order=['common', 'trending', 'medical'],
    data=melted[
        ((melted['y-axis'] == LH) | (melted['y-axis'] == RH))
    ],
    kind="bar",
    height=3, aspect=1.5, ci=None,
    sharex=False,
)
if SAVE_PLOTS:
    plt.savefig('reports/LHRH_catplot.png', dpi=300)
#%%
# above-the fold middle ground
g = sns.catplot(
    x="Query Category", y='Incidence rate',
    hue="Search Engine", col="Device", row='y-axis',
    palette=['g', 'b', 'y'],
    #order=['common', 'trending', 'medical'],
    #row_order=[FP, AF, RH],
    data=melted[melted['y-axis'] == AF_MG], kind="bar",
    height=3, aspect=1.5, ci=None,
    sharex=False,
)
if SAVE_PLOTS:
    plt.savefig('reports/AF_catplot.png', dpi=300)

#%%
g = sns.catplot(
    x="Query Category", y='Incidence rate',
    hue="Search Engine", col="Device", row='y-axis',
    palette=['g', 'b', 'y'],
    #order=['common', 'trending', 'medical'],
    data=melted[melted['y-axis'] == LH_AF_MG], kind="bar",
    height=3, aspect=1.5, ci=None,
    sharex=False,
)
if SAVE_PLOTS:
    plt.savefig('reports/LH_AF_catplot.png', dpi=300)


# %%
# max difference between search engines
results_df.groupby(['device_name', 'query_cat']).agg(lambda x: max(x) - min(x))['inc_rate']

#%%
# max difference between devices
results_df.groupby(['search_engine', 'query_cat']).agg(lambda x: max(x) - min(x))['inc_rate']

#%%
# diff between FP and AF
melted[
    (melted['y-axis'] == FP) | (melted['y-axis'] == AF_MG)
].groupby(['Device', 'Query Category', 'Search Engine']).agg(lambda x: max(x) - min(x))

# %%
# what's in the first but not in the second

se_minus_se = {}
se_to_matches = {}
sub = results_df[(results_df.device_name == 'Chrome on Windows')]
for groupname, group in sub.groupby('query_cat'):
    print(groupname)
    for i, row in group.iterrows():
        se_to_matches[row.search_engine] = set(row.matches)
    se_to_matches
    for k1, v1 in se_to_matches.items():
        for k2, v2 in se_to_matches.items():
            if k1 == k2:
                continue
            se_minus_se[f'{k1}_{k2}'] = v1 - v2
    pprint(se_minus_se)


# %%
