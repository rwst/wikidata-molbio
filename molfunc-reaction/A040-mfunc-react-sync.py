
import os, json, argparse, sys, datetime, time
import pronto, six, rdflib

"""
ftp://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
Getting Rhea xrefs from GO functions, and removing obsolete reaction participants,
as well as backlinks from compound items
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

LEFT = 'Q96483149'
RITE = 'Q96483162'
reacl = {}
reacr = {}
for d in jol:
    exm = d.get('exm')
    rhea = exm[exm.rfind('/rhea/')+6:]
    chebi = d.get('chebi')
    if chebi is None or len(chebi) == 0:
        print('empty chebi for {}'.format(exm))
        raise
    side = d.get('partof')
    stmt1 = d.get('stmt1')
    stmt2 = d.get('stmt2')
    if stmt2 is not None and len(stmt2)==0:
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
    else:
        print('{} {} {}'.format(rhea, chebi, side))
        raise

print('Reading Rhea', file=sys.stderr)
rhea = rdflib.Graph()
rhea.parse("/home/ralf/wikidata/rhea.rdf") 

stmts1 = set()
stmts2 = set()
for r in reacl.keys():
    rhearef = 'RHEA:' + r
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
    print('{}/{} = {}/{}\n{}\n'.format(reacl.get(r), lside, reacr.get(r), rside, row))
    l = reacr.get(r)
    if l is None:
        l = set()
    for tup in l:
        if tup[0] not in rside:
            stmts1.add(tup[1])
            if tup[2] is not None:
                stmts2.add(tup[2])
    l = reacl.get(r)
    if l is None:
        l = set()
    for tup in l:
        if tup[0] not in lside:
            stmts1.add(tup[1])
            if tup[2] is not None:
                stmts2.add(tup[2])

for s in stmts2:
    print(s)
for s in stmts1:
    print(s)

