
import os, json, argparse, sys, datetime, time, csv

"""
Takes as input argument a (filtered) S2citations.out file, queries WD for Qitem, date
chunkwise and spits out list for usual eyeballing. If a DOI is not found in WD the list
prints it with title so it can be ignored/created manually
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
dontquery = not args.query
print(args)

# Check for --version or -V
script = os.path.basename(sys.argv[0])[:-3]

titles = {}
with open(args.infile) as file:
    s = file.readlines()
    if len(s) == 0:
        print('Nothing to do...')
        exit()
    for line in s:
        line = line.rstrip()
        doi = line[1:line[1:].find(' ')+1]
        title = line[line[1:].find(' ')+1:]
        titles[doi] = title

print(len(titles))

wddois = {}
if dontquery is False:
    lst = list(titles.keys())
    offset = 0
    chunksize = 1000
    while offset < len(lst):
        size = min(chunksize, len(lst)-offset)
        query="""
        SELECT DISTINCT ?item ?doi ?date
        WHERE
        {{
          VALUES ?art {{ wd:Q580922 wd:Q13442814 }}
          VALUES ?doi {{ '{}' }}
          ?item wdt:P31 ?art.
          ?item wdt:P356 ?doi.
          ?item wdt:P577 ?date
        }}
        """.format("' '".join(lst[offset:offset+size]))
        with open('{}.rq'.format(script), 'w') as f:
            f.write(query)
            f.close()

        print('performing query for {} DOIs... '.format(size), file=sys.stderr)
        ret = os.popen('wd sparql {}.rq >{}-1.json'.format(script, script))
        time.sleep(5)
        offset += chunksize

        jol = []
        with open('{}-1.json'.format(script)) as f:
            s = ''
            s = f.read()
            f.close()
            try:
                jol = json.loads(s)
            except json.JSONDecodeError:
                pass
        for d in jol:
            qitem = d.get('item')
            doi = d.get('doi')
            date = d.get('date')
            if date is not None:
                date = date[0:10]
            wddois[doi] = (qitem,date)

    print(len(wddois))
    with open('{}.json'.format(script), 'w') as f:
        f.write(json.dumps(wddois))
        f.close()

with open('{}.json'.format(script), 'r') as f:
    s = f.read()
    f.close()
    wddois = json.loads(s)
print(len(wddois))

items = []
for doi in titles.keys():
    title = titles.get(doi)
    p = wddois.get(doi)
    if p is None:
        qitem,date = doi,'1000-01-01'
    else:
        qitem,date = p
    items.append((qitem, title, date))
    
for tup in sorted(items, key=lambda item: item[2]):
    print('* {} [[{}]] {} '.format(tup[2], tup[0], tup[1]))
