
import os, json, argparse, sys, datetime, time
import pronto, six, rdflib

"""
ftp://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
Getting Rhea xrefs from GO functions, and adding reaction participants
to GO function items
We decided to not add transporter reactions; markup as cargo should be implemented
Use stdout with wd ee.
UPDATE RHDATE! (date of rhea2go.txt)
TODO: collect all edits on one item
"""
RHDATE = "2022-05-25T00:00:00Z"
REF = { 'P854': 'http://geneontology.org/external2go/rhea2go', 'P813': RHDATE }

# Initiate the parser
parser = argparse.ArgumentParser()
#parser.add_argument("-r", "--addref", help="add missing refs",
#        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

cmpd_adds = set()

def ensure(subit, obit, sideq, prop):
    #print('ensure {} {}'.format(subit, obit))
    ss = stmts.get(subit)
    if ss is not None:
        os = ss.get(obit)
        if os is not None:
            #print('{} {} exists'.format(subit, obit), file=sys.stderr)
            return
        """
            if os[1] == sideq:
                return
            if sideq is None:
                # add ref to stmt
                j = {"id": subit, "claims": { prop: [{ "id": os[0],
                    "value": obit,
                    "references": REF }] } }
                print('{} {} 1'.format(subit, obit), file=sys.stderr)
                print(json.dumps(j), flush=True)
                return
            # add ref to stmt
            print('{} {} 2'.format(subit, obit), file=sys.stderr)
            j = {"id": subit, "claims": { prop: [{ "id": os[1],
                "value": obit,
                "qualifiers": { "P361": sideq },
                "references": REF }] } }
            print(json.dumps(j), flush=True)
            return
        """
    # create stmt
    if prop == 'P527':
        if sideq is None:
            j = {"id": subit, "claims": { prop: [{ "value": obit,
                "references": REF }] } }
        else:
            j = {"id": subit, "claims": { prop: [{ "value": obit,
                "qualifiers": { "P361": sideq },
                "references": REF }] } }
            print(json.dumps(j), flush=True)
    else:
        cmpd_adds.add((subit, obit))

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
file = open('{}.json'.format(script))
s = file.read()
jol = json.loads(s)

chits = {}
goits = {}
stmts = {}
exms = {}
chdups = set()
exdups = set()
for d in jol:
    item = d.get('item')
    chid = d.get('chid')
    goid = d.get('goid')
    if (chid is None) == (goid is None):
        print('CANT HAPPEN: {}'.format(chid))
        exit()
    if chid is not None:
        it = chits.get(chid)
        if it is not None and it != item:
            chdups.add(item)
            continue
        chits[chid] = item
    else:
        goits[goid] = item
        exm = d.get('exm')
        e = exms.get(goid)
        if e is not None:
            exdups.add(goid)
            continue
        else:
            exms[goid] = exm[exm.rfind('/rhea/')+6:]
    obj = d.get('obj')
    if obj is None:
        continue
    tup = (d.get('stmt'), d.get('side'))
    s = stmts.get(item)
    if s is not None:
        if s.get(obj) is not None:
            if s.get(obj)[1] != tup[1]:
                continue
            print('CANT HAPPEN: {} {}'.format(item, obj), file=sys.stderr)
            exit()
        s[obj] = tup
    else:
        stmts[item] = { obj : tup }

print('Reading Rhea', file=sys.stderr)
rhea = rdflib.Graph()
rhea.parse("/home/ralf/wikidata/rhea.rdf") 

dontputinchem = set(['Q23905964','Q27104100','Q9154808','Q27126319','Q27124397',
        'Q60711173','Q60711368','Q171877','Q27225747','Q27102088','Q27104095',
        'Q27089397','Q27125623','Q56071634','Q190901','Q27124396#',
        'Q27115222','Q1997','Q27225748','Q27104508','Q27124944','Q27125717',
        'Q27125072','Q28529711','Q27113900','Q5203615','Q283','Q506710',
        ])

# having groups or classes. TODO: add missing group items
ignore = set(['GO:0050528', 'GO:0008800', 'GO:0047654', 'GO:0070330', 'GO:0103064',
    'GO:0047157', 'GO:0047290', 'GO:0047876', 'GO:0047177', 'GO:0047178', 'GO:0050207',
    'GO:0000773', 'GO:0080101', 'GO:0008779', 'GO:0004608', 'GO:0004609', 'GO:0106245',
    'GO:0004307', 'GO:0106262', 'GO:0047637', 'GO:0047391', 'GO:0050018', 'GO:0047313',
    'GO:0008793', 'GO:0050131', 'GO:0047658', 'GO:0005253', 'GO:0004687', 'GO:0016829',
    'GO:0042586', 'GO:0033787', 'GO:0015267'])

for goid in goits.keys():
    if goid in ignore or goid in exdups:
        continue
    goit = goits.get(goid)
    if goit is None:
        continue
    rhearef = exms.get(goid)
    if rhearef is None:
        continue
    rhearef = 'RHEA:' + rhearef
    #print('query {}'.format(rhearef))
    qres = rhea.query("""PREFIX rh:<http://rdf.rhea-db.org/>
SELECT DISTINCT ?item ?prset ?acc ?transp
WHERE {{
    ?item rh:accession '{}' .
    ?item rh:isTransport ?transp .
    ?item rh:bidirectionalReaction ?breac .
    ?breac rh:substratesOrProducts ?prset .
    ?prset rh:contains ?partcp .
    ?partcp rh:compound ?comp .
    ?comp rh:accession ?acc
}}""".format(rhearef))
    for row in qres:
        if not str(row[2]).startswith('CHEBI:') or str(row[3]) == 'true':
            continue
        side = row[1][-1]
        sideq = 'Q96483149'
        if side == 'R':
            sideq = 'Q96483162'
        chebid = str(row[2])[6:]
        chit = chits.get(chebid)
        if chit is None:
            print('missing: {} from {}'.format(chebid, rhearef), file=sys.stderr)
        else:
            if chit in chdups:
                print('WARNING: {}'.format(chit), file=sys.stderr)
            ensure(goit, chit, sideq, 'P527')
            if chit not in dontputinchem:
                ensure(chit, goit, None, 'P361')

#TODO:add cache to collect all edits on one item 
for subit,obit in cmpd_adds:
    j = {"id": subit, "claims": { 'P361': [{ "value": obit,
        "references": REF }] } }
    print(json.dumps(j), flush=True)
