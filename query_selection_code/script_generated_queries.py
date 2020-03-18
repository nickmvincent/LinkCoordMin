import glob
import json
import pandas as pd
from reshape_queries import write_batches

raw_data_dir = 'search_queries/script_generated'
prepped_data_dir = f'search_queries/prepped/'
for file in glob.glob(f'{raw_data_dir}/*.json'):
    with open(file, 'r', encoding='utf8') as f:
        d = json.load(f)['default']
    if 'rankedList' in d:
        row_dicts = []
        ranked_list = d['rankedList']
        for row in ranked_list:
            data = row['rankedKeyword']
            for x in data:
                #print(x)
                row_dicts.append(x)
        ranked_df = pd.DataFrame(row_dicts)
        ranked_path = file.replace('_raw_', '_df_').replace('.json', '.csv')
        print(ranked_df.head(3))
        ranked_df.to_csv(ranked_path, index=False)
        cat = file.replace(
            f'{raw_data_dir}/', ''
        ).replace('relatedQueries_raw_', '').replace('.json', '')

        write_batches(ranked_df['query'], cat, prepped_data_dir)

    if 'trendingSearchesDays' in d:
        trending_searches_days = d['trendingSearchesDays']
        trending_dicts = []
        related_dicts = []
        for day_dict in trending_searches_days:
            date = day_dict['date']
            for search in day_dict['trendingSearches']:
                trending_dict = search['title']
                trending_dict['formattedTraffic'] = search['formattedTraffic']
                trending_dicts.append(trending_dict)
                print(search['relatedQueries'])
                if search['relatedQueries']:
                    related_dicts+= search['relatedQueries']
        
        trending_df = pd.DataFrame(trending_dicts)
        trending_path = file.replace('_raw_', '_trendingdf_').replace('.json', '.csv')
        trending_df.to_csv(trending_path, index=False)
        
        #related_df = pd.DataFrame(related_dicts)
        # related_path = file.replace('_raw_', '_relateddf_').replace('.json', '.csv')
        # related_df.to_csv(related_path, index=False)

        cat = file.replace(
            f'{raw_data_dir}/', ''
        ).replace('_raw_', '').replace('.json', '')
        write_batches(trending_df['query'], cat, prepped_data_dir)


for file in glob.glob(f'{raw_data_dir}/*_edgelist.csv'):
    df = pd.read_csv(file)
    root_query = list(df['root'].unique())[0]

    write_batches(df['target'], f'recurse_{root_query}', prepped_data_dir)


