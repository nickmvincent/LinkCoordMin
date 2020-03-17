import suggests 

def helper(q='coronavirus'):
    tree = suggests.get_suggests_tree(q, source='google', max_depth=3)
    df = suggests.to_edgelist(tree)
    df.to_csv(f'search_queries/script_generated/{q}_edgelist.csv', encoding='utf8')

#helper()
helper('COVID19')
