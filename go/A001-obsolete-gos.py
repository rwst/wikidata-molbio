
import pronto, six, csv, os, json, argparse, sys, datetime

"""
wget http://purl.obolibrary.org/obo/go/extensions/go-plus.owl
NOTE: DEPRECATION OF P686 NOT IMPLEMENTED. PROCEED MANUALLY.
REMOVAL OF ALIASES NOT IMPLEMENTED.

Find obsolete GO items (either "is_obsolete" or not existing) and:
Remove "exact match" and deprecate "Gene Ontology ID" claims.
Change "instance of"-->"F/C/P obsoleted in GO"
Remove any GO: alias
If replaced_by exists as item, add P1366.
Use with wd ee.

Further processing (removing stmts, merging) should be done manually.
Effectively, replaced entities should be merged, others should have
all links removed that point to them (see rm-ann-to-obs-go.py)
"""

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--preview", help="",
        action="store_true")
parser.add_argument("-q", "--query", help="perform SPARQL query",
        action="store_true")
parser.add_argument("-Q", "--query1", help="perform SPARQL query",
        action="store_true")

# Read arguments from the command line
args = parser.parse_args()

# Check for --version or -V
dontquery = not args.query
script = os.path.basename(sys.argv[0])[:-3]
GORELEASE = "Q112968510"
REASON = "P2241"
DEPRECATED = "Q67125514"

if dontquery is False:
    print('performing query...', file=sys.stderr)
    ret = os.popen('wd sparql {}.rq >{}.json'.format(script, script))
    if ret.close() is not None:
        raise
with open('{}.json'.format(script)) as file:
    s = file.read()
    jol = json.loads(s)
    print('read {} records'.format(len(jol)), flush=True, file=sys.stderr)

goids = {}
items = []
for d in jol:
    goid = d.get('goid')
    gorank = d.get('rank')
    if gorank == 'http://wikiba.se/ontology#DeprecatedRank':
        continue
    gostmt = d.get('gostmt')
    exm = d.get('exm')
    if exm is not None and exm.startswith('http://purl.obolibrary.org/obo/GO_'):
        exstmt = d.get('exstmt')
    else:
        exstmt = None
    it = d.get('item')
    git = goids.get(goid)
    if git is None:
        goids[goid] = (it,gostmt,exm,exstmt)
        
        items.append(it)
    else:
        if exstmt is not None:
            goids[goid] = (it,gostmt,exm,exstmt)

print('reading GO', file=sys.stderr)
ont = pronto.Ontology('go-plus.owl')
check = True
obids = []
obitems = []
for goid in goids.keys():
    term = ont.get(goid)
    if term is not None and term.obsolete is False:
        continue
    obids.append(goid)
    obitems.append(goids.get(goid)[0])
    if args.preview:
        print("{} {} {}".format(goid, term.name, goids.get(goid)[0]))
        continue

als = {}
if args.query1:
    itstr = " ".join(list(map(str, obitems)))
    print('Fetching aliases for {} items'.format(len(obitems)), flush=True, file=sys.stderr)
    ret = os.popen('echo {}| wd data --simplify --props aliases >t.json'.format(itstr))
    print(ret.read())
    if ret.close() is not None:
        print('ERROR')
with open('t.json'.format(script)) as file:
    lines = file.readlines()
    for s in lines:
        jol = json.loads(s)
        it = jol.get('id')
        als[it] = jol.get('aliases')

ndate = datetime.date.today().isoformat()
newd = ndate + 'T00:00:00Z'
for goid in obids:
    it,gostmt,exm,exstmt = goids.get(goid)
    aldir = als.get(it)
    ald = {}
    if aldir is not None:
        for lang,allist in aldir.items():
            for al in allist:
                if al.startswith('GO:'):
                    ald[lang] = { "value":al, "remove":True }
    claims = {
            "P31": [ { "value": "Q93740491",
                        "references": { "P248": GORELEASE,
                            "P813": ndate }}],
            "P686": [{"id":gostmt,
                        "value": goid,
                        "rank": "deprecated", 
                        "qualifiers": { REASON: DEPRECATED }}],
            }
    term = ont.get(goid)
    if term.replaced_by is not None:
        P1366 = []
        for t in term.replaced_by:
            if goids.get(t.id) is not None:
                P1366.append( { "value": goids.get(t.id)[0],
                                "references": { "P248": GORELEASE,
                                    "P813": ndate }} )
        if len(P1366) > 0:
            claims["P1366"] = P1366
    j = {"id": it,
        "claims": claims }
#        if repl_id is not None:
#            j.get('claims')['P1366'] = { "value": goids.get(repl_id)[0],
#                                    "references": { "P248": "Q93741199",
#                                       "P813": ndate }}
    if exstmt is not None:
        j.get('claims')['P2888'] = [{"id":exstmt, "remove":True}]
    if len(ald) > 0:
        j['aliases'] = ald
#    f = open('t.json', 'w')
#    f.write(json.dumps(j))
#    f.close()
    print(json.dumps(j), flush=True)
#        ret = os.popen('wd ee t.json --summary obsolete-gos')
#        print(ret.read())
#        if ret.close() is not None:
#            print('ERROR')
