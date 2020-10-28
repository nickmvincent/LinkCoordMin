# About this Software
This software navigates to a web link, collects all the links, records their "coordinates" (their [getBoundingClientRect position](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect)), and saves this data alongside a screenshot of the page.

This coordinate data can be used to examine the "spatial incidence rate" of certain domains or content types (e.g. "How often do Stack Overflow links appear in the top half of a SERP"?, "How often do Wikipedia links appear in the right half of a SERP?" ). You could also use these coordinates to generate a "ranked list". However, for traditional ranking analyses, you may wish to examine software that includes platform-specific parsing.

While written with the goal of studying Search Engine Results pages (SERPs), in theory the software works for any website. See examples below for scraping Google and Bing's homepages.

It uses the open source [puppeteer](https://github.com/puppeteer/puppeteer/) library to automate headless browsing.


## Background
The basic concept of using puppeteer for SERP scraping is based on NikolaiT's library [se-scraper](https://github.com/NikolaiT/se-scraper). 

Key differences from se-scaper:
* This repo contains a separate, more minimal implementation of the link coordinate collection without the additional scraping features from `se-scraper` (e.g. use of [puppeteer-cluster](https://github.com/thomasdondorf/puppeteer-cluster), specific parsing rules for Google news, etc.).
* This repo focuses on spatial analysis, not ranking analyses. The results are links and their coordinates, not ranks. While this has some advantages, there are also limitations to using a spatial approach.
* This repo is currently maintained as a side-project by a grad student, and may not be updated as frequently as other similar packages. Contributions and feedback are welcome!


# Installation
## Pre-reqs
* node and npm (most recently run with node 10.15.3 and npm 6.4.1)
* python3 distribution (anaconda recommended)

To play with the results_notebook.py, you may want to use a Jupyter-compatible tool, e.g. JupyterLab or VSCode's notebook feature (https://code.visualstudio.com/docs/python/jupyter-support).

## Downloading node packages
To install relevant node packages into a local `node_modules` folder, navigate to this folder (e.g. `cd LinkCoordMin`) and run:

`npm install`

# Generating search queries
A critical part of studying SERPs is generating relevant search queries. This is a huge topic, so it has a separate README!

See README in `query_selection_code/`

# SERP Collection
The `collect.js` script runs SERP collection.

There are a variety of named command line args you can pass. Check out collect.js to most directly see the options, or use `collect.js -h`. You can also see examples below.

# Example Pipeline: 
See `EXAMPLE_RUN.sh` to see how you can 4 scripts in a sequence to programmatically generate queries and save SERP data for these queries.

# Specific Examples of SERP collection

To run script that
1) emulates iPhone X using puppeteer's Devices API (`--device=iphonex`)
2) searches the Google search engine (by visiting https://www.google.com/search&q=) ((`--platform=google`))
3) makes "covid_stems queries" (`--queryCat=covid_stems`)
4) from the `search_queries/prepped/covid_stems/0.txt` file (`--queryFile=0`)
5) from the `uw` location (university of washington lat / long /zip) (`--geoName=uw`)
6) to dir `test` (`--outDir=test`)

`node collect.js --device=iphonex --platform=google --queryCat=covid_stems --queryFile=0 --geoName=uw --outDir=test`


For bing & no location spoofing:
`node collect.js --device=iphonex --platform=bing --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output/test`

For bing on Chrome/Windows and a single test query (q = 'covid')
`node collect.js --device=chromewindows --platform=bing --queryCat=test --queryFile=0 --geoName=None --outDir=output/test0`


To run google and bing at the same time (using `&` for parallel):

`node collect.js --device=chromewindows --platform=google --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output/covidout_mar20 & node collect.js --device=chromewindows --platform=bing --queryCat=covid_stems --queryFile=0 --geoName=None --outDir=output/covidout_mar20 & wait`


This software can collect data for websites other than SERPs as well!

To scrape reddit, we just create a `queryCat` called reddit. The software will look at `search_queries/reddit/0.txt` and visit any websites listed there.
`node collect.js --device=chromewindows --platform=reddit --queryCat=reddit --queryFile=0 --geoName=None --outDir=output/reddit`

Similarly, to visit search engine homepages.
`node collect.js --device=chromewindows --platform=se --queryCat=homepages --queryFile=0 --geoName=None --outDir=output/reddit`

Note that --sleepMin and --sleepMax default to 15 and 30 (seconds) respectively. You may wish to make these larger for longer jobs to avoid being rate limited (see discussion in the [se-scraper repo](https://github.com/NikolaiT/se-scraper/issues/19)).


## Running many query categories with a python scirpt
* see `covid.py` for a script that collects a variety of COVID-19 related data. 
* This script is a useful template for running a bunch of tasks at once, or setting up regular data collection.


# Data visualization and analysis
* See `WikipediaSERP.html` for a worked example
* See `results_notebook.py` for details. If you're not using an Anaconda environment, you may need to `pip install` dependencies like pandas, matplotlib, etc.  

`results_notebook.py` is formatted for use with VsCode's [interactive jupyter notebook features](https://code.visualstudio.com/docs/python/jupyter-support). You can alternatively use the `results_notebook.ipynb` version (updated semi-regularly) or just run `results_notebook.py` as a Python script.

e.g. set SAVE_PLOTS to True, then run `results_notebook.py > my_results.txt`

# Known Issues and Debugging
* Location spoofing is inconsistent and the feature most likely to break. If performing any location-specific analyses, consider doing extra manaul validation for data quality!
* Bing mobile pages only loads top results (appears to be 4-6 items). The bottom half of the page is left with placeholder images, e.g. it hasn't loaded the full page yet. When this issue first arose, the "scrollDown" function seemed to fix it (issues scroll action til the bottom is reached).
* Reddit sometimes has issues loading
* Duckduckgo has some hard-to-replicate bugs when location spoofing.

## Using headfull mode for developmet
* Pass --headless=0
* This is very useful for debugging, you can watch the web browser in real time!
* If you are interested in helping to debug any issues with the software (including new issues that may arise as SERPs change), consider using headfull mode and watching the software "in action".

# Misc
* run `node tests/testStealth.js` to see how puppeteer-extra-stealth is doing. This library is meant to help puppeteer scripts avoid detection, i.e. so websites don't detect the script.






