
import csv, os, json, argparse, sys

"""
Print list of items: proper chemclasses that have no proper chemclasses as superclass
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()
#print(args)

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

items = {}
for d in jol:
    it = d.get('item')
    sup = d.get('super')
    i = items.get(it)
    if i is not None:
        i.append(sup)
    else:
        items[it] = [sup]

whitelist = set(['Q2393187'])
for it,itsuplist in items.items():
    if all([s not in set(items.keys()).union(whitelist) for s in itsuplist]):
        print('{}'.format(it))
