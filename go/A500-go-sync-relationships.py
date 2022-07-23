
import pronto, six, csv, os, json, argparse, sys, datetime, subprocess

"""
wget http://purl.obolibrary.org/obo/go/snapshot/go.obo

On current GO items sync relationship stmts (not is_a).
Remove erroneous claims: Use with wd rc.
Option -a adds missing claims: Use with wd ee.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-a", "--add", help="switch modus to adding missing claims",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
dontadd = not args.add
script = os.path.basename(sys.argv[0])[:-3]
GORELEASE = "Q112968510"

# get GO IDs
if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True, file=sys.stderr)

its = {}
goids = {}
for d in jol:
    item = d.get('item')
    goid = d.get('goid')
    it = its.get(goid)
    if it is None:
        its[goid] = item
    g = goids.get(item)
    if g is None:
        goids[item] = goid

# get all existing relationship stmts except "is a" (P279)

RELS = { 'part of': 'P361', 
        'has part': 'P527', 
        'regulates': 'P128',
        'positively regulates': 'P128',
        'negatively regulates': 'P128',
        'occurs in': 'P927',
        'happens during': 'P361',
        'ends_during': 'P793',
        'WRONG_location_USE_P927': 'P276'
        }

RELQUALS = { 
        'positively regulates': { 'P2868': 'Q22260639' },
        'negatively regulates': { 'P2868': 'Q22260640' },
        'happens during': { 'P2868': 'Q113130942' },
        'ends_during': { 'P2868': 'Q113130973' },
        }

query = """
SELECT DISTINCT ?item ?goid ?stmt ?val ?qval
{{
  ?item wdt:P686 ?goid.
  ?item p:{0} ?stmt.
  ?stmt ps:{0} ?val.
  ?stmt prov:wasDerivedFrom ?ref.
  ?ref pr:P248 ?go.
  ?go wdt:P629 wd:Q135085.
  OPTIONAL {{
    ?stmt pq:P2868 ?qval.
  }}
}}
"""

if dontquery is False:
    for p in set(RELS.values()):
        qfile = open('{}.rq.{}'.format(script, p), 'w')
        qfile.write(query.format(p))
        qfile.close()
        print('performing query for {} ...'.format(p), file=sys.stderr)
        ret = subprocess.call('wd sparql {}.rq.{} >{}.json.{}'.format(script, p, script, p),
                shell=True)

stmts = {}
for p in set(RELS.values()):
    fname = '{}.json.{}'.format(script, p)
    if os.stat(fname).st_size == 0:
        continue
    with open(fname) as file:
        s = file.read()
        jol = json.loads(s)
        print('{}: read {} records'.format(p, len(jol)), flush=True, file=sys.stderr)

    for REL in RELS.keys():
        if RELS.get(REL) != p:
            continue
        tstmts = {}
        for d in jol:
            goid = d.get('goid')
            val = d.get('val')
            valgo = goids.get(val)
            qval = d.get('qval')
            stmt = d.get('stmt')
            s = tstmts.get(goid)
            if s is None:
                tstmts[goid] = [(valgo, qval, stmt)]
            else:
                tstmts[goid].append((valgo, qval, stmt))
        stmts[REL] = tstmts


ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go.obo')

for goid in its.keys():
    term = ont.get(goid)
    if term is None or term.obsolete is True:
        continue

    if not dontadd:
        pclsts = {}
        for r in term.relationships.keys():
            if r.name == 'is a':
                continue
            tset = term.relationships.get(r)
            p = RELS.get(r.name)
            tstmts = stmts.get(r.name)
            for t in tset:
                texists = False
                if tstmts is not None:
                    tslst = tstmts.get(goid)
                    if tslst is not None:
                        for valgo,qval,stmt in tslst:
                            #print((t.id, valgo,qvalgo,stmt))
                            if valgo == t.id:
                                texists = True
                                break
                if not texists:
                    if r.name in RELQUALS.keys():
                        claim = { "value": its.get(t.id),
                                "qualifiers": RELQUALS.get(r.name),
                                "references": { "P248": GORELEASE,
                                    "P813": ndate }}
                    else:
                        claim = { "value": its.get(t.id),
                                "references": { "P248": GORELEASE,
                                    "P813": ndate }}
                    pcl = pclsts.get(p)
                    if pcl is None:
                        pclsts[p] = [claim]
                    else:
                        pcl.append(claim)

        if len(pclsts) > 0:
            j = {"id": its.get(goid),
                "claims": pclsts }
            print(json.dumps(j), flush=True)

    else: #dontadd
        for REL in RELS.keys():
            p = RELS.get(REL)
            relq = RELQUALS.get(REL)
            relqval = None
            if relq is not None:
                relqval = relq.get('P2868')
            tstmts = stmts.get(REL)
            if tstmts is None:
                continue
            tslst = tstmts.get(goid)
            if tslst is None:
                continue
            for r in term.relationships.keys():
                if r.name != REL:
                    continue
                tset = term.relationships.get(r)
            for valgo,qval,stmt in tslst:
                if relqval != qval or valgo is None:
                    continue
                if all([valgo != t.id for t in tset]):
                    print(stmt)

