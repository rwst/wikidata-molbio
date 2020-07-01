
import os, json, argparse, sys, datetime, time
import pronto, six, rdflib

"""
ftp://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
Getting Rhea xrefs from GO functions, and adding reaction participants
to GO function items
"""
wdeecnt = 0
def wdee(j):
    global wdeecnt
    wdeecnt = wdeecnt + 1
#    if wdeecnt > 10:
#        exit()
    f = open('t.json', 'w')
    f.write(json.dumps(j))
    f.close()
    print(json.dumps(j), flush=True)
    ret = os.popen('wd ee t.json')
    print(ret.read())
    if ret.close() is not None:
        print('ERROR')

def ensure(subit, obit, sideq, prop):
    GOREF = "Q93741199"
    RHREF = "Q96482790"
    if QS:
        if sideq is None:
            print('{}|{}|{}|S248|{}|S248|{}'.format(subit, prop, obit, GOREF, RHREF))
        else:
            print('{}|{}|{}|P361|{}|S248|{}|S248|{}'.format(subit, prop, obit, sideq, GOREF, RHREF))
        return
    print('ensure {} {}'.format(subit, obit))
    ss = stmts.get(subit)
    qprop = 'P361'
    if ss is not None:
        os = ss.get(obit)
        if os is not None and os[0] == prop:
            if os[2] == sideq:
                return
            if sideq is None:
                # add ref to stmt
                j = {"id": subit, "claims": { prop: [{ "id": os[0],
                    "value": obit,
                    "references": { "P248": [ GOREF, RHREF ] }}] } }
                wdee(j)
                return
            # add ref to stmt
            j = {"id": subit, "claims": { prop: [{ "id": os[1],
                "value": obit,
                "qualifiers": { "P361": sideq },
                "references": { "P248": [ GOREF, RHREF ] }}] } }
            wdee(j)
            return
    # create stmt
    if sideq is None:
        j = {"id": subit, "claims": { prop: [{ "value": obit,
            "references": { "P248": [ GOREF, RHREF ] }}] } }
    else:
        j = {"id": subit, "claims": { prop: [{ "value": obit,
            "qualifiers": { "P361": sideq },
            "references": { "P248": [ GOREF, RHREF ] }}] } }
    wdee(j)


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

if dontquery is False:
    print('performing query...')
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

chits = {}
goits = {}
stmts = {}
for d in jol:
    item = d.get('item')
    chid = d.get('chid')
    goid = d.get('goid')
    if (chid is None) == (goid is None):
        print('CANT HAPPEN: {}'.format(chid))
        exit()
    if chid is not None:
        chits[chid] = item
        continue
    else:
        goits[goid] = item
    s = stmts.get(item)
    obj = d.get('obj')
    tup = (d.get('stmt'), d.get('ref'), d.get('side'))
    if s is not None:
        if s.get(obj) is not None:
            if s.get(obj)[1] != tup[1]:
                continue
            print('CANT HAPPEN: {} {}'.format(item, obj))
            exit()
        s[obj] = tup
    else:
        stmts[item] = { obj : tup }

print('Reading Rhea')
rhea = rdflib.Graph()
rhea.parse("/home/ralf/wikidata/rhea.rdf") 
print('Reading GO')
ont = pronto.Ontology('/home/ralf/go-ontology/src/ontology/go-edit.obo')

dontputinchem = set(['Q23905964','Q27104100','Q9154808','Q27126319','Q27124397',
        'Q60711173','Q60711368','Q171877','Q27225747','Q27102088','Q27104095',
        'Q27089397','Q27125623','Q56071634','Q190901','Q27124396#',
        'Q27115222','Q1997','Q27225748','Q27104508','Q27124944','Q27125717',
        'Q27125072','Q28529711','Q27113900','Q5203615','Q283','Q506710'])

for term in ont.terms():
    goid = term.id
    if not goid.startswith('GO:'):
        continue
    goit = goits.get(goid)
    if goit is None:
        continue
    rhearef = None
    for xref in term.xrefs:
        if xref.id.startswith('RHEA:'):
            rhearef = xref.id
            break
    if rhearef is None:
        continue
    #print('query {}'.format(rhearef))
    qres = rhea.query("""PREFIX rh:<http://rdf.rhea-db.org/>
SELECT DISTINCT ?item ?prset ?acc
WHERE {{
    ?item rh:accession '{}' .
    ?item rh:bidirectionalReaction ?breac .
    ?breac rh:substratesOrProducts ?prset .
    ?prset rh:contains ?partcp .
    ?partcp rh:compound ?comp .
    ?comp rh:accession ?acc
}}""".format(rhearef))
    for row in qres:
        if not str(row[2]).startswith('CHEBI:'):
            continue
        side = row[1][-1]
        sideq = 'Q96483149'
        if side == 'R':
            sideq = 'Q96483162'
        chebid = str(row[2])[6:]
        chit = chits.get(chebid)
        if chit is None:
            print('missing: {}'.format(chebid))
        else:
            ensure(goit, chit, sideq, 'P527')
            if chit not in dontputinchem:
                ensure(chit, goit, None, 'P361')
