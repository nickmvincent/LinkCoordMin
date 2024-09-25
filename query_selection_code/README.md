# For greggle project

* We'll just use the `trends.js` script without the stems. We don't use the suggestions.


# Collecting Google Trends data

* `recurse_suggests.py` uses from Ronaldson et al. (https://github.com/gitronald/suggests) to scrape queries from Google's autocompete
* `trends.js` uses the unofficial Google trends API (https://github.com/pat310/google-trends-api) to collect queries from Google Trends
* `script_generated_queries.py` takes the raw data from suggests and google-trends-api and creates easy-to-check csv files and `prepped`, ready-to-go keyword files.
* `reshape_queries.py` reshapes and `preps` the curated queries used in Vincent and Hecht 2020 (link goes here). 

To generate queries, you will need to install `suggests` from here: https://github.com/nickmvincent/suggests

# Steps to generate a set of queries
* First run `query_selection_code/trends.js` and `query_selection_code/recurse_suggests.py`
* If you successfully ran these two scripts, you will have populated data in `search_queries/script_generated`
* Now, run `query_selection_code/script_generated_queries.py`
* This will have populated "prepped" query files in `search_queries/prepped` that are ready for use by collect.js!

Now you can run collect.js by specifying a query category (e.g. `--queryCat=myCat`) and query file (e.g. `--queryFile=0` for `0.txt`)

