
import os, json, argparse, sys, datetime, time
import pronto, six

"""
GO has KEGG reaction references in def: and xref: fields of function entries.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--output_qs", help="output to QS",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
QS = args.output_qs
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
GOREF = "Q93741199"   

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

goits = {}
keggs = {}
for d in jol:
    item = d.get('item')
    stmt = d.get('stmt')
    kegg = d.get('kegg')
    ref = d.get('refd')
    ref = (ref is not None) and (ref == GOREF)
    k = keggs.get(item)
    if k is None:
        keggs[item] = [(kegg, stmt, ref)]
    else:
        k.append((kegg, stmt, ref))
    goid = d.get('goid')
    goits[goid] = item

print('Reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')

for term in ont.terms():
    goid = term.id
    if not goid.startswith('GO:'):
        continue
    goit = goits.get(goid)
    if goit is None:
        continue
    keggref = None
    for xref in term.xrefs:
        if xref.id.startswith('KEGG_REACTION:'):
            keggref = xref.id[14:]
            break
    if keggref is None and term.definition is not None:
        for xref in term.definition.xrefs:
            if xref.id.startswith('KEGG_REACTION:'):
                keggref = xref.id[14:]
            break
    if keggref is None:
        continue
    if keggref[0] != 'R':
        keggref = 'R' + keggref
    k = keggs.get(goit)
    if k is None:
        # no KEGG, create new stmt
        j = {"id": goit, "claims": { "P665": [{
            "value": keggref,
            "references": { "P248": GOREF }}] } }
        print(json.dumps(j))
        continue
    if all([tup[2] is False for tup in k]):
        stmt = None
        for tup in k:
            if tup[0] == keggref:
                stmt = tup[1]
                break
        if stmt is None:
            j = {"id": goit, "claims": { "P665": [{
                "value": keggref,
                "references": { "P248": GOREF }}] } }
        else:
            # add ref to stmt
            j = {"id": goit, "claims": { "P665": [{ "id": stmt,
                "value": keggref,
                "references": { "P248": GOREF }}] } }
        print(json.dumps(j))
