import glob
import json
import pandas as pd
import os
from helpers import batch, write_batches

all_cats = []
raw_data_dir = 'search_queries/script_generated'
prepped_data_dir = f'search_queries/prepped/'
for file in glob.glob(f'{raw_data_dir}/*_metadata.json'):
    with open(file, 'r', encoding='utf8') as f:
        meta = json.load(f)
    for meta_row in meta:
        print(meta_row)
        meta_date = meta_row['date']
        name = meta_row['name']
        cat = f'{name}_{meta_date}'.replace(':', '-')
        path = meta_row['raw'].replace('_raw_', '_df_').replace('.json', '.csv')

        with open(meta_row['raw'], 'r', encoding='utf8') as f:
            d = json.load(f)['default']
    
        if 'rankedList' in d:
            row_dicts = []
            ranked_list = d['rankedList']
            for row in ranked_list:
                data = row['rankedKeyword']
                for x in data:
                    x['date'] = meta_date
                    row_dicts.append(x)
            df = pd.DataFrame(row_dicts)

        if 'trendingSearchesDays' in d:
            trending_searches_days = d['trendingSearchesDays']
            trending_dicts = []
            related_dicts = []
            for day_dict in trending_searches_days:
                date = day_dict['date']
                for search in day_dict['trendingSearches']:
                    trending_dict = search['title']
                    trending_dict['formattedTraffic'] = search['formattedTraffic']
                    trending_dict['date'] = date
                    trending_dict['meta_data'] = meta_date
                    trending_dicts.append(trending_dict)
                    print(search['relatedQueries'])
                    if search['relatedQueries']:
                        related_dicts+= search['relatedQueries']
        
            df = pd.DataFrame(trending_dicts)
        write_batches(df['query'], cat, prepped_data_dir)
        all_cats.append({
            'name': name,
            'date': meta_date,
            'cat': cat,
        })
        df.to_csv(path, index=False)
        
        


for file in glob.glob(f'{raw_data_dir}/*_recurse*.csv'):
    df = pd.read_csv(file)
    root_query = list(df['root'].unique())[0]
    assert len(list(df['root'].unique())) == 1
    date = list(df['dateAtSave'].unique())[0]
    assert len(list(df['dateAtSave'].unique())) == 1
   # max_depth = df['depth'].max()

    date = date.replace('+00:00', 'Z').replace(' ', 'T')

    cat = os.path.basename(file).replace('.csv', '')
    cat = '_'.join(cat.split('_')[:-1]) + '_' + date.replace(':', '-')

    all_cats.append({
        'name': os.path.basename(file),
        'date': date,
        'cat': cat,
    })

    try:
        write_batches(df['target'], cat, prepped_data_dir)
    except AttributeError:
        print(f'Skipping {file} b/c attribute error (no autocomplete queries')

pd.DataFrame(all_cats).to_csv('query_selection_code/all_cats.csv', index=False)
pd.DataFrame(all_cats)['cat'].to_csv('query_selection_code/cat_names.txt', index=False)


