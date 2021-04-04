
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
CHEBI_RELEASE = 'Q105965742'

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
#    rank = d,get('rank')
    taut = d.get('taut')
    if taut is not None and len(taut) == 0:
        taut = None
    i = items.get(ch)
    if i is not None and i != it:
        print('duplicate items for ChEBI:{}: {} {}'.format(ch, it, items.get(ch)), file=sys.stderr)
        dups.add(ch)
        continue
    items[ch] = it
    if taut is None:
        continue
    t = tauts.get(ch)
    if t is not None:
        t.add(taut)
    else:
        tauts[ch] = set([taut])

print('reading ChEBI...', file=sys.stderr)
ont = pronto.Ontology('chebi.obo')
ref = { STATED_IN: CHEBI_RELEASE }
for ch in items.keys():
    term = ont.get('CHEBI:' + ch)
    if term is None:
        print('Obsolete CHEBI:{} on {}'.format(ch, items.get(ch)), file=sys.stderr)
        continue
    if ch in dups:
        print('duplicate requested ChEBI subject: {}'.format(ch), file=sys.stderr)
        continue
    tt = tauts.get(ch)
    for rel in term.relationships:
        if rel.name == 'is tautomer of':
            tset = term.relationships.get(rel)
            for t in tset:
                tc = t.id[6:]
                if tc in dups:
                    print('duplicate requested ChEBI object: {}'.format(tc), file=sys.stderr)
                    continue
                if tt is not None:
                    ti = items.get(tc)
                    if ti is None:
                        print('missing: {}'.format(tc), file=sys.stderr)
                        continue
                    if ti in tt:
                        continue
                ti = items.get(tc)
                if ti is None:
                    continue
                j = {"id": items.get(ch), "claims": { 'P6185': [{
                    "value": ti,
                    "references": [ref] }] } }
                print(json.dumps(j))

