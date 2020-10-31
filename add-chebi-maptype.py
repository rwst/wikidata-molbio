
import os, json, argparse, sys, datetime, time, csv

"""
For every item with a single InChi key with ref to a specific source,
having a ChEBI ID, add mapping type: exact as qualifier to the
ChEBI statement.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise

file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

ik = {}
ist = {}
gooditems = set() # items with good ref
ambigs = set()
for d in jol:
    rel = d.get('rel')
    if rel is not None:
        continue
    item = d.get('item')
    key = d.get('key')
    iref = d.get('iref')
    irank = d.get('irank')
    if irank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    k = ik.get(item)
    if k is not None and k != key:
        ambigs.add(item)
    else:
        ik[item] = key
    if iref == 'Q98915402':
        gooditems.add(item)
    cstmt = d.get('cstmt')
    ist[item] = cstmt

for i in gooditems.difference(ambigs):
    print('{} P4390 Q39893449'.format(ist.get(i)))
#print(ambigs)
