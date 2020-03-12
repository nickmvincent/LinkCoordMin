#%%
import pandas as pd
import numpy as np
import os
load_folder = 'search_queries'
save_folder = 'search_queries/prepped'
n = 3
write_samples = True

#%%
from search_queries.georgetown_medical_bing import MED_QUERIES
med_df = pd.DataFrame(MED_QUERIES)
med_df

#%%
#https://stackoverflow.com/a/40755160
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def write_batches(s, name, save_folder):
    os.makedirs(f'{save_folder}/{name}', exist_ok=True)
    s = pd.Series(s.str.strip().unique())
    for i, chunk in enumerate(batch(s, 25)):
        name_i = f'{name}_{i}.txt'
        chunk.str.strip().to_csv(f'{save_folder}/{name}/{name_i}', index=False, header=False)



#%%
write_batches(med_df.sort_values(by=0)[0], 'med', save_folder)
#med_df[0].to_csv(f'{save_folder}/med.txt', index=False, header=False)


#%%


#%%
top_df = pd.read_csv(f'{load_folder}/ahrefs_top2019_google.txt', delimiter='\t', header=None)
top_df

#%%
write_batches(top_df[1], 'top', save_folder)


#%%
trends_df = pd.read_csv(f'{load_folder}/google_2018_queries.csv')
trends_df


# %%
melted = trends_df.melt(var_name='g', value_name='q')
melted.head()

# %%
melted['q'] = melted['q'].apply(lambda x: x[3:])
melted.head()

#%%
melted['q']

# %%
write_batches(melted['q'], 'trend', save_folder)
#melted[['q']].to_csv(f'{save_folder}/trend.txt', index=False, header=False)


# %%
if write_samples:
    melted.sample(n)[['q']].to_csv(f'{save_folder}/trend/trend_sample{n}.txt', index=False, header=False)
    med_df[0].sample(n).to_csv(f'{save_folder}/med/med_sample{n}.txt', index=False, header=False)
    top_df[1].sample(n).to_csv(f'{save_folder}/top/top_sample{n}.txt', index=False, header=False)


# %%
