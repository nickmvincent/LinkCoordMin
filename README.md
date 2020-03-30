# Installation
This software navigates to a web link, collects all the links, records their "coordinates" (their [getBoundingClientRect position](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)), and saves this data alongside a screenshot of the page.

It uses the open source [puppeteer](https://github.com/puppeteer/puppeteer/) library to automate headless browsing.

Originally, I added this functionality to a fork of [se-scraper](https://github.com/NikolaiT/se-scraper). This repo contains a separate, more minimal implementation of the link coordinate collection without the additional scraping features from se-scraper (e.g. use of [puppeteer-cluster](https://github.com/thomasdondorf/puppeteer-cluster), specific parsing rules for Google news, etc.).


# Installation
## Pre-reqs
* node and npm (most recently run with node 10.15.3 and npm 6.4.1)
* python3 distribution (anaconda recommended)

To play with the results_notebook.py, you may want to use a Jupyter-compatible tool, e.g. JupyterLab or VSCode's notebook feature.

## Downloading node packages
To install relevant node packages into a local `node_modules` folder:
`npm install`

# Generating search queries
See README in `query_selection_code/`

# SERP Collection
The `collect.js` script runs SERP collection.

There are a variety of named command line args you can pass. Check out collect.js to most directly see the options, or use `collect.js -h`.

# Example Pipeline
See EXAMPLE_RUN.sh to see how you can 4 scripts in a sequence to programmatically generate queries and save SERP data for these queries.

## Examples

To run script that
1) emulates iPhone X using puppeteer's Devices API
2) searches the Google search engine (by visiting https://www.google.com/search&q=)
3) makes "medical queries"
4) from the `search_queries/prepped/med/med_sample3.txt` file
5) from the `uw` location (university of washington lat / long /zip)
6) to dir `out`

`node collect.js --device=iphonex --platform=bing --queryCat=covid_stems --queryFile=0 --geoName=uw --outDir=nicktest`


For bing:
`node collect.js --device=iphonex --platform=bing --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output`

To run google and bing at the same time (using & for parallel):

`node collect.js --device=chromewindows --platform=google --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output/covidout_mar20 & node collect.js --device=chromewindows --platform=bing --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output/covidout_mar20 & wait`


This software can collect data for websites other than SERPs as well!
`node collect.js --device=chromewindows --platform=reddit --queryCat=reddit --queryFile=0 --geoName=None --outDir=output/reddit`

Note that --sleepMin and --sleepMax default to 15 and 30 (seconds) respectively. You may wish to make these larger for longer jobs to avoid being rate limited (see discussion in the [se-scraper repo](https://github.com/NikolaiT/se-scraper/issues/19)).


# Using headfull mode for developmet
* Pass --headless=false
* This is very useful for debugging, you can watch the web browser in real time!

# Misc
* run `node tests/testStealth.js` to see how puppeteer-extra-stealth is doing.
* see `covid.py` for a script that collects a variety of COVID-19 related data. 
* This script is a useful template for running a bunch of tasks at once, or setting up regular data collection.


# Data visualization and analysis
* See `WikipediaSERP.html` for a worked example
See `results_notebook.py` for details. If you're not using an Anaconda environment, you may need to `pip install` dependencies like pandas, matplotlib, etc.  
`results_notebook.py` is formatted for use with VsCode's [interactive jupyter notebook features](https://code.visualstudio.com/docs/python/jupyter-support). You can alternatively use the `results_notebook.ipynb` version (updated semi-regularly) or just run `results_notebook.py` as a Python script.

e.g. set SAVE_PLOTS to True, then run `results_notebook.py > my_results.txt`



# Known Issues
* Bing mobile pages only loads top results (appears to be 4-6 items). The bottom half of the page is left with placeholder images, e.g. it hasn't loaded the full page yet. When this issue first arose, the "scrollDown" function seemed to fix it (issues scroll action til the bottom is reached).

