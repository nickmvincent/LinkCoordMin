
#%%
# defaults
import json
import glob
from pprint import pprint
from collections import defaultdict

# scipy
import pandas as pd
import numpy as np

# plotting / images
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from PIL import Image

# helpers for this project
from helpers import infinite_defaultdict, recurse_print_infinitedict, extract
from constants import CONSTANTS

#%% [markdown]
# The below function takes a dataframe of SERP / webpage links
# and calculates the width, height, and normalized coordinates.
# It extracts the domain from each link (using urlparse(link).netloc, see helpers.py).
# Finally, it calculates a variety of incidence rates: how often are various
# domain appearing in the full page, above-the-fold, in the right column, etc.
# Above-the-fold, right-hand, etc. are calculated using the constants defined above
# such as common viewport heights for desktop and mobile devices.

# to keep variables / column names short, there's some short hand here
# lh = left-hand
# rh = right-hand
# noscroll = above-the-fold
#%%

def prep_links_df(df, mobile=False):
    """
    TODO
    see above markdown
    """
    df['width'] = df.right - df.left
    df['height'] = df.bottom - df.top
    right_max = df['right'].max()
    bot_max = df['bottom'].max()

    # normalize all x-axis values relative to rightmost point
    for key in ['width', 'left', 'right']:
        df['norm_{}'.format(key)] = df[key] / right_max

    # normalize all y-axis values relative to bottommost point
    for key in ['height', 'top', 'bottom']:
        df['norm_{}'.format(key)] = df[key] / bot_max

    # treat links to DDG twitter & reddit as internal
    df.loc[df.href == 'https://twitter.com/duckduckgo', 'href'] = 'www.duckduckgo.com'
    df.loc[df.href == 'https://reddit.com/r/duckduckgo', 'href'] = 'www.duckduckgo.com'

    df['domain'] = df.apply(extract, axis=1)

    # flag UGC domains of note (can add more if desired)
    domains = [
        'wikipedia',
        'twitter', 'youtube',
        'facebook', 'reddit',
    ]

    df['platform_ugc'] = df['domain'].str.contains('|'.join(
        domains
    ))
    
    for domain in domains:
        df[f'{domain}_in'] = df['domain'].str.contains(domain)
        df[f'{domain}_appears'] = (
            df['domain'].str.contains(domain) &
            (df.width != 0) & (df.height != 0)
        )
        kp_line = CONSTANTS['lefthand_width'] / right_max
        if mobile:
            # no left-hand or right-hand incidence
            df[f'{domain}_appears_rh'] = 0
            # no lefthand above-the-fold incidence
            df[f'{domain}_appears_lh'] = 0
            for name, line in CONSTANTS['mobile_lines'].items():
                mobile_noscroll_line = line / bot_max

                df[f'{domain}_appears_{name}'] = (
                    (df[f'{domain}_appears']) &
                    (df.norm_top < mobile_noscroll_line)
                )

                df[f'{domain}_appears_lh_{name}'] = 0

        else:
            df[f'{domain}_appears_rh'] = (
                (df[f'{domain}_appears']) &
                (df.norm_left > kp_line)
            )

            df[f'{domain}_appears_lh'] = (
                (df[f'{domain}_appears']) &
                (df.norm_left <= kp_line)
            )

            for name, line in CONSTANTS['desktop_lines'].items():
                noscroll_line = line / bot_max

                df[f'{domain}_appears_{name}'] = (
                    (df[f'{domain}_appears']) &
                    (df.norm_top < noscroll_line)
                )

                df[f'{domain}_appears_lh_{name}'] = (
                    (df[f'{domain}_appears_lh']) &
                    (df.norm_top < noscroll_line)
                )
    return df


#%%
# Experiment parameters (which experiments to load)
device_names = [
    'Chrome on Windows',
    'iPhone X',
]
def is_mobile(device_name):
    """ is this device_name a mobile device"""
    return device_name in [
        'iPhone X', 'Galaxy S5',
    ]

search_engines = [
    'google',
    'bing',
    'duckduckgo',
]
query_sets = [
    #'top',
    #'med',
    #'trend',
    'covid19',
]
configs = []
for device_name in device_names:
    for search_engine in search_engines:
        for query_cat in query_sets:
            configs.append({
                'device_name': device_name,
                'search_engine': search_engine,
                'query_cat': query_cat,
            })
    

#%% [markdown]
# Below: load all the files from specified directory
# and put then load them into the "full_df" dataframe

#%%
rows = []
# where are the files
outdir = 'server_output'
for file in glob.glob(f'{outdir}/**/*.json', recursive=True):
    print(file)
    with open(file, 'r', encoding='utf8') as f:
        d = json.load(f)
    rows.append(d)
full_df = pd.DataFrame(rows)
full_df.head(3)

#%%
# we will have one df for each combination of device_name / search_engine / query_cat
dfs = infinite_defaultdict()
# this three-key dict will be use the following sequence of keys: device_name, search_engine, query_cat

for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']
    print(device_name, search_engine, query_cat)

    sub = full_df[
        (full_df.deviceName == device_name) &
        (full_df.platform == search_engine) & 
        (full_df.queryCat == query_cat) 
    ]
    links_rows = []
    for i, row in sub.iterrows():
        linkElements = row.linkElements
        for x in linkElements:
            x['target'] = row.target
        links_rows += row.linkElements

    links_df = pd.DataFrame(links_rows)

    dfs[device_name][search_engine][query_cat] = prep_links_df(pd.DataFrame(links_df), is_mobile(device_name))


#%% [markdown]
# Let's see which links are most common
#%%
# 
for_concat_list = []
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']
    for_concat_df = dfs[device_name][search_engine][query_cat][['domain']]
    for_concat_list.append(for_concat_df)
pd.concat(for_concat_list)['domain'].value_counts()[:15]


#%% [markdown]
# What are the Wikipedia links showing up on desktop?
#%%
tmp = dfs['Chrome on Windows']['bing']['covid19']
list(
    tmp[tmp.wikipedia_appears].href.apply(lambda x: x.replace('http://', '').replace('https://', '')).unique()
)

#%%
# to concat images:
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
DO_COORDS = False
if DO_COORDS:
    for config in configs:
        device_name = config['device_name']
        search_engine = config['search_engine']
        query_cat = config['query_cat']

        print(device_name, search_engine, query_cat)
        df = dfs[device_name][search_engine][query_cat]
        if type(df) == defaultdict:
            continue
        right_max = df['right'].max()
        bot_max = df['bottom'].max()
        ratio = bot_max / right_max
        k = f'{device_name}_{search_engine}_{query_cat}'

        available_targets = list(full_df[
            (full_df.deviceName == device_name) & (full_df.platform == search_engine) & (full_df.queryCat == query_cat)
        ].target)

        np.random.seed(0)
        chosen_ones = np.random.choice(available_targets, 1, replace=False)
        with open(f'reports/samples/{k}.txt', 'w', encoding='utf8') as f:
            f.write('\n'.join(chosen_ones))
        for target in available_targets + [None]:
            if target:
                subdf = df[df['target'] == target]
            else:
                subdf = df
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

            plt.savefig(f'reports/overlays/{k}_{target}.png')
            if target == 'nba':
                plt.savefig(f'reports/{k}_{target}.png')
            plt.close()
            if target in chosen_ones:
                screenshot_path = f'{outdir}/{device}/{search_engine}/{query_cat}/results.json_{target}.png'
                # the overlay will be smaller
                #TODO
                try:
                    screenshot_img = Image.open(screenshot_path)
                    big_w, big_h = screenshot_img.size
                    overlay_img = Image.open(f'reports/overlays/{k}_{target}.png')
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

                new_im.save(f'reports/samples/concat_{k}_{query_cat}.png')


#%%
# toss results in here for easy dataframe creation
row_dicts = []
for config in configs:
    device_name = config['device_name']
    search_engine = config['search_engine']
    query_cat = config['query_cat']

    print(device_name, search_engine, query_cat)
    df = dfs[device_name][search_engine][query_cat]
    if type(df) == defaultdict:
        continue

    inc_rate = df.groupby('target').wikipedia_appears.agg(any).mean()
    rh_inc_rate = df.groupby('target').wikipedia_appears_rh.agg(any).mean()
    lh_inc_rate = df.groupby('target').wikipedia_appears_lh.agg(any).mean()

    if device_name in ['iPhone X', 'Galaxy S5']:
        d = CONSTANTS['mobile_lines']
    else:
        d = CONSTANTS['desktop_lines']
    matches = set(df[df.wikipedia_appears == True]['target'])

    row_dict = {
        'query_cat': query_cat,
        'search_engine': search_engine,
        'device_name': device_name,
        'inc_rate': inc_rate,
        'rh_inc_rate': rh_inc_rate,
        'lh_inc_rate': lh_inc_rate,
        'matches': matches
    }
    for name in d.keys():
        row_dict[f'{name}_inc_rate'] = df.groupby('target')[f'wikipedia_appears_{name}'].agg(any).mean()
        row_dict[f'lh_{name}_inc_rate'] = df.groupby('target')[f'wikipedia_appears_lh_{name}'].agg(any).mean()
    for domain in [
        'twitter', 'youtube',
        'facebook',
    ]:
        row_dict[f'{domain}_inc_rate'] = df.groupby('target')[f'{domain}_appears'].agg(any).mean() 


    row_dicts.append(row_dict)
#%%
results_df = pd.DataFrame(row_dicts)
results_df

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
}, inplace=True)
renamed

renamed[[
    'Device', 'Search Engine', 'Query Category',
    FP, RH, LH, AF_pretty, LH_AF_pretty
]].to_csv('reports/main.csv', float_format="%.2f", index=False)

#%%
renamed[
    renamed.Device == 'desktop'
][[
    'Search Engine', 'Query Category',
    FP,  LH, RH, AF_pretty, LH_AF_pretty
]].to_csv('reports/desktop.csv', float_format="%.2f", index=False)
renamed[
    renamed.Device == 'mobile'
][[
    'Search Engine', 'Query Category',
    FP, AF_pretty
]].to_csv('reports/mobile.csv', float_format="%.2f", index=False)

#%%
renamed

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
melted

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
    #order=['common', 'trending', 'medical'],
    order=['covid19'],
    #row_order=[FP, AF, RH],
    data=melted[melted['y-axis'] == FP], kind="bar",
    height=3, aspect=1.5, ci=None,
    sharex=False,
)
plt.savefig('reports/FP_catplot.png', dpi=300)

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
plt.savefig('reports/LHRH_catplot.png', dpi=300)
#%%
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
plt.savefig('reports/AF_catplot.png', dpi=300)

#%%
g = sns.catplot(
    x="Query Category", y='Incidence rate',
    hue="Search Engine", col="Device", row='y-axis',
    palette=['g', 'b', 'y'],
    #order=['common', 'trending', 'medical'],
    data=melted[melted['y-axis'] == LH_AF_MG], kind="bar",
    height=2.5, aspect=1.5, ci=None,
    sharex=False,
)
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
sub = results_df[(results_df.device_name == 'Chrome on Windows') & (results_df.query_cat == 'covid19')]
for i, row in sub.iterrows():
    se_to_matches[row.search_engine] = set(row.matches)
se_to_matches
for k1, v1 in se_to_matches.items():
    for k2, v2 in se_to_matches.items():
        if k1 == k2:
            continue
        se_minus_se[f'{k1}_{k2}'] = v1 - v2

#%%
# what's in the first but not in the second

pprint(se_minus_se)


# %%
