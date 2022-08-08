
import os, json, argparse, sys, datetime, time
import pronto, six, rdflib

"""
ftp://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
Getting Rhea xrefs from GO functions, and removing obsolete reaction participants,
as well as backlinks from compound items
Use wd rc with stdout, wd ee with stderr
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-v", "--verbose", help="print more info",
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

LEFT = 'Q96483149'
RITE = 'Q96483162'
reacl = {}
reacr = {}
for d in jol:
    item = d.get('item')
    exm = d.get('exm')
    rhea = exm[exm.rfind('/rhea/')+6:]
    chebi = d.get('chebi')
    side = d.get('partof')
    stmt1 = d.get('stmt1')
    stmt2 = d.get('stmt2')
    if chebi is not None and len(chebi) == 0:
        chebi = None
    if stmt2 is not None and len(stmt2) == 0:
        stmt2 = None

    if side == LEFT:
        c = reacl.get(rhea)
        if c is None:
            reacl[rhea] = [(chebi, stmt1, stmt2)]
        else:
            c.append((chebi, stmt1, stmt2))
    elif side == RITE:
        c = reacr.get(rhea)
        if c is None:
            reacr[rhea] = [(chebi, stmt1, stmt2)]
        else:
            c.append((chebi, stmt1, stmt2))

rhits = {}
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq1 >{}.json1'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json1'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    for d in jol:
        item = d.get('item')
        exm = d.get('url')
        rhea = exm[exm.rfind('/rhea/')+6:]
        i = rhits.get(rhea)
        if i is None:
            rhits[rhea] = item
        else:
            rhits[rhea] = ''

chits = {}
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq2 >{}.json2'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json2'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    for d in jol:
        item = d.get('item')
        chebi = d.get('chebi')
        i = chits.get(chebi)
        if i is None:
            chits[chebi] = item
        else:
            chits[chebi] = ''

# remove RHEAs that are on items with multiple RHEAs
rrs = set()
durs = {}
for r in rhits.keys():
    i = rhits.get(r)
    rr = durs.get(i)
    if rr is None:
        durs[i] = r
    else:
        rrs.add(rr)
        rrs.add(r)

    
print('Reading Rhea', file=sys.stderr)
rhea = rdflib.Graph()
rhea.parse("/home/ralf/wikidata/rhea.rdf") 

RHEAREL = 'Q113253685'
REF = { 'P248': RHEAREL }
stmts1 = set()
stmts2 = set()
addl = set()
addr = set()
for r in set(reacl.keys()).union(set(reacr.keys())):
    i = rhits.get(r)
    if i is None:
        print(r)
    if i is None or r in rrs or len(i) == 0:
        continue
    rhearef = 'RHEA:' + r
    j = { "id": rhits.get(r) }
    claims = []
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
    lside = set()
    rside = set()
 #   if r == '22304':
 #       for row in qres:
 #           print(row)
 #       exit(1)
    for row in qres:
        if not str(row[2]).startswith('CHEBI:'):
            continue
        chebid = str(row[2])[6:]
        side = row[1][-1]
        if side == 'R':
            rside.add(chebid)
        else:
            lside.add(chebid)
        #print('{}/{} = {}/{}'.format(len(reacl.get(r)), len(lside), len(reacr.get(r)), len(rside)))
    if args.verbose:
        print('{}/{} = {}/{}\n{}\n'.format(reacl.get(r), lside, reacr.get(r), rside, row))
    l = reacr.get(r)
    reacrset = set()
    if l is None:
        l = set()
    for tup in l:
        reacrset.add(tup[0])
        if tup[0] not in rside:
            stmts1.add(tup[1])
            if tup[2] is not None:
                stmts2.add(tup[2])
    l = reacl.get(r)
    reaclset = set()
    if l is None:
        l = set()
    for tup in l:
        reaclset.add(tup[0])
        if tup[0] not in lside:
            stmts1.add(tup[1])
            if tup[2] is not None:
                stmts2.add(tup[2])
    
    for ch in rside.difference(reacrset):
        chit = chits.get(ch)
        if chit is None or len(chit) == 0:
            continue
        cl = { "value": chit,
                "qualifiers": { "P361": RITE },
                "references": REF }
        claims.append(cl)
    for ch in lside.difference(reaclset):
        chit = chits.get(ch)
        if chit is None or len(chit) == 0:
            continue
        cl = { "value": chit,
                "qualifiers": { "P361": LEFT },
                "references": REF }
        claims.append(cl)
    if len(claims) > 0:
        j['claims'] = { 'P527': claims }
        print(json.dumps(j), flush=True, file=sys.stderr)

for s in stmts2:
    print(s)
for s in stmts1:
    print(s)

