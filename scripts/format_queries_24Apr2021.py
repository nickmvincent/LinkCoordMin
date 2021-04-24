import glob

out = ""
path = 'search_queries/prepped/hw/*'

paths = glob.glob(path)
print(paths)
for x in paths:
    with open(x, 'r') as f:
        lines = f.readlines() # should remove all newlines
    for line in lines:
        if line == "\n":
            out += line
        else:
            out += line.strip("\n")

    new_name = x.replace(' ', '_').strip('.txt') + '_nice.txt' 
    with open(new_name, 'w') as f:
        f.write(out)
