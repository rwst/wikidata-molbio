
import os, json, argparse, sys, datetime, time
import pronto, six

"""
GO has relationship: capable_of (-->activity) and relationship: capable_of_part_of (--> process) on cell component entries. These can be made to the resp.
molfunc and process statemens. 
"""
# Initiate the parser
parser = argparse.ArgumentParser()
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
    for it in term.relationships.items(): 
        rel = it[0] 
        if rel.name == 'capable of': 
            for t in it[1]: 
                oterm = ont.get(t.id)
                if oterm is None:
                    print('CANT HAPPEN: {}'.format(t.id))
                    exit()
                goit = goits.get(t.id)
                if oterm is None:
                    print('CANT HAPPEN: {}'.format(t.id))
                    exit()

                
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
