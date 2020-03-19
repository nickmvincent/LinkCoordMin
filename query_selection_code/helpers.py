import pandas as pd
import os

#https://stackoverflow.com/a/40755160
def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def write_batches(s, name, save_folder):
    os.makedirs(f'{save_folder}/{name}', exist_ok=True)
    s = pd.Series(s.str.strip().unique())
    for i, chunk in enumerate(batch(s, 25)):
        name_i = f'{i}.txt'
        chunk.str.strip().to_csv(f'{save_folder}/{name}/{name_i}', index=False, header=False)