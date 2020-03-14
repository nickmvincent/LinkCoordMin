# iPhone viewport heights (see paper for similarly sized Android devices)
IPHONE_6_H = 667
IPHONE_6plus_H = 736
IPHONE_X_H = 812

# desktop viepwort heights
#https://gs.statcounter.com/screen-resolution-stats/desktop/worldwide
MOST_COMMON = 768
ZOOM_90 = 853
ZOOM_110 = 698

CONSTANTS = {
    'figure_width': 8, # width of our figures in inches
    'lefthand_width': 780,  # manually identified vertical line dividing the left-hand col and right-hand col of serps
    'viewport_width': 1024,
    'mobile_lines': {
        'noscroll_lb': IPHONE_6_H,
        'noscroll_mg': IPHONE_6plus_H,
        'noscroll_ub': IPHONE_X_H
    },
    'desktop_lines': {
        'noscroll_lb': ZOOM_110,
        'noscroll_mg': MOST_COMMON,
        'noscroll_ub': ZOOM_90,
    }
    
}