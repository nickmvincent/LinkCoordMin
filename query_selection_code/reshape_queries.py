#%%
import pandas as pd
import numpy as np
import os
from helpers import batch, write_batches
load_folder = 'query_selection_code/curated'
save_folder = '../search_queries/prepped'
n = 3
write_samples = True

#%%
from georgetown_medical_bing import MED_QUERIES
med_df = pd.DataFrame(MED_QUERIES)
med_df

#%%




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

if __name__ == '__main__':
    pass
