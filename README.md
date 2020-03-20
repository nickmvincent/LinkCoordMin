# Installation
Pre-reqs:
* node and npm (most recently run with node 10.15.3 and npm 6.4.1)
* python3 distribution (anaconda recommended)

To play with the results_notebook.py, you may want to use a Jupyter-compatible tool, e.g. JupyterLab or VSCode's notebook feature.

To install relevant node packages into a local `node_modules` folder:

`npm install`

## Generating queries
See README in `query_selection_code/`

## SERP Collection
The `collect.js` script runs SERP collection.

There are a variety of named command line args you can pass. Check out collect.js to most directly see the options, or use `collect.js -h`.

### Examples

To run script that
1) emulates iPhone X using puppeteer's Devices API
2) searches the Google search engine (by visiting https://www.google.com/search&q=)
3) makes "medical queries"
4) from the `search_queries/prepped/med/med_sample3.txt` file
5) from the `uw` location (university of washington lat / long /zip)
6) to dir `out`

`node collect.js --device=iphonex --platform=google --queryCat=med --queryFile=med_sample3 --geoName=uw --outDir=output`

To run google and bing at the same time (using & for parallel):

`node collect.js --device=iphonex --platform=google --queryCat=med --queryFile=med_sample3 --geoName=uw --outDir=output & node collect.js --device=iphonex --platform=bing --queryCat=med --queryFile=med_sample3 --geoName=uw --outDir=output & wait`

This software can collect data for websites other than SERPs as well!
`node collect.js --device=chromewindows --platform=reddit --queryCat=reddit --queryFile=0 --geoName=None --outDir=output/reddit`


## Using headfull mode for developmet
* Pass --headless=false
* This is very useful for debugging, you can watch the web browser in real time!

## Misc
* run `node tests/testStealth.js` to see how puppeteer-extra-stealth is doing.


## Data visualization and analysis
* See `WikipediaSERP.html` for a worked example
* See `results_notebook.py` for details


