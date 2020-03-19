import suggests
import datetime
import pandas as pd

def helper(q='coronavirus', depth=1, source='google'):
    tree = suggests.get_suggests_tree(q, source=source, max_depth=depth)
    df = suggests.to_edgelist(tree)
    now = datetime.datetime.now(datetime.timezone.utc)
    df['dateAtSave'] = now
    df.to_csv(f'search_queries/script_generated/{q}_recurse{depth}_{source}_{now.timestamp()}.csv', encoding='utf8')

#helper()
stems = pd.read_csv('search_queries/prepped/covid_stems/0.txt', header=None)[0]
for stem in stems:
    print(stem)
    helper(stem, 1, 'bing')
    helper(stem, 1, 'google')
