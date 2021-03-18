
import csv, os, json, argparse, sys
import pronto, six

"""
use with wd ee
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
MAPPING_TYPE = 'P4390'
SKOS_EXACT = 'Q39893449'
STATED_IN = 'P248'
CHEBI_RELEASE = 'Q105965742'

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json1'.format(script))
s = file.read()
jol = json.loads(s)

items = {}
for d in jol:
    it = d.get('item')
    ik = d.get('ik')
    i = items.get(ik)
    if i is not None:
        i.append(it)
    else:
        items[ik] = [it]

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq2 >{}.json2'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json2'.format(script))
s = file.read()
jol = json.loads(s)

chebis = {}
exmapq = set()
for d in jol:
    it = d.get('item')
    chebi = d.get('chebi')
    ik = d.get('ik')
    mapq = d.get('mapq')
    if mapq == 'Q39893449':
        exmapq.add(it)
    c = chebis.get(it)
    if c is not None:
        c.append(chebi)
    else:
        chebis[it] = [chebi]

ont = pronto.Ontology('chebi.obo')
missing = 0
for term in ont.terms():
    ik = None
    for ann in term.annotations:
        if ann.property == 'http://purl.obolibrary.org/obo/chebi/inchikey':
            ik = ann.literal
            break
    if ik is None:
        continue
    its = items.get(ik)
    if its is None:
        missing = missing + 1
        continue
    for it in its:
        if it in exmapq:
            continue
        chs = chebis.get(it)
        ID = term.id[6:]
        if chs is not None and ID in chs:
            # handled in other module
            continue
        j = {"id": it,
            "claims": {
                 "P683": { "value": ID,
                     "qualifiers": { MAPPING_TYPE: SKOS_EXACT },
                     "references": { STATED_IN: CHEBI_RELEASE } },
                    }
                }
        print(json.dumps(j), flush=True)

#print('Missing: {}'.format(missing))

