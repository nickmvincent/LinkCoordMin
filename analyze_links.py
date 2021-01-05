#%%
from helpers import extract
from my_constants import CONSTANTS


#%% [markdown]
# The below function takes a dataframe of SERP / webpage links
# and calculates the width, height, and normalized coordinates.
# It extracts the domain from each link (using urlparse(link).netloc, see helpers.py).
# Finally, it calculates a variety of incidence rates: how often are various
# domains appearing in the full page, above-the-fold, in the right column, etc.
# Above-the-fold, right-hand, etc. are calculated using the constants defined above
# such as common viewport heights for desktop and mobile devices.

# to keep variables / column names short, there's some short hand here
# lh = left-hand
# rh = right-hand
# noscroll = above-the-fold
#%%

def analyze_links_df(df, mobile=False):
    """
    TODO
    see above markdown
    """
    df['width'] = df.right - df.left
    df['height'] = df.bottom - df.top
    right_max = df['right'].max()
    bot_max = df['bottom'].max()

    # normalize all x-axis values relative to rightmost point
    for key in ['width', 'left', 'right']:
        df['norm_{}'.format(key)] = df[key] / right_max

    # normalize all y-axis values relative to bottommost point
    for key in ['height', 'top', 'bottom']:
        df['norm_{}'.format(key)] = df[key] / bot_max

    # treat links to DDG twitter & reddit as internal
    df.loc[df.href == 'https://twitter.com/duckduckgo', 'href'] = 'www.duckduckgo.com'
    df.loc[df.href == 'https://reddit.com/r/duckduckgo', 'href'] = 'www.duckduckgo.com'

    df['domain'] = df.apply(extract, axis=1)

    # flag UGC domains of note (can add more if desired)
    domains = [
        'wikipedia',
        'twitter', 'youtube',
        'facebook', 'reddit',
    ]

    df['platform_ugc'] = df['domain'].str.contains('|'.join(
        domains
    ))
    
    for domain in domains:
        df[f'{domain}_in'] = df['domain'].str.contains(domain)
        df[f'{domain}_appears'] = (
            df['domain'].str.contains(domain) &
            (df.width != 0) & (df.height != 0)
        )
        kp_line = CONSTANTS['lefthand_width'] / right_max
        if mobile:
            # no left-hand or right-hand incidence
            df[f'{domain}_appears_rh'] = 0
            # no lefthand above-the-fold incidence
            df[f'{domain}_appears_lh'] = 0
            for name, line in CONSTANTS['mobile_lines'].items():
                mobile_noscroll_line = line / bot_max

                df[f'{domain}_appears_{name}'] = (
                    (df[f'{domain}_appears']) &
                    (df.norm_top < mobile_noscroll_line)
                )

                df[f'{domain}_appears_lh_{name}'] = 0

        else:
            df[f'{domain}_appears_rh'] = (
                (df[f'{domain}_appears']) &
                (df.norm_left > kp_line)
            )

            df[f'{domain}_appears_lh'] = (
                (df[f'{domain}_appears']) &
                (df.norm_left <= kp_line)
            )

            for name, line in CONSTANTS['desktop_lines'].items():
                noscroll_line = line / bot_max

                df[f'{domain}_appears_{name}'] = (
                    (df[f'{domain}_appears']) &
                    (df.norm_top < noscroll_line)
                )

                df[f'{domain}_appears_lh_{name}'] = (
                    (df[f'{domain}_appears_lh']) &
                    (df.norm_top < noscroll_line)
                )
    return df