
import pronto, six, csv, os, json, argparse, sys, datetime

"""
wget http://purl.obolibrary.org/obo/go/extensions/go-plus.owl

On current GO items remove P279 claims pointing to obsoleted GOs.
Also, remove erroneous P279 claims to current GO items.
Use with wd rc.

Option -a adds missing P279. Use with wd ee.
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--preview", help="",
        action="store_true")
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
validits = set()
deprcits = set()
for d in jol:
    item = d.get('item')
    goid = d.get('goid')
    stmt = d.get('stmt1')
    if stmt is None:
        print("null stmt: {}".format(item))
        exit(0)
    sgoid = d.get('sgoid')
    rank = d.get('rank')
    if rank != 'http://wikiba.se/ontology#DeprecatedRank':
        validits.add(stmt)
    it = its.get(goid)
    if it is None:
        its[goid] = item
    git = goids.get(goid)
    if git is None:
        goids[goid] = [(stmt,sgoid)]
    else:
        goids[goid].append((stmt,sgoid))

if dontadd:
    for d in jol:
        stmt = d.get('stmt1')
        if not stmt in validits:
            print(stmt)

ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go-plus.owl')
for goid in goids.keys():
    term = ont.get(goid)
    if term is None or term.obsolete is True:
        continue
    
    subs = []
    for r in term.relationships.keys():
        if r.name == 'is a':
            tset = term.relationships.get(r)
            for t in tset:
                subs.append(t.id)
    if dontadd:
        for stmt,sgoid in goids.get(goid):
            if not sgoid in subs:
                print(stmt)
    else:
        cl = []
        for sub in subs:
            if not sub in list(zip(*goids.get(goid)))[1]:
                claim = { "value": its.get(sub),
                          "references": { "P248": GORELEASE,
                            "P813": ndate }}
                cl.append(claim)
        if len(cl) == 0:
            continue
        claims = { "P279": cl }
        it = its.get(goid)
        j = {"id": it,
            "claims": claims }
        print(json.dumps(j), flush=True)

