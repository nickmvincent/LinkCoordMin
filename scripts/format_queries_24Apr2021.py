import glob

out = ""
path = 'search_queries/prepped/hw/*'
new_path = 'search_queries/prepped/hw_nice/'

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

    parts = x.split('/')
    print(parts)
    name = parts[-1]
    new_name = new_path + name.replace(' ', '_')
    #new_name = x.replace(' ', '_').strip('.txt') + '_nice.txt' 
    with open(new_name, 'w') as f:
        f.write(out)
