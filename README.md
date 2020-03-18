# Quick start
Pre-reqs:
node and npm (most recently run with node 10.15.3 and npm 6.4.1)
python3 distribution (anaconda recommended)

To generating queries, you will need to install `suggest` from here: https://github.com/gitronald/suggests
To play with the results_notebook.py, you may want to use a Jupyter-compatible tool, e.g. JupyterLab or VSCode's notebook features.

To install relevant node packages
`npm install`

## Generating queries
See code in `query_selection_code/`
* `recurse_suggests.py` uses from Ronaldson et al. (https://github.com/gitronald/suggests) to scrape queries from Google's autocompete
* `trends.js` uses the unofficial Google trends API (https://github.com/pat310/google-trends-api) to collect queries from Google Trends
* `script_generated_queries.py` takes the raw data from suggests and google-trends-api and creates easy-to-check csv files and `prepped`, ready-to-go keyword files.
* `reshape_queries.py` reshapes and `preps` the curated queries used in Vincent and Hecht 2020 (link goes here). 

## SERP Collection
To run script that
1) emulates iPhone X using puppeteer's Devices API
2) searches the Google search engine (by visiting https://www.google.com/search&q=)
3) makes "medical queries"
4) from the `search_queries/prepped/med/med_sample3.txt` file
5) from the `uw` location (university of washington lat / long /zip)
6) to dir `out`

`node collect.js iphonex google med med_sample3 uw output`

To run google and bing at the same time (using & for parallel)
`node collect.js iphonex google local local_0 uw localout & node collect.js iphonex bing local local_0 uw localout & wait`


## Misc
run `node tests/testStealth.js` to see how puppeteer-extra-stealth is doing.


## Data visualization and analysis
* See `WikipediaSERP.html` for a worked example
* See `results_notebook.py` for details