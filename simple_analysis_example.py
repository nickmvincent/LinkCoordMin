
#%% [markdown]
# See results_notebook.py for a more complicated analysis example (used to replicate some analyses from a previous SERP-related paper). 
# 
# This file is meant to provide a very quick starting point for writing up other analyses.


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
# we'll use pandas and friends for this quick analysis.


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

# %%
# new data will be in results/*. This is an example!
filename = 'example_Wed Oct 28 2020 16-21-08 GMT-0500 (Central Daylight Time).json'
with open(filename, 'r', encoding='utf8') as f:
    d = json.load(f)
d.keys()

#%%
# print all details except the actual links (which is huge)
{k: v for k, v in d.items() if k != 'linkElements'}

#%%
df = pd.DataFrame(d['linkElements'])
df.head()

#%%
from analyze_links import analyze_links_df
analyzed = analyze_links_df(df)
analyzed.head()

#%%
analyzed.domain.value_counts()