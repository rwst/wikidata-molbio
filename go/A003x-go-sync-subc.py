
import pronto, six, csv, os, json, argparse, sys, datetime

"""
Use -c to check if the pronto version combined with your env can
see "is a" relationships.

On current GO items remove P279 claims pointing to obsoleted GOs.
Also, remove erroneous P279 claims to current GO items.
Use with wd rc.

Option -a adds missing P279. Use with wd ee.
"""
# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--check", help="",
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

if args.check:
    ont = pronto.Ontology('/home/ralf/wikidata/go.obo')
    term = ont.get("GO:0017057")
    print(list(term.relationships.keys()))
    subs = []
    for r in term.relationships.keys():
        if r.name == 'is a':
            tset = term.relationships.get(r)
            for t in tset:
                subs.append(t.id)
    print(subs)
    exit(0)

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
stmts = set()
for d in jol:
    item = d.get('item')
    goid = d.get('goid')
    stmt = d.get('stmt1')
    sgoid = d.get('sgoid')
    stmts.add(stmt)
    it = its.get(goid)
    if it is None:
        its[goid] = item
    git = goids.get(goid)
    if git is None:
        goids[goid] = {(stmt,sgoid)}
    else:
        git.add((stmt,sgoid))

#if dontadd:
#    for s in stmts.difference(validits):
#        print(stmt)

ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
print('reading GO', file=sys.stderr)
ont = pronto.Ontology('/home/ralf/wikidata/go.owl')
for goid in goids.keys():
    term = ont.get(goid)
    #print(goid)
    #print(list(term.relationships.keys()))
    if term is None or term.obsolete is True:
        continue
    
    subs = []
    for r in term.relationships.keys():
        if r.name == 'is a':
            tset = term.relationships.get(r)
            for t in tset:
                subs.append(t.id)
    #print(subs)
    if dontadd:
        gset = goids.get(goid)
        if gset is not None:
            try:
                for stmt,sgoid in gset:
                    if not sgoid in subs:
                        print(stmt)
            except ValueError:
                print(gset)
                raise
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

