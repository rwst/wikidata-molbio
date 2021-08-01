
import csv, os, json, argparse, sys
import pronto, six

"""
use stdout with wd ee
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
STATED_IN = 'P248'
CHEBI_RELEASE = 'Q107647028'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

items = {}
tauts = {}
dups = set()
for d in jol:
    it = d.get('item')
    ch = d.get('chebi')
    i = items.get(ch)
    if i is not None and i != it:
        print('duplicate items for ChEBI:{}: {} {}'.format(ch, it, items.get(ch)), file=sys.stderr)
        dups.add(ch)
        continue
    items[ch] = it

print('reading ChEBI...', file=sys.stderr)
ont = pronto.Ontology('chebi.owl')
ref = { STATED_IN: CHEBI_RELEASE }
for ch in items.keys():
    term = ont.get('CHEBI:' + ch)
    if term is None:
        print('Obsolete CHEBI:{} on {}'.format(ch, items.get(ch)), file=sys.stderr)
        continue
    if ch in dups:
        print('duplicate requested ChEBI subject: {}'.format(ch), file=sys.stderr)
        continue
    chebi = None
    for a in term.annotations:
        if a.property == 'http://purl.obolibrary.org/obo/chebi/smiles':
            chebi = a.literal
    if chebi is None or not '*' in chebi:
        continue
    if '@' in chebi or '/' in chebi:
        prop = 'P2017'
    else:
        prop = 'P233'
    j = {"id": items.get(ch), "claims": { prop: [{
        "value": chebi,
        "references": [ref] }] } }
    print(json.dumps(j))

