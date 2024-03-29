
import csv, os, json, argparse, sys

"""
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-t", "--topic", help="base name", required=True)
parser.add_argument("-w", "--write", help="write new dead DOIs if set", action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
topic = args.topic
dowrite = args.write

deaddois = set()
try:
    with open('{}.deaddois.txt'.format(topic)) as file:
        for line in file.readlines():
            line = line.rstrip()
            deaddois.add(line)
except FileNotFoundError:
    print('WARNING: empty database', file=sys.stderr)

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.cited.rq >{}.cited.json'.format(topic, topic))
    if ret.close() is not None:
        raise
file = open('{}.cited.json'.format(topic))
s = file.read()
jol = json.loads(s)

newdeaddois = set()
items = []
for d in jol:
    ref = d.get('ref')
    value = ref.get('value')
    doi = d.get('doi')
    if doi is None or doi in deaddois:
        continue
    items.append((value, ref.get('label'), d.get('date')[0:10]))
    newdeaddois.add(doi)

if dowrite:
    for it in sorted(deaddois.union(newdeaddois)):
        print(it)
else:
    for tup in sorted(items, key=lambda item: item[2]):
        print('* {} [[{}]] {} '.format(tup[2], tup[0], tup[1]))

