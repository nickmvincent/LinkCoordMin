import suggests 
import datetime

def helper(q='coronavirus', depth=1):
    tree = suggests.get_suggests_tree(q, source='google', max_depth=depth)
    df = suggests.to_edgelist(tree)
    now = datetime.datetime.now(datetime.timezone.utc)
    df['dateAtSave'] = now
    df.to_csv(f'search_queries/script_generated/{q}_recurse{depth}_{now.timestamp()}.csv', encoding='utf8')

#helper()
helper('coronavirus', 1)
helper('coronavirus', 2)
