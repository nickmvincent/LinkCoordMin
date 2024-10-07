import glob
import json
import pandas as pd
import os
import argparse
from datetime import datetime, timezone
from pytrends.request import TrendReq
import suggests

def get_suggested_queries_df(q, depth=1, source='google'):
    '''
    From Nick's recurse_suggests.py helper function
    '''
    tree = suggests.get_suggests_tree(q, source=source, max_depth=depth)
    df = suggests.to_edgelist(tree)
    now = datetime.now(timezone.utc)
    df['dateAtSave'] = now
    return df

def get_suggested_queries_list(kw):
    # use Ronaldson et al's suggests package
    # which Nick uses in addition to the related queries of Google API
    suggested = suggests.get_suggests(kw, source='google')
    return suggested['suggests']

def parse_args():
    parser = argparse.ArgumentParser(description='Create a dataset.')
    parser.add_argument('-i', '--input', help='File with paths to .txt stems.', default='', type=str)
    parser.add_argument('-o', '--output', help='The directory you want the queries to output to.', default='search_queries', type=str)
    parser.add_argument('-d', '--depth', help='Depth of our recursion. Default is 1.', default=1, type=int)
    args = parser.parse_args()
    return(args)

if __name__ == "__main__":
    args = parse_args()
    d = args.depth

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '..', args.output)

    # process dates
    today = datetime.now().date()
    start_stamp = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

    # i believe that nate's script will generate a tsv with 
    # paths to keywords that serve as our "stem" words.
    #TODO - sync up with Nate and figure out the exact input here.
    path_df = pd.read_csv(args.input,header=0,sep='\t')
    cats_paths = list(zip(path_df.cat, path_df.path))

    # i assume that each filepath in the tsv references
    # a .txt file (1 per category, which is also a col) with a short list of keywords
    # that are the base for the queries we will generate and then
    # scrape search results of. 
    # for now, i will also assume that each category only has one filepath per call.

    #cats_paths = [("test","sohw_test.txt")]

    for item in cats_paths:
        category = item[0]
        path = item[1]
        with open(path, 'r') as f:
            keywords = [line.strip() for line in f]
            print(keywords)

        category_queries = []
        for kw in keywords:
            # doing depth = 1 will give us a lot more queries than we proably need. need some kind of selection strategy.
            category_queries.append(get_suggested_queries_df(kw, depth=d))

        compiled_df = pd.concat(category_queries)
        output_file = f"{output_dir}/greggle_{category}_{today}.csv"
        compiled_df.to_csv(output_file, encoding='utf8')
        
        # this is from before when i was just outputting a text file. 
        # doing a csv for now, and we can decide if we want to change.
        # i mostly just want to talk about constraints + criteria we want to put on the generated queries
        #with open(output_file, 'w') as f:
            #for q in category_queries:
                #f.write(f"{q}\n")